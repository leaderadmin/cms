from django.urls import include, path
from .modules.auth import urls as auth_urls
from .modules.dashboard import urls as dashboard_urls
from .modules.audit import urls as audit_urls
from .modules.settings import urls as settings_urls
from .modules.entities import urls as entity_urls
from .modules.media import urls as media_urls
from .modules.articles import urls as article_urls
from .modules.pages import urls as page_urls
from .modules.products import urls as product_urls
from .modules.recruitment import urls as recruitment_urls
from .modules.faq import urls as faq_urls
from .modules.dealers import urls as dealer_urls

urlpatterns = [
	path("auth/", include(auth_urls.urlpatterns)),
	path("", include(dashboard_urls.urlpatterns)),
	path("audit/", include(audit_urls.urlpatterns)),
	path("settings/", include(settings_urls.urlpatterns)),
	path("entities/", include(entity_urls.urlpatterns)),
	path("media/", include(media_urls.urlpatterns)),
	path("articles/", include(article_urls.urlpatterns)),
	path("pages/", include(page_urls.urlpatterns)),
	path("products/", include(product_urls.urlpatterns)),
	path("recruitment/", include(recruitment_urls.urlpatterns)),
	path("faq/", include(faq_urls.urlpatterns)),
	path("dealers/", include(dealer_urls.urlpatterns)),
]
