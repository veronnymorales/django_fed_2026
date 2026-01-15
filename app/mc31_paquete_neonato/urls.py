from django.urls import path
from .views import (
    index_mc31_paquete_neonato,
    get_establecimientos_mc31_paquete_neonato_h,
    p_microredes_establec_mc31_paquete_neonato_h,
    p_establecimientos_mc31_paquete_neonato_h,
    get_redes_mc31_paquete_neonato,
    get_microredes_mc31_paquete_neonato,
    get_establecimientos_mc31_paquete_neonato,
    p_microredes_mc31_paquete_neonato,
    p_microredes_establec_mc31_paquete_neonato,
    p_establecimientos_mc31_paquete_neonato,
    RptPaqueteNino,
    RptPaqueteNinoMicroRed,
    RptPaqueteNinoEstablec
)

urlpatterns = [
    
    path('mc31_paquete_neonato/', index_mc31_paquete_neonato, name='index_mc31_paquete_neonato'),

    ### BARRA HORIZONTAL - Filtros
    path('get_establecimientos_mc31_paquete_neonato_h/<int:establecimiento_id>/', get_establecimientos_mc31_paquete_neonato_h, name='get_establecimientos_mc31_paquete_neonato_h'),
    path('p_microredes_establec_mc31_paquete_neonato_h/', p_microredes_establec_mc31_paquete_neonato_h, name='p_microredes_establec_mc31_paquete_neonato_h'),
    path('p_establecimiento_mc31_paquete_neonato_h/', p_establecimientos_mc31_paquete_neonato_h, name='p_establecimientos_mc31_paquete_neonato_h'),
 # ========================================
    # SEGUIMIENTO NOMINAL - ÁMBITO SALUD
    # ========================================
    
    # REDES
    path('get_redes_mc31_paquete_neonato/<int:redes_id>/', 
         get_redes_mc31_paquete_neonato, 
         name='get_redes_mc31_paquete_neonato'),
    path('rpt_mc31_paquete_neonato_red_excel/', 
         RptPaqueteNino.as_view(), 
         name='rpt_mc31_paquete_neonato_red_xls'),
    
    # MICROREDES
    path('get_microredes_mc31_paquete_neonato/<int:microredes_id>/', 
         get_microredes_mc31_paquete_neonato, 
         name='get_microredes_mc31_paquete_neonato'),
    path('p_microredes_mc31_paquete_neonato/', 
         p_microredes_mc31_paquete_neonato, 
         name='p_microredes_mc31_paquete_neonato'),
    path('rpt_mc31_paquete_neonato_microred_excel/', 
         RptPaqueteNinoMicroRed.as_view(), 
         name='rpt_mc31_paquete_neonato_microred_xls'),
    
    # ESTABLECIMIENTOS
    path('get_establecimientos_mc31_paquete_neonato/<int:establecimiento_id>/', 
         get_establecimientos_mc31_paquete_neonato, 
         name='get_establecimientos_mc31_paquete_neonato'),
    path('p_microredes_establec_mc31_paquete_neonato/', 
         p_microredes_establec_mc31_paquete_neonato, 
         name='p_microredes_establec_mc31_paquete_neonato'),
    path('p_establecimientos_mc31_paquete_neonato/', 
         p_establecimientos_mc31_paquete_neonato, 
         name='p_establecimientos_mc31_paquete_neonato'),
    
    # REPORTE EXCEL
    path('rpt_mc31_paquete_neonato_establec_excel/', 
         RptPaqueteNinoEstablec.as_view(), 
         name='rpt_mc31_paquete_neonato_establecimiento_xls'),
    
    
]