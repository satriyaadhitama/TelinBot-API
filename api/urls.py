from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

apps_name = ["user_auth", "services", "finance", "faq", "chatbot"]

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("admin/", admin.site.urls),  # /admin
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

for app_name in apps_name:
    urlpatterns.append(path("api/", include(f"apps.{app_name}.urls")))
