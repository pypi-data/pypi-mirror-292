from django.core.management.base import BaseCommand

from allianceauth.services.hooks import get_extension_logger

from metenox import tasks
from metenox.models import HoldingCorporation

logger = get_extension_logger(__name__)


class Command(BaseCommand):
    help = "Checks all metenox owners and update their Metenoxes"

    def handle(self, *args, **options):
        holding_corps = HoldingCorporation.objects.all()
        logger.info(f"Starting update for {len(holding_corps)} owner(s)")
        for holding in holding_corps:
            tasks.update_holding.delay(holding.corporation.corporation_id)
