from django.urls import path
from .views import (
    index_dashboard,
    get_establecimientos_dashboard_h,
    p_microredes_establec_dashboard_h,
    p_establecimientos_dashboard_h,
    get_redes_dashboard,
    get_microredes_dashboard,
    get_establecimientos_dashboard,
    p_microredes_dashboard,
    p_microredes_establec_dashboard,
    p_establecimientos_dashboard,
    RptPaqueteGestante,
    RptPaqueteGestanteMicroRed,
    RptPaqueteGestanteEstablec
)

urlpatterns = [
    
    path('dashboard/', index_dashboard, name='index_dashboard'),

    ### BARRA HORIZONTAL - Filtros
    path('get_establecimientos_dashboard_h/<int:establecimiento_id>/', get_establecimientos_dashboard_h, name='get_establecimientos_dashboard_h'),
    path('p_microredes_establec_dashboard_h/', p_microredes_establec_dashboard_h, name='p_microredes_establec_dashboard_h'),
    path('p_establecimiento_dashboard_h/', p_establecimientos_dashboard_h, name='p_establecimientos_dashboard_h'),
 # ========================================
    # SEGUIMIENTO NOMINAL - ÁMBITO SALUD
    # ========================================
    
    # REDES
    path('get_redes_dashboard/<int:redes_id>/', 
         get_redes_dashboard, 
         name='get_redes_dashboard'),
    path('rpt_dashboard_red_excel/', 
         RptPaqueteGestante.as_view(), 
         name='rpt_dashboard_red_xls'),
    
    # MICROREDES
    path('get_microredes_dashboard/<int:microredes_id>/', 
         get_microredes_dashboard, 
         name='get_microredes_dashboard'),
    path('p_microredes_dashboard/', 
         p_microredes_dashboard, 
         name='p_microredes_dashboard'),
    path('rpt_dashboard_microred_excel/', 
         RptPaqueteGestanteMicroRed.as_view(), 
         name='rpt_dashboard_microred_xls'),
    
    # ESTABLECIMIENTOS
    path('get_establecimientos_dashboard/<int:establecimiento_id>/', 
         get_establecimientos_dashboard, 
         name='get_establecimientos_dashboard'),
    path('p_microredes_establec_dashboard/', 
         p_microredes_establec_dashboard, 
         name='p_microredes_establec_dashboard'),
    path('p_establecimientos_dashboard/', 
         p_establecimientos_dashboard, 
         name='p_establecimientos_dashboard'),
    
    # REPORTE EXCEL
    path('rpt_dashboard_establec_excel/', 
         RptPaqueteGestanteEstablec.as_view(), 
         name='rpt_dashboard_establecimiento_xls'),
    
    
]