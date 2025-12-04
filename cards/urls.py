from django.urls import path
from .views import CardListView

app_name = 'cards'

urlpatterns = [
    path('', CardListView.as_view(), name='card_list'),
]
