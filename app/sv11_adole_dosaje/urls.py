from django.urls import path
from .views import (
    index_sv11_adole_dosaje,
    get_establecimientos_sv11_adole_dosaje_h,
    p_microredes_establec_sv11_adole_dosaje_h,
    p_establecimientos_sv11_adole_dosaje_h,
    get_redes_sv11_adole_dosaje,
    get_microredes_sv11_adole_dosaje,
    get_establecimientos_sv11_adole_dosaje,
    p_microredes_sv11_adole_dosaje,
    p_microredes_establec_sv11_adole_dosaje,
    p_establecimientos_sv11_adole_dosaje,
    RptAdoleDosaje,
    RptAdoleDosajeMicroRed,
    RptAdoleDosajeEstablec
)

urlpatterns = [
    
    path('sv11_adole_dosaje/', index_sv11_adole_dosaje, name='index_sv11_adole_dosaje'),

    ### BARRA HORIZONTAL - Filtros
    path('get_establecimientos_sv11_adole_dosaje_h/<int:establecimiento_id>/', get_establecimientos_sv11_adole_dosaje_h, name='get_establecimientos_sv11_adole_dosaje_h'),
    path('p_microredes_establec_sv11_adole_dosaje_h/', p_microredes_establec_sv11_adole_dosaje_h, name='p_microredes_establec_sv11_adole_dosaje_h'),
    path('p_establecimiento_sv11_adole_dosaje_h/', p_establecimientos_sv11_adole_dosaje_h, name='p_establecimientos_sv11_adole_dosaje_h'),
 # ========================================
    # SEGUIMIENTO NOMINAL - ÁMBITO SALUD
    # ========================================
    
    # REDES
    path('get_redes_sv11_adole_dosaje/<int:redes_id>/', 
         get_redes_sv11_adole_dosaje, 
         name='get_redes_sv11_adole_dosaje'),
    path('rpt_sv11_adole_dosaje_red_excel/', 
         RptAdoleDosaje.as_view(), 
         name='rpt_sv11_adole_dosaje_red_xls'),
    
    # MICROREDES
    path('get_microredes_sv11_adole_dosaje/<int:microredes_id>/', 
         get_microredes_sv11_adole_dosaje, 
         name='get_microredes_sv11_adole_dosaje'),
    path('p_microredes_sv11_adole_dosaje/', 
         p_microredes_sv11_adole_dosaje, 
         name='p_microredes_sv11_adole_dosaje'),
    path('rpt_sv11_adole_dosaje_microred_excel/', 
         RptAdoleDosajeMicroRed.as_view(), 
         name='rpt_sv11_adole_dosaje_microred_xls'),
    
    # ESTABLECIMIENTOS
    path('get_establecimientos_sv11_adole_dosaje/<int:establecimiento_id>/', 
         get_establecimientos_sv11_adole_dosaje, 
         name='get_establecimientos_sv11_adole_dosaje'),
    path('p_microredes_establec_sv11_adole_dosaje/', 
         p_microredes_establec_sv11_adole_dosaje, 
         name='p_microredes_establec_sv11_adole_dosaje'),
    path('p_establecimientos_sv11_adole_dosaje/', 
         p_establecimientos_sv11_adole_dosaje, 
         name='p_establecimientos_sv11_adole_dosaje'),
    
    # REPORTE EXCEL
    path('rpt_sv11_adole_dosaje_establec_excel/', 
         RptAdoleDosajeEstablec.as_view(), 
         name='rpt_sv11_adole_dosaje_establecimiento_xls'),
    
    
]