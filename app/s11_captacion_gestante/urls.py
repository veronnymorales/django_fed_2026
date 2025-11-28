from django.urls import path
from .views import (
    index_s11_captacion_gestante,
    get_establecimientos_s11_captacion_gestante_h,
    p_microredes_establec_s11_captacion_gestante_h,
    p_establecimientos_s11_captacion_gestante_h,
    get_redes_s11_captacion_gestante,
    get_microredes_s11_captacion_gestante,
    get_establecimientos_s11_captacion_gestante,
    p_microredes_s11_captacion_gestante,
    p_microredes_establec_s11_captacion_gestante,
    p_establecimientos_s11_captacion_gestante,
    RptCaptacionGestante
)

urlpatterns = [
    
    path('s11_captacion_gestante/', index_s11_captacion_gestante, name='index_s11_captacion_gestante'),

    ### BARRA HORIZONTAL - Filtros
    path('get_establecimientos_s11_captacion_gestante_h/<int:establecimiento_id>/', get_establecimientos_s11_captacion_gestante_h, name='get_establecimientos_s11_captacion_gestante_h'),
    path('p_microredes_establec_s11_captacion_gestante_h/', p_microredes_establec_s11_captacion_gestante_h, name='p_microredes_establec_s11_captacion_gestante_h'),
    path('p_establecimiento_s11_captacion_gestante_h/', p_establecimientos_s11_captacion_gestante_h, name='p_establecimientos_s11_captacion_gestante_h'),
 # ========================================
    # SEGUIMIENTO NOMINAL - ÁMBITO SALUD
    # ========================================
    
    # REDES
    path('get_redes_s11_captacion_gestante/<int:redes_id>/', 
         get_redes_s11_captacion_gestante, 
         name='get_redes_s11_captacion_gestante'),
    path('rpt_s11_captacion_gestante_red_excel/', 
         RptCaptacionGestante.as_view(), 
         name='rpt_s11_captacion_gestante_red_xls'),
    
    # MICROREDES
    path('get_microredes_s11_captacion_gestante/<int:microredes_id>/', 
         get_microredes_s11_captacion_gestante, 
         name='get_microredes_s11_captacion_gestante'),
    path('p_microredes_s11_captacion_gestante/', 
         p_microredes_s11_captacion_gestante, 
         name='p_microredes_s11_captacion_gestante'),
    path('rpt_s11_captacion_gestante_microred_excel/', 
         RptCaptacionGestante.as_view(), 
         name='rpt_s11_captacion_gestante_microred_xls'),
    
    # ESTABLECIMIENTOS
    path('get_establecimientos_s11_captacion_gestante/<int:establecimiento_id>/', 
         get_establecimientos_s11_captacion_gestante, 
         name='get_establecimientos_s11_captacion_gestante'),
    path('p_microredes_establec_s11_captacion_gestante/', 
         p_microredes_establec_s11_captacion_gestante, 
         name='p_microredes_establec_s11_captacion_gestante'),
    path('p_establecimientos_s11_captacion_gestante/', 
         p_establecimientos_s11_captacion_gestante, 
         name='p_establecimientos_s11_captacion_gestante'),
    
    # REPORTE EXCEL
    path('rpt_s11_captacion_gestante_establec_excel/', 
         RptCaptacionGestante.as_view(), 
         name='rpt_s11_captacion_gestante_establecimiento_xls'),
    
    
]