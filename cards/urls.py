from django.urls import path
from .views import (
    CardListView, card_create, increase_card_quantity, decrease_card_quantity
)

app_name = 'cards'

urlpatterns = [
    path('', CardListView.as_view(), name='card_list'),
    path('new/', card_create, name='card_create'),
    path('<int:pk>/increase/', increase_card_quantity, name='increase_card_quantity'),
    path('<int:pk>/decrease/', decrease_card_quantity, name='decrease_card_quantity'),
]
