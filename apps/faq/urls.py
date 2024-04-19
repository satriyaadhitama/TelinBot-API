from django.urls import path
from .views import FAQViewSet

faq_view_list = FAQViewSet.as_view(
    {
        "get": "list",  # GET request to /faq/ lists all records
        "post": "create",  # POST request to /faq/ creates a new record
    }
)

faq_view_detail = FAQViewSet.as_view(
    {
        "get": "retrieve",  # GET request to /faq/<pk>/ retrieves a specific record
        "put": "update",  # PUT request to /faq/<pk>/ updates a specific record
        "patch": "partial_update",  # PATCH request to /faq/<pk>/ partially updates a record
        "delete": "destroy",  # DELETE request to /faq/<pk>/ deletes a specific record
    }
)

urlpatterns = [
    path(
        "faq/",
        faq_view_list,
        name="faq-list",
    ),
    path(
        "faq/<int:pk>/",
        faq_view_detail,
        name="faq-detail",
    ),
]
