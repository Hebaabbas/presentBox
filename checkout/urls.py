from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .webhooks import webhook


urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('checkout_done/<order_number>', views.checkout_done, name='checkout_done'),
    path('wh/', webhook, name='webhook'),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
