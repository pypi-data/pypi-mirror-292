"""
Modules containing all ESI interactions
"""

from typing import Dict, List, Optional

from esi.clients import EsiClientProvider
from esi.errors import TokenError

from metenox.models import HoldingCorporation

from . import __version__

METENOX_TYPE_ID = 81826


esi = EsiClientProvider(app_info_text=f"aa-metenox v{__version__}")


def get_metenox_from_esi(
    holding_corporation: HoldingCorporation,
) -> Optional[List[Dict]]:
    """Returns all metenoxes associated with a given Owner"""

    structures = get_structures_from_esi(holding_corporation)

    return (
        [
            structure
            for structure in structures
            if structure["type_id"] == METENOX_TYPE_ID
        ]
        if structures
        else None
    )


def get_structure_info_from_esi(
    holding_corporation: HoldingCorporation, structure_id: int
) -> Dict:
    """Returns the location information of a structure"""

    for owner in holding_corporation.owners.all():

        structure_info = esi.client.Universe.get_universe_structures_structure_id(
            structure_id=structure_id,
            token=owner.fetch_token().valid_access_token(),
        ).result()

        return structure_info


def get_structures_from_esi(
    holding_corporation: HoldingCorporation,
) -> Optional[List[Dict]]:
    """Returns all structures associated with a given owner"""

    for owner in holding_corporation.owners.all():
        try:
            return esi.client.Corporation.get_corporations_corporation_id_structures(
                corporation_id=owner.corporation.corporation.corporation_id,
                token=owner.fetch_token().valid_access_token(),
            ).results()
        except TokenError:  # tries the next owner
            continue

    return None  # No owner worked
