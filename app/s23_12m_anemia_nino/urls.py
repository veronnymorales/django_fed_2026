from django.urls import path
from .views import (
    index_s23_12m_anemia_nino,
    get_establecimientos_s23_12m_anemia_nino_h,
    p_microredes_establec_s23_12m_anemia_nino_h,
    p_establecimientos_s23_12m_anemia_nino_h,
    get_redes_s23_12m_anemia_nino,
    get_microredes_s23_12m_anemia_nino,
    get_establecimientos_s23_12m_anemia_nino,
    p_microredes_s23_12m_anemia_nino,
    p_microredes_establec_s23_12m_anemia_nino,
    p_establecimientos_s23_12m_anemia_nino,
    Rpt12mAnemiaNino,
    Rpt12mAnemiaNinoMicroRed,
    Rpt12mAnemiaNinoEstablec
)

urlpatterns = [
    
    path('s23_12m_anemia_nino/', index_s23_12m_anemia_nino, name='index_s23_12m_anemia_nino'),

    ### BARRA HORIZONTAL - Filtros
    path('get_establecimientos_s23_12m_anemia_nino_h/<int:establecimiento_id>/', get_establecimientos_s23_12m_anemia_nino_h, name='get_establecimientos_s23_12m_anemia_nino_h'),
    path('p_microredes_establec_s23_12m_anemia_nino_h/', p_microredes_establec_s23_12m_anemia_nino_h, name='p_microredes_establec_s23_12m_anemia_nino_h'),
    path('p_establecimiento_s23_12m_anemia_nino_h/', p_establecimientos_s23_12m_anemia_nino_h, name='p_establecimientos_s23_12m_anemia_nino_h'),
 # ========================================
    # SEGUIMIENTO NOMINAL - ÁMBITO SALUD
    # ========================================
    
    # REDES
    path('get_redes_s23_12m_anemia_nino/<int:redes_id>/', 
         get_redes_s23_12m_anemia_nino, 
         name='get_redes_s23_12m_anemia_nino'),
    path('rpt_s23_12m_anemia_nino_red_excel/', 
         Rpt12mAnemiaNino.as_view(), 
         name='rpt_s23_12m_anemia_nino_red_xls'),
    
    # MICROREDES
    path('get_microredes_s23_12m_anemia_nino/<int:microredes_id>/', 
         get_microredes_s23_12m_anemia_nino, 
         name='get_microredes_s23_12m_anemia_nino'),
    path('p_microredes_s23_12m_anemia_nino/', 
         p_microredes_s23_12m_anemia_nino, 
         name='p_microredes_s23_12m_anemia_nino'),
    path('rpt_s23_12m_anemia_nino_microred_excel/', 
         Rpt12mAnemiaNinoMicroRed.as_view(), 
         name='rpt_s23_12m_anemia_nino_microred_xls'),
    
    # ESTABLECIMIENTOS
    path('get_establecimientos_s23_12m_anemia_nino/<int:establecimiento_id>/', 
         get_establecimientos_s23_12m_anemia_nino, 
         name='get_establecimientos_s23_12m_anemia_nino'),
    path('p_microredes_establec_s23_12m_anemia_nino/', 
         p_microredes_establec_s23_12m_anemia_nino, 
         name='p_microredes_establec_s23_12m_anemia_nino'),
    path('p_establecimientos_s23_12m_anemia_nino/', 
         p_establecimientos_s23_12m_anemia_nino, 
         name='p_establecimientos_s23_12m_anemia_nino'),
    
    # REPORTE EXCEL
    path('rpt_s23_12m_anemia_nino_establec_excel/', 
         Rpt12mAnemiaNinoEstablec.as_view(), 
         name='rpt_s23_12m_anemia_nino_establecimiento_xls'),
    
    
]