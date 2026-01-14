from django.urls import path
from .views import (
    index_mc21_paquete_nino,
    get_establecimientos_mc21_paquete_nino_h,
    p_microredes_establec_mc21_paquete_nino_h,
    p_establecimientos_mc21_paquete_nino_h,
    get_redes_mc21_paquete_nino,
    get_microredes_mc21_paquete_nino,
    get_establecimientos_mc21_paquete_nino,
    p_microredes_mc21_paquete_nino,
    p_microredes_establec_mc21_paquete_nino,
    p_establecimientos_mc21_paquete_nino,
    RptPaqueteNino,
    RptPaqueteNinoMicroRed,
    RptPaqueteNinoEstablec
)

urlpatterns = [
    
    path('mc21_paquete_nino/', index_mc21_paquete_nino, name='index_mc21_paquete_nino'),

    ### BARRA HORIZONTAL - Filtros
    path('get_establecimientos_mc21_paquete_nino_h/<int:establecimiento_id>/', get_establecimientos_mc21_paquete_nino_h, name='get_establecimientos_mc21_paquete_nino_h'),
    path('p_microredes_establec_mc21_paquete_nino_h/', p_microredes_establec_mc21_paquete_nino_h, name='p_microredes_establec_mc21_paquete_nino_h'),
    path('p_establecimiento_mc21_paquete_nino_h/', p_establecimientos_mc21_paquete_nino_h, name='p_establecimientos_mc21_paquete_nino_h'),
 # ========================================
    # SEGUIMIENTO NOMINAL - ÁMBITO SALUD
    # ========================================
    
    # REDES
    path('get_redes_mc21_paquete_nino/<int:redes_id>/', 
         get_redes_mc21_paquete_nino, 
         name='get_redes_mc21_paquete_nino'),
    path('rpt_mc21_paquete_nino_red_excel/', 
         RptPaqueteNino.as_view(), 
         name='rpt_mc21_paquete_nino_red_xls'),
    
    # MICROREDES
    path('get_microredes_mc21_paquete_nino/<int:microredes_id>/', 
         get_microredes_mc21_paquete_nino, 
         name='get_microredes_mc21_paquete_nino'),
    path('p_microredes_mc21_paquete_nino/', 
         p_microredes_mc21_paquete_nino, 
         name='p_microredes_mc21_paquete_nino'),
    path('rpt_mc21_paquete_nino_microred_excel/', 
         RptPaqueteNinoMicroRed.as_view(), 
         name='rpt_mc21_paquete_nino_microred_xls'),
    
    # ESTABLECIMIENTOS
    path('get_establecimientos_mc21_paquete_nino/<int:establecimiento_id>/', 
         get_establecimientos_mc21_paquete_nino, 
         name='get_establecimientos_mc21_paquete_nino'),
    path('p_microredes_establec_mc21_paquete_nino/', 
         p_microredes_establec_mc21_paquete_nino, 
         name='p_microredes_establec_mc21_paquete_nino'),
    path('p_establecimientos_mc21_paquete_nino/', 
         p_establecimientos_mc21_paquete_nino, 
         name='p_establecimientos_mc21_paquete_nino'),
    
    # REPORTE EXCEL
    path('rpt_mc21_paquete_nino_establec_excel/', 
         RptPaqueteNinoEstablec.as_view(), 
         name='rpt_mc21_paquete_nino_establecimiento_xls'),
    
    
]