from django.urls import path
from . import views

urlpatterns = [
    path('', views.VenueListView.as_view(), name='venue-list'),
    path('<int:pk>/', views.VenueDetailView.as_view(), name='venue-detail'),
    path('create/', views.VenueCreateView.as_view(), name='venue-create'),
    path('<int:pk>/update/', views.VenueUpdateView.as_view(), name='venue-update'),
    path('categories/', views.venue_categories_view, name='venue-categories'),
    path('types/', views.venue_types_view, name='venue-types'),
    path('<int:pk>/pricing/', views.venue_pricing_view, name='venue-pricing'),
    path('<int:pk>/block/', views.block_venue_view, name='venue-block'),
]
