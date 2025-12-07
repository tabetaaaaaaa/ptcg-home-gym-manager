from django.urls import path
from .views import (
    CardListView, card_create, card_edit, increase_card_quantity,
    decrease_card_quantity, card_delete, card_name_suggestions,
    toggle_view_mode, card_detail_modal
)

app_name = 'cards'

urlpatterns = [
    path('', CardListView.as_view(), name='card_list'),
    path('new/', card_create, name='card_create'),
    path('<int:pk>/edit/', card_edit, name='card_edit'),
    path('<int:pk>/increase/', increase_card_quantity, name='increase_card_quantity'),
    path('<int:pk>/decrease/', decrease_card_quantity, name='decrease_card_quantity'),
    path('<int:pk>/delete/', card_delete, name='card_delete'),
    path('<int:pk>/detail/', card_detail_modal, name='card_detail_modal'),
    path('suggestions/', card_name_suggestions, name='card_name_suggestions'),
    path('toggle-view-mode/', toggle_view_mode, name='toggle_view_mode'),
]
