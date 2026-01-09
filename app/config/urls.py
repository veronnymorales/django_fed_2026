from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('base.urls')),
    path('', include('s11_captacion_gestante.urls')),
    path('', include('s12_anemia_gestante.urls')),
    path('', include('s13_suple_gestante.urls')),
    path('', include('s21_suple_nino.urls')),
    path('', include('s22_sin_anemia_nino.urls')),
    path('', include('s23_12m_anemia_nino.urls')),
    path('', include('s24_12m_sin_anemia_nino.urls')),
    path('', include('sv11_adole_dosaje.urls')),
    path('', include('s32_adole_paquete.urls')),
    path('', include('v11_tamizaje_gestante.urls')),    
    path('', include('v12_paquete_terapeutico.urls')),
    # path('', include('discapacidad.padron_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)