from django.urls import path
from .views import (
    index_v11_tamizaje_gestante,
    get_establecimientos_v11_tamizaje_gestante_h,
    p_microredes_establec_v11_tamizaje_gestante_h,
    p_establecimientos_v11_tamizaje_gestante_h,
    get_redes_v11_tamizaje_gestante,
    get_microredes_v11_tamizaje_gestante,
    get_establecimientos_v11_tamizaje_gestante,
    p_microredes_v11_tamizaje_gestante,
    p_microredes_establec_v11_tamizaje_gestante,
    p_establecimientos_v11_tamizaje_gestante,
    RptTamizajeGestante,
    RptTamizajeGestanteMicroRed,
    RptTamizajeGestanteEstablec
)

urlpatterns = [
    
    path('v11_tamizaje_gestante/', index_v11_tamizaje_gestante, name='index_v11_tamizaje_gestante'),

    ### BARRA HORIZONTAL - Filtros
    path('get_establecimientos_v11_tamizaje_gestante_h/<int:establecimiento_id>/', get_establecimientos_v11_tamizaje_gestante_h, name='get_establecimientos_v11_tamizaje_gestante_h'),
    path('p_microredes_establec_v11_tamizaje_gestante_h/', p_microredes_establec_v11_tamizaje_gestante_h, name='p_microredes_establec_v11_tamizaje_gestante_h'),
    path('p_establecimiento_v11_tamizaje_gestante_h/', p_establecimientos_v11_tamizaje_gestante_h, name='p_establecimientos_v11_tamizaje_gestante_h'),
 # ========================================
    # SEGUIMIENTO NOMINAL - ÁMBITO SALUD
    # ========================================
    
    # REDES
    path('get_redes_v11_tamizaje_gestante/<int:redes_id>/', 
         get_redes_v11_tamizaje_gestante, 
         name='get_redes_v11_tamizaje_gestante'),
    path('rpt_v11_tamizaje_gestante_red_excel/', 
         RptTamizajeGestante.as_view(), 
         name='rpt_v11_tamizaje_gestante_red_xls'),
    
    # MICROREDES
    path('get_microredes_v11_tamizaje_gestante/<int:microredes_id>/', 
         get_microredes_v11_tamizaje_gestante, 
         name='get_microredes_v11_tamizaje_gestante'),
    path('p_microredes_v11_tamizaje_gestante/', 
         p_microredes_v11_tamizaje_gestante, 
         name='p_microredes_v11_tamizaje_gestante'),
    path('rpt_v11_tamizaje_gestante_microred_excel/', 
         RptTamizajeGestanteMicroRed.as_view(), 
         name='rpt_v11_tamizaje_gestante_microred_xls'),
    
    # ESTABLECIMIENTOS
    path('get_establecimientos_v11_tamizaje_gestante/<int:establecimiento_id>/', 
         get_establecimientos_v11_tamizaje_gestante, 
         name='get_establecimientos_v11_tamizaje_gestante'),
    path('p_microredes_establec_v11_tamizaje_gestante/', 
         p_microredes_establec_v11_tamizaje_gestante, 
         name='p_microredes_establec_v11_tamizaje_gestante'),
    path('p_establecimientos_v11_tamizaje_gestante/', 
         p_establecimientos_v11_tamizaje_gestante, 
         name='p_establecimientos_v11_tamizaje_gestante'),
    
    # REPORTE EXCEL
    path('rpt_v11_tamizaje_gestante_establec_excel/', 
         RptTamizajeGestanteEstablec.as_view(), 
         name='rpt_v11_tamizaje_gestante_establecimiento_xls'),
    
    
]