"""Tasks."""

from celery import shared_task
from moonmining.constants import EveTypeId
from moonmining.models.moons import Moon as MoonminingMoon

from eveuniverse.constants import EveGroupId
from eveuniverse.models import EveSolarSystem

from allianceauth.services.hooks import get_extension_logger

from metenox.api.fuzzwork import get_type_ids_prices
from metenox.esi import get_metenox_from_esi, get_structure_info_from_esi
from metenox.models import (
    HoldingCorporation,
    Metenox,
    MetenoxHourlyProducts,
    Moon,
    MoonGooPrice,
)
from metenox.moons import get_metenox_hourly_harvest

logger = get_extension_logger(__name__)


class TaskError(Exception):
    """To be raised when a task fails"""


@shared_task
def update_holding(holding_corp_id: int):
    """
    Updated the list of metenoxes under a specific owner
    If harvest is set to True the harvest components are also recalculated
    """

    logger.info("Updating corporation id %s", holding_corp_id)

    holding_corp = HoldingCorporation.objects.get(
        corporation__corporation_id=holding_corp_id
    )

    metenoxes_info = get_metenox_from_esi(holding_corp)
    if not metenoxes_info:
        logger.warning("Failed to fetch the metenoxes for corporation %s", holding_corp)
        raise TaskError

    metenoxes_info_dic = {
        metenox["structure_id"]: metenox for metenox in metenoxes_info
    }

    metenoxes_ids = set(metenox["structure_id"] for metenox in metenoxes_info)
    current_metenoxes_ids = set(
        metenox.structure_id for metenox in Metenox.objects.all()
    )

    for metenox_id in metenoxes_ids - current_metenoxes_ids:
        location_info = get_structure_info_from_esi(holding_corp, metenox_id)
        create_metenox.delay(
            holding_corp.corporation.corporation_id,
            metenoxes_info_dic[metenox_id],
            location_info,
        )

    # TODO update existing metenoxes


@shared_task
def create_metenox(
    holding_corporation_id: int, structure_info: dict, location_info: dict
):
    """
    Creates and adds the Metenox in the database
    """
    holding_corporation = HoldingCorporation.objects.get(
        corporation__corporation_id=holding_corporation_id
    )
    logger.info(
        "Creating metenox %s for %s",
        structure_info["structure_id"],
        holding_corporation,
    )
    solar_system, _ = EveSolarSystem.objects.get_or_create_esi(
        id=location_info["solar_system_id"]
    )
    try:
        nearest_celestial = solar_system.nearest_celestial(
            x=location_info["position"]["x"],
            y=location_info["position"]["y"],
            z=location_info["position"]["z"],
            group_id=EveGroupId.MOON,
        )
    except OSError as exc:
        logger.exception("%s: Failed to fetch nearest celestial", structure_info)
        raise exc

    if not nearest_celestial or nearest_celestial.eve_type.id != EveTypeId.MOON:
        logger.exception(
            "Couldn't find the moon corresponding to metenox %s", structure_info
        )
        raise TaskError

    eve_moon = nearest_celestial.eve_object
    moon, _ = Moon.objects.get_or_create(eve_moon=eve_moon)

    metenox = Metenox(
        moon=moon,
        structure_name=structure_info["name"],
        structure_id=structure_info["structure_id"],
        corporation=holding_corporation,
    )
    metenox.save()


@shared_task
def update_moon(moon_id: int):
    """
    Update the materials and price of a Moon
    """
    logger.info("Updating information of metenox id %s", moon_id)

    moon = Moon.objects.get(eve_moon_id=moon_id)

    harvest = get_metenox_hourly_harvest(moon_id)

    MetenoxHourlyProducts.objects.bulk_create(
        [
            MetenoxHourlyProducts(moon=moon, product=goo_type, amount=amount)
            for goo_type, amount in harvest.items()
        ],
        update_conflicts=True,
        unique_fields=["moon", "product"],
        update_fields=["amount"],
    )


@shared_task
def update_moons_from_moonmining(*, no_delay=False):
    """
    Will fetch all the moons from aa-moonmining application and update the metenox database

    no_delay is a param for testing purpose to disable task delaying and make sure everything is synchronous
    """

    logger.info("Updating all moons from moonming")

    metenox_moons = Moon.objects.all()
    metenox_moon_ids = [moon.eve_moon.id for moon in metenox_moons]
    missing_moons = MoonminingMoon.objects.exclude(eve_moon__id__in=metenox_moon_ids)

    for moon in missing_moons:
        if no_delay:
            create_moon_from_moonmining(moon.eve_moon.id)
        else:
            create_moon_from_moonmining.delay(moon.eve_moon.id)

    moons_to_update = [moon for moon in metenox_moons if len(moon.hourly_pull) == 0]
    for moon in moons_to_update:
        if no_delay:
            update_moon(moon.eve_moon.id)
        else:
            update_moon.delay(moon.eve_moon.id)


@shared_task
def create_moon_from_moonmining(moon_id: int):
    """
    Fetches a moon from moonmining. Creates it for metenox and fetches materials
    """

    logger.info("Updating materials of moon id %s", moon_id)

    Moon.objects.get_or_create(
        eve_moon_id=moon_id,
        moonmining_moon=MoonminingMoon.objects.get(eve_moon_id=moon_id),
    )

    update_moon(moon_id)


@shared_task
def update_moon_prices():
    """Task fetching the current moon goo prices updating all moon values"""

    goo_ids = list(MetenoxHourlyProducts.all_moon_goo_ids())

    goo_prices = get_type_ids_prices(goo_ids)

    for type_id, price in goo_prices.items():
        goo_price, _ = MoonGooPrice.objects.get_or_create(
            moon_goo_id=type_id,
        )
        goo_price.update_price(price)

    moons = Moon.objects.all()
    logger.info(
        "Successfully updating material prices. Now updating %s moons", moons.count()
    )

    for moon in moons:
        moon.update_price()
