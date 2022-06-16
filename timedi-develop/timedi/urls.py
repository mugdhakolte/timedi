"""
timedi URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from rest_framework_swagger.views import get_swagger_view

excluded_url = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('timedi_auth.urls')),
    path('api/v1/', include('api.urls')),
    path('api/v1/', include('patient.urls')),
    path('api/v1/', include('invoicing.urls')),
    path('api/v1/', include('history.urls')),
    path('api/v1/', include('production.urls')),
    path('api/v1/', include('planning.urls')),
    path('api/v1/', include('history.urls')),
    path('api/v1/', include('hospital.urls')),
    path('api/v1/', include('therapeutic_booklets.urls')),
    path('api/v1/', include('pharmacist_control.urls')),
]

urlpatterns = excluded_url + [
    path(
        'api-docs/', get_swagger_view(
            title='Timedi API',
            patterns=excluded_url,
        ),
    ),
]
