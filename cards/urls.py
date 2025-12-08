from django.urls import path
from .views import (
    PokemonCardListView, TrainersCardListView, card_create, card_edit, increase_card_quantity,
    decrease_card_quantity, card_delete,
    toggle_view_mode, card_detail_modal
)

app_name = 'cards'

urlpatterns = [
    path('', PokemonCardListView.as_view(), name='pokemon_card_list'),
    path('trainers/', TrainersCardListView.as_view(), name='trainer_card_list'),
    path('new/<str:category_slug>/', card_create, name='card_create'),
    path('<int:pk>/edit/', card_edit, name='card_edit'),
    path('<int:pk>/increase/', increase_card_quantity, name='increase_card_quantity'),
    path('<int:pk>/decrease/', decrease_card_quantity, name='decrease_card_quantity'),
    path('<int:pk>/delete/', card_delete, name='card_delete'),
    path('<int:pk>/detail/', card_detail_modal, name='card_detail_modal'),
    path('toggle-view-mode/', toggle_view_mode, name='toggle_view_mode'),
]
