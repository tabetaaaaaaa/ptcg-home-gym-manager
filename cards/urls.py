from django.urls import path
from . import views

app_name = 'cards'

urlpatterns = [
    # Main Views
    path('', views.PokemonCardListView.as_view(), name='pokemon_card_list'),
    path('trainers/', views.TrainersCardListView.as_view(), name='trainer_card_list'),
    path('new/<str:category_slug>/', views.card_create, name='card_create'),
    
    # Card Actions
    path('<int:pk>/edit/', views.card_edit, name='card_edit'),
    path('<int:pk>/increase/', views.increase_card_quantity, name='increase_card_quantity'),
    path('<int:pk>/decrease/', views.decrease_card_quantity, name='decrease_card_quantity'),
    path('<int:pk>/delete/', views.card_delete, name='card_delete'),
    path('<int:pk>/detail/', views.card_detail_modal, name='card_detail_modal'),
    path('<int:pk>/related/', views.related_cards_modal, name='related_cards_modal'),
    path('toggle-view-mode/', views.toggle_view_mode, name='toggle_view_mode'),
    
    # Bulk Registration
    path('bulk/upload/', views.bulk_register_upload, name='bulk_register_upload'),
    path('bulk/analyze/', views.bulk_register_analyze, name='bulk_register_analyze'),
    path('bulk/item/<str:item_id>/edit/', views.bulk_register_edit_item, name='bulk_register_edit_item'),
    path('bulk/item/<str:item_id>/toggle-exclude/', views.bulk_register_toggle_exclude, name='bulk_register_toggle_exclude'),
    path('bulk/submit/', views.bulk_register_submit, name='bulk_register_submit'),
    path('search/name/', views.search_cards_by_name_modal, name='search_cards_by_name_modal'),
    path('export-csv-modal/', views.export_csv_modal, name='export_cards_csv_modal'),
    path('export-csv/', views.export_cards_csv, name='export_cards_csv'),
    path('import-csv/', views.import_cards_csv, name='import_cards_csv'),
]
