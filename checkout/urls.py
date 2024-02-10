from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.checkout, name='checkout')
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
