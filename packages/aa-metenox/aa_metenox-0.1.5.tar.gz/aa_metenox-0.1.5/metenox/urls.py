"""Routes."""

from django.urls import path

from . import views

app_name = "metenox"

urlpatterns = [
    path("", views.list_moons, name="index"),
    path("modal_loader_body", views.modal_loader_body, name="modal_loader_body"),
    path("add_owner", views.add_owner, name="add_owner"),
    path("corporations", views.corporations, name="corporations"),
    path("moon/<int:moon_pk>", views.moon_details, name="moon_details"),
    path("moons_data", views.MoonListJson.as_view(), name="moons_data"),
    path("moons_fdd_data", views.moons_fdd_data, name="moons_fdd_data"),
    path("prices", views.prices, name="prices"),
]
