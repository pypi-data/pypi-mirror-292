"""Helpers for views."""

from moonmining.models import Moon

from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from app_utils.views import BootstrapStyle


def moon_details_button_html(moon: Moon) -> str:
    """
    Return HTML to render a moon details button.

    Rewriting the function `fontawesome_modal_button_html` from app_utils
    """

    ajax_url = reverse("metenox:moon_details", args=[moon.pk])
    tooltip = "Moon details"

    return format_html(
        '<button type="button" '
        'class="btn btn-{}" '
        'data-bs-toggle="modal" '
        'data-bs-target="#{}" '
        "{}"
        "{}>"
        '<i class="{}"></i>'
        "</button>",
        BootstrapStyle(BootstrapStyle.DEFAULT),
        "modalMoonDetails",
        mark_safe(f'title="{tooltip}" ') if tooltip else "",
        mark_safe(f'data-ajax_url="{ajax_url}" ') if ajax_url else "",
        "fas fa-moon",
    )
