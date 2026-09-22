from django.urls import path

from .views import EmailConfigurationView, EmailTemplateDetailView, EmailTemplateListView, EmailTestView, SystemLogoView, SystemSettingsView

urlpatterns = [
    path("system/", SystemSettingsView.as_view()),
    path("system/logo/", SystemLogoView.as_view(), name="system-logo"),
    path("email/", EmailConfigurationView.as_view()),
    path("email/test/", EmailTestView.as_view()),
    path("email/templates/", EmailTemplateListView.as_view()),
    path("email/templates/<int:pk>/", EmailTemplateDetailView.as_view()),
]
