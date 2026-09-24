from django.urls import path
from .views import DealerDetailView, DealerListView
urlpatterns = [path("", DealerListView.as_view()), path("<int:dealer_id>/", DealerDetailView.as_view())]