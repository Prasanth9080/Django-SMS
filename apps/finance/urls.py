from django.urls import path
from .views import download_invoice

from . import  views
from .views import (
    InvoiceCreateView,
    InvoiceDeleteView,
    InvoiceDetailView,
    InvoiceListView,
    InvoiceUpdateView,
    ReceiptCreateView,
    ReceiptUpdateView,
    bulk_invoice,


    # DownloadCSVViewdownloadcsv,
)


urlpatterns = [
    path("list/", InvoiceListView.as_view(), name="invoice-list"),
    path("create/", InvoiceCreateView.as_view(), name="invoice-create"),
    path("<int:pk>/detail/", InvoiceDetailView.as_view(), name="invoice-detail"),
    path("<int:pk>/update/", InvoiceUpdateView.as_view(), name="invoice-update"),
    path("<int:pk>/delete/", InvoiceDeleteView.as_view(), name="invoice-delete"),
    path("receipt/create", ReceiptCreateView.as_view(), name="receipt-create"),
    path(
        "receipt/<int:pk>/update/", ReceiptUpdateView.as_view(), name="receipt-update"
    ),
    path("bulk-invoice/", bulk_invoice, name="bulk-invoice"),



    # path("download-csv/", DownloadCSVViewdownloadcsv.as_view(), name="download-csv"),
    path('download-invoice/<int:invoice_id>/', download_invoice, name='download-invoice'),





    # path('student/<int:student_id>/', views.student_detail, name='student_detail'),

]

