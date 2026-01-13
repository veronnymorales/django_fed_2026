from django.urls import path
from .views import (
    index_mc11_paquete_gestante,
    get_establecimientos_mc11_paquete_gestante_h,
    p_microredes_establec_mc11_paquete_gestante_h,
    p_establecimientos_mc11_paquete_gestante_h,
    get_redes_mc11_paquete_gestante,
    get_microredes_mc11_paquete_gestante,
    get_establecimientos_mc11_paquete_gestante,
    p_microredes_mc11_paquete_gestante,
    p_microredes_establec_mc11_paquete_gestante,
    p_establecimientos_mc11_paquete_gestante,
    RptPaqueteGestante,
    RptPaqueteGestanteMicroRed,
    RptPaqueteGestanteEstablec
)

urlpatterns = [
    
    path('mc11_paquete_gestante/', index_mc11_paquete_gestante, name='index_mc11_paquete_gestante'),

    ### BARRA HORIZONTAL - Filtros
    path('get_establecimientos_mc11_paquete_gestante_h/<int:establecimiento_id>/', get_establecimientos_mc11_paquete_gestante_h, name='get_establecimientos_mc11_paquete_gestante_h'),
    path('p_microredes_establec_mc11_paquete_gestante_h/', p_microredes_establec_mc11_paquete_gestante_h, name='p_microredes_establec_mc11_paquete_gestante_h'),
    path('p_establecimiento_mc11_paquete_gestante_h/', p_establecimientos_mc11_paquete_gestante_h, name='p_establecimientos_mc11_paquete_gestante_h'),
 # ========================================
    # SEGUIMIENTO NOMINAL - ÁMBITO SALUD
    # ========================================
    
    # REDES
    path('get_redes_mc11_paquete_gestante/<int:redes_id>/', 
         get_redes_mc11_paquete_gestante, 
         name='get_redes_mc11_paquete_gestante'),
    path('rpt_mc11_paquete_gestante_red_excel/', 
         RptPaqueteGestante.as_view(), 
         name='rpt_mc11_paquete_gestante_red_xls'),
    
    # MICROREDES
    path('get_microredes_mc11_paquete_gestante/<int:microredes_id>/', 
         get_microredes_mc11_paquete_gestante, 
         name='get_microredes_mc11_paquete_gestante'),
    path('p_microredes_mc11_paquete_gestante/', 
         p_microredes_mc11_paquete_gestante, 
         name='p_microredes_mc11_paquete_gestante'),
    path('rpt_mc11_paquete_gestante_microred_excel/', 
         RptPaqueteGestanteMicroRed.as_view(), 
         name='rpt_mc11_paquete_gestante_microred_xls'),
    
    # ESTABLECIMIENTOS
    path('get_establecimientos_mc11_paquete_gestante/<int:establecimiento_id>/', 
         get_establecimientos_mc11_paquete_gestante, 
         name='get_establecimientos_mc11_paquete_gestante'),
    path('p_microredes_establec_mc11_paquete_gestante/', 
         p_microredes_establec_mc11_paquete_gestante, 
         name='p_microredes_establec_mc11_paquete_gestante'),
    path('p_establecimientos_mc11_paquete_gestante/', 
         p_establecimientos_mc11_paquete_gestante, 
         name='p_establecimientos_mc11_paquete_gestante'),
    
    # REPORTE EXCEL
    path('rpt_mc11_paquete_gestante_establec_excel/', 
         RptPaqueteGestanteEstablec.as_view(), 
         name='rpt_mc11_paquete_gestante_establecimiento_xls'),
    
    
]