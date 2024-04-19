from django.urls import path
from .views import FinanceViewSet

finance_view_list = FinanceViewSet.as_view(
    {
        "get": "list",  # GET request to /finance/ lists all records
        "post": "create",  # POST request to /finance/ creates a new record
    }
)

finance_view_detail = FinanceViewSet.as_view(
    {
        "get": "retrieve",  # GET request to /finance/<pk>/ retrieves a specific record
        "put": "update",  # PUT request to /finance/<pk>/ updates a specific record
        "patch": "partial_update",  # PATCH request to /finance/<pk>/ partially updates a record
        "delete": "destroy",  # DELETE request to /finance/<pk>/ deletes a specific record
    }
)

urlpatterns = [
    path(
        "finance/",
        finance_view_list,
        name="finance-list",
    ),
    path(
        "finance/<int:pk>",
        finance_view_detail,
        name="finance-detail",
    ),
]
