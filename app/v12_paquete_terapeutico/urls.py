from django.urls import path
from .views import (
    index_v12_paquete_terapeutico,
    get_establecimientos_v12_paquete_terapeutico_h,
    p_microredes_establec_v12_paquete_terapeutico_h,
    p_establecimientos_v12_paquete_terapeutico_h,
    get_redes_v12_paquete_terapeutico,
    get_microredes_v12_paquete_terapeutico,
    get_establecimientos_v12_paquete_terapeutico,
    p_microredes_v12_paquete_terapeutico,
    p_microredes_establec_v12_paquete_terapeutico,
    p_establecimientos_v12_paquete_terapeutico,
    RptPaqueteTerapeutico,
    RptPaqueteTerapeuticoMicroRed,
    RptPaqueteTerapeuticoEstablec
)

urlpatterns = [
    
    path('v12_paquete_terapeutico/', index_v12_paquete_terapeutico, name='index_v12_paquete_terapeutico'),

    ### BARRA HORIZONTAL - Filtros
    path('get_establecimientos_v12_paquete_terapeutico_h/<int:establecimiento_id>/', get_establecimientos_v12_paquete_terapeutico_h, name='get_establecimientos_v12_paquete_terapeutico_h'),
    path('p_microredes_establec_v12_paquete_terapeutico_h/', p_microredes_establec_v12_paquete_terapeutico_h, name='p_microredes_establec_v12_paquete_terapeutico_h'),
    path('p_establecimiento_v12_paquete_terapeutico_h/', p_establecimientos_v12_paquete_terapeutico_h, name='p_establecimientos_v12_paquete_terapeutico_h'),
 # ========================================
    # SEGUIMIENTO NOMINAL - ÁMBITO SALUD
    # ========================================
    
    # REDES
    path('get_redes_v12_paquete_terapeutico/<int:redes_id>/', 
         get_redes_v12_paquete_terapeutico, 
         name='get_redes_v12_paquete_terapeutico'),
    path('rpt_v12_paquete_terapeutico_red_excel/', 
         RptPaqueteTerapeutico.as_view(), 
         name='rpt_v12_paquete_terapeutico_red_xls'),
    
    # MICROREDES
    path('get_microredes_v12_paquete_terapeutico/<int:microredes_id>/', 
         get_microredes_v12_paquete_terapeutico, 
         name='get_microredes_v12_paquete_terapeutico'),
    path('p_microredes_v12_paquete_terapeutico/', 
         p_microredes_v12_paquete_terapeutico, 
         name='p_microredes_v12_paquete_terapeutico'),
    path('rpt_v12_paquete_terapeutico_microred_excel/', 
         RptPaqueteTerapeuticoMicroRed.as_view(), 
         name='rpt_v12_paquete_terapeutico_microred_xls'),
    
    # ESTABLECIMIENTOS
    path('get_establecimientos_v12_paquete_terapeutico/<int:establecimiento_id>/', 
         get_establecimientos_v12_paquete_terapeutico, 
         name='get_establecimientos_v12_paquete_terapeutico'),
    path('p_microredes_establec_v12_paquete_terapeutico/', 
         p_microredes_establec_v12_paquete_terapeutico, 
         name='p_microredes_establec_v12_paquete_terapeutico'),
    path('p_establecimientos_v12_paquete_terapeutico/', 
         p_establecimientos_v12_paquete_terapeutico, 
         name='p_establecimientos_v12_paquete_terapeutico'),
    
    # REPORTE EXCEL
    path('rpt_v12_paquete_terapeutico_establec_excel/', 
         RptPaqueteTerapeuticoEstablec.as_view(), 
         name='rpt_v12_paquete_terapeutico_establecimiento_xls'),
    
    
]