"""Corporation views"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render
from esi.decorators import token_required

from allianceauth.eveonline.models import EveCorporationInfo
from app_utils.allianceauth import notify_admins

from metenox import tasks
from metenox.app_settings import METENOX_ADMIN_NOTIFICATIONS_ENABLED
from metenox.models import ESI_SCOPES, HoldingCorporation, Owner
from metenox.views.general import add_common_context


@permission_required(["moonmining.basic_access"])
@token_required(scopes=ESI_SCOPES)
@login_required
def add_owner(request, token):
    """Render view to add an owner."""
    character_ownership = get_object_or_404(
        request.user.character_ownerships.select_related("character"),
        character__character_id=token.character_id,
    )
    corporation_id = character_ownership.character.corporation_id
    try:
        corporation = EveCorporationInfo.objects.get(corporation_id=corporation_id)
    except EveCorporationInfo.DoesNotExist:
        corporation = EveCorporationInfo.objects.create_corporation(
            corp_id=corporation_id
        )
        corporation.save()

    holding_corporation, _ = HoldingCorporation.objects.get_or_create(
        corporation=corporation,
    )

    owner, _ = Owner.objects.update_or_create(
        corporation=holding_corporation,
        defaults={"character_ownership": character_ownership},
    )

    # TODO figure out why I need to type all this to get the right corp id
    tasks.update_holding.delay(owner.corporation.corporation.corporation_id)
    messages.success(request, f"Update of refineries started for {owner}.")
    if METENOX_ADMIN_NOTIFICATIONS_ENABLED:
        notify_admins(
            message=f"{owner} was added as new owner by {request.user}.",
            title=f"Metenox: Owner added: {owner}",
        )
    return redirect("metenox:corporations")


@permission_required(["moonmining.basic_access"])
@login_required
def corporations(request):
    """
    Displays the corporations that the user is allowed to see and the metenoxes that they own
    """

    user_owners = Owner.get_owners_associated_to_user(request.user)
    holdings = [owner.corporation for owner in user_owners]

    metenoxes = {holding: list(holding.metenoxes.all()) for holding in holdings}

    return render(
        request,
        "metenox/corporations.html",
        add_common_context(
            {
                "holding_corporations": holdings,
                "metenoxes": metenoxes,
            }
        ),
    )
