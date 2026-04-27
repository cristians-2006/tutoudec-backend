"""
URLs raíz del proyecto Django.

- /admin/: panel de administración
- /api/: API REST (incluye auth, tutores, materias, tutorías)
- / y /api/schema/*: documentación OpenAPI (Swagger/ReDoc)
"""
from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),

    # Raíz: interfaz Swagger para explorar endpoints sin Postman.
    path('', SpectacularSwaggerView.as_view(url_name='schema')),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]