from django.urls import path
from .views import (
    index_s12_anemia_gestante,
    get_establecimientos_s12_anemia_gestante_h,
    p_microredes_establec_s12_anemia_gestante_h,
    p_establecimientos_s12_anemia_gestante_h,
    get_redes_s12_anemia_gestante,
    get_microredes_s12_anemia_gestante,
    get_establecimientos_s12_anemia_gestante,
    p_microredes_s12_anemia_gestante,
    p_microredes_establec_s12_anemia_gestante,
    p_establecimientos_s12_anemia_gestante,
    RptCaptacionGestante,
    RptCaptacionGestanteMicroRed,
    RptCaptacionGestanteEstablec
)

urlpatterns = [
    
    path('s12_anemia_gestante/', index_s12_anemia_gestante, name='index_s12_anemia_gestante'),

    ### BARRA HORIZONTAL - Filtros
    path('get_establecimientos_s12_anemia_gestante_h/<int:establecimiento_id>/', get_establecimientos_s12_anemia_gestante_h, name='get_establecimientos_s12_anemia_gestante_h'),
    path('p_microredes_establec_s12_anemia_gestante_h/', p_microredes_establec_s12_anemia_gestante_h, name='p_microredes_establec_s12_anemia_gestante_h'),
    path('p_establecimiento_s12_anemia_gestante_h/', p_establecimientos_s12_anemia_gestante_h, name='p_establecimientos_s12_anemia_gestante_h'),
 # ========================================
    # SEGUIMIENTO NOMINAL - ÁMBITO SALUD
    # ========================================
    
    # REDES
    path('get_redes_s12_anemia_gestante/<int:redes_id>/', 
         get_redes_s12_anemia_gestante, 
         name='get_redes_s12_anemia_gestante'),
    path('rpt_s12_anemia_gestante_red_excel/', 
         RptCaptacionGestante.as_view(), 
         name='rpt_s12_anemia_gestante_red_xls'),
    
    # MICROREDES
    path('get_microredes_s12_anemia_gestante/<int:microredes_id>/', 
         get_microredes_s12_anemia_gestante, 
         name='get_microredes_s12_anemia_gestante'),
    path('p_microredes_s12_anemia_gestante/', 
         p_microredes_s12_anemia_gestante, 
         name='p_microredes_s12_anemia_gestante'),
    path('rpt_s12_anemia_gestante_microred_excel/', 
         RptCaptacionGestanteMicroRed.as_view(), 
         name='rpt_s12_anemia_gestante_microred_xls'),
    
    # ESTABLECIMIENTOS
    path('get_establecimientos_s12_anemia_gestante/<int:establecimiento_id>/', 
         get_establecimientos_s12_anemia_gestante, 
         name='get_establecimientos_s12_anemia_gestante'),
    path('p_microredes_establec_s12_anemia_gestante/', 
         p_microredes_establec_s12_anemia_gestante, 
         name='p_microredes_establec_s12_anemia_gestante'),
    path('p_establecimientos_s12_anemia_gestante/', 
         p_establecimientos_s12_anemia_gestante, 
         name='p_establecimientos_s12_anemia_gestante'),
    
    # REPORTE EXCEL
    path('rpt_s12_anemia_gestante_establec_excel/', 
         RptCaptacionGestanteEstablec.as_view(), 
         name='rpt_s12_anemia_gestante_establecimiento_xls'),
    
    
]