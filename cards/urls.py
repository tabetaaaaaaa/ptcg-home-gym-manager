from django.urls import path
from .views import CardListView, card_create

app_name = 'cards'

urlpatterns = [
    path('', CardListView.as_view(), name='card_list'),
    path('new/', card_create, name='card_create'),
]
