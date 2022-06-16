from rest_framework.routers import DefaultRouter

from invoicing.viewsets import *

router = DefaultRouter()

router.register('invoices', InvoiceListViewSet, basename='invoices')
router.register('invoice', InvoiceViewSet, basename='invoice')
router.register('invoice-medicine', InvoiceMedicineViewSet, basename='invoice_medicine')
router.register('invoice-action', HospitalPatientDetailViewSet, basename='invoice_action')
router.register('invoices-simulator', SimulatorDashboardViewSet, basename='invoices_simulator')
router.register('invoices-history', InvoiceStockMovementViewSet, basename='invoices_history')

urlpatterns = router.urls
