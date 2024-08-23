"""Models."""

from typing import Dict, Set

from moonmining.models import Moon as MoonminigMoon
from typing_extensions import Optional

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from esi.models import Token
from eveuniverse.models import EveMoon, EveType

from allianceauth.authentication.models import CharacterOwnership
from allianceauth.eveonline.models import EveCorporationInfo
from allianceauth.services.hooks import get_extension_logger

ESI_SCOPES = [
    "esi-universe.read_structures.v1",
    "esi-corporations.read_structures.v1",
]

logger = get_extension_logger(__name__)


class General(models.Model):
    """A meta model for app permissions."""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ("basic_access", "Can access this app"),
            ("auditor", "Can access metenox information about all corporations"),
        )


class HoldingCorporation(models.Model):
    """Corporation holding metenox moon drills"""

    corporation = models.OneToOneField(
        EveCorporationInfo, on_delete=models.CASCADE, primary_key=True
    )
    last_updated = models.DateTimeField(null=True, default=None)

    @property
    def alliance(self):
        """Returns holding corp's alliance"""
        return self.corporation.alliance

    def __str__(self) -> str:
        return self.corporation.__str__()


class Owner(models.Model):
    """Character in corporation owning metenoxes"""

    corporation = models.ForeignKey(
        HoldingCorporation,
        on_delete=models.CASCADE,
        related_name="owners",
    )

    character_ownership = models.ForeignKey(
        CharacterOwnership,
        on_delete=models.SET_DEFAULT,
        default=None,
        null=True,
        related_name="+",
        help_text="Character used to sync this corporation from ESI",
    )

    is_enabled = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Disabled corporations are excluded from the update process",
    )

    class Meta:
        verbose_name = "Owner"
        verbose_name_plural = "Owners"

    def __str__(self):
        return self.name

    @property
    def name(self) -> str:
        """Return name."""
        alliance_ticker_str = (
            f" [{self.corporation.alliance.alliance_ticker}]"
            if self.corporation.alliance
            else ""
        )
        return f"{self.corporation}{alliance_ticker_str} - {self.character_ownership.character}"

    @property
    def alliance_name(self) -> str:
        """Return alliance name."""
        return (
            self.corporation.alliance.alliance_name if self.corporation.alliance else ""
        )

    def fetch_token(self) -> Token:
        """Return valid token for this mining corp or raise exception on any error."""
        if not self.character_ownership:
            raise RuntimeError("This owner has no character configured.")
        token = (
            Token.objects.filter(
                character_id=self.character_ownership.character.character_id
            )
            .require_scopes(ESI_SCOPES)
            .require_valid()
            .first()
        )
        if not token:
            raise Token.DoesNotExist(f"{self}: No valid token found.")
        return token

    @classmethod
    def get_owners_associated_to_user(cls, user: User):
        """Returns all owners of the user"""
        return cls.objects.filter(character_ownership__user=user)


class Moon(models.Model):
    """Represents a moon and the metenox related values"""

    eve_moon = models.OneToOneField(
        EveMoon, on_delete=models.CASCADE, primary_key=True, related_name="+"
    )

    moonmining_moon = models.OneToOneField(
        MoonminigMoon,
        on_delete=models.CASCADE,
        related_name="+",
    )

    value = models.FloatField(default=0)
    value_updated_at = models.DateTimeField(null=True, default=None)

    @property
    def hourly_pull(self) -> Dict[EveType, int]:
        """Returns how much goo is harvested in an hour by a metenox"""
        hourly_products = MetenoxHourlyProducts.objects.filter(moon=self)
        return {product.product: product.amount for product in hourly_products}

    @property
    def name(self) -> str:
        """Returns name of this moon"""
        return self.moonmining_moon.name

    @property
    def rarity_class(self):
        """Returns rarity class of this moon"""
        return self.moonmining_moon.rarity_class

    def update_price(self):
        """Updates the Metenox price attribute to display"""
        hourly_harvest_value = sum(
            MoonGooPrice.find_goo_price(moon_goo) * moon_goo_amount
            for moon_goo, moon_goo_amount in self.hourly_pull.items()
        )
        self.value = hourly_harvest_value * 24 * 30
        self.value_updated_at = timezone.now()
        self.save()

    def __str__(self):
        return self.name


class Metenox(models.Model):
    """
    Represents a metenox anchored on a moon
    """

    structure_id = models.PositiveBigIntegerField(primary_key=True)
    structure_name = models.TextField(max_length=150)

    moon = models.OneToOneField(
        Moon,
        on_delete=models.CASCADE,
        related_name="metenox",
    )
    corporation = models.ForeignKey(
        HoldingCorporation, on_delete=models.CASCADE, related_name="metenoxes"
    )

    def __str__(self):
        return self.structure_name


class MetenoxHourlyProducts(models.Model):
    """
    Represents how much moon goo a Metenox harvests in an hour
    """

    moon = models.ForeignKey(Moon, on_delete=models.CASCADE, related_name="+")
    product = models.ForeignKey(EveType, on_delete=models.CASCADE, related_name="+")

    amount = models.IntegerField()

    def __str__(self):
        return f"{self.product.name} - {self.amount}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["moon", "product"], name="functional_pk_metenoxhourlyproduct"
            )
        ]

    @classmethod
    def all_moon_goo_ids(cls) -> Set[int]:
        """Returns all known moon goo ids in the database"""
        return set(cls.objects.values_list("product", flat=True).order_by("product_id"))


class MoonGooPrice(models.Model):
    """
    Represent a moon goo and its last fetched price
    """

    moon_goo = models.OneToOneField(EveType, on_delete=models.CASCADE, related_name="+")
    price = models.FloatField(default=0)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.moon_goo.name} - {self.price} ISK"

    def update_price(self, new_price: float):
        """Updates the price of an item"""
        self.price = new_price
        self.save()

    @classmethod
    def find_goo_price(cls, moon_goo: EveType) -> Optional[float]:
        """Returns the price of an item"""
        if goo_price := cls.objects.get(moon_goo=moon_goo):
            return goo_price.price
        return None
