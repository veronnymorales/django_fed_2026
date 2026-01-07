from django.urls import path
from .views import (
    index_s32_adole_sin_anemia,
    get_establecimientos_s32_adole_sin_anemia_h,
    p_microredes_establec_s32_adole_sin_anemia_h,
    p_establecimientos_s32_adole_sin_anemia_h,
    get_redes_s32_adole_sin_anemia,
    get_microredes_s32_adole_sin_anemia,
    get_establecimientos_s32_adole_sin_anemia,
    p_microredes_s32_adole_sin_anemia,
    p_microredes_establec_s32_adole_sin_anemia,
    p_establecimientos_s32_adole_sin_anemia,
    RptAdoleSinAnemia,
    RptAdoleSinAnemiaMicroRed,
    RptAdoleSinAnemiaEstablec
)

urlpatterns = [
    
    path('s32_adole_sin_anemia/', index_s32_adole_sin_anemia, name='index_s32_adole_sin_anemia'),

    ### BARRA HORIZONTAL - Filtros
    path('get_establecimientos_s32_adole_sin_anemia_h/<int:establecimiento_id>/', get_establecimientos_s32_adole_sin_anemia_h, name='get_establecimientos_s32_adole_sin_anemia_h'),
    path('p_microredes_establec_s32_adole_sin_anemia_h/', p_microredes_establec_s32_adole_sin_anemia_h, name='p_microredes_establec_s32_adole_sin_anemia_h'),
    path('p_establecimiento_s32_adole_sin_anemia_h/', p_establecimientos_s32_adole_sin_anemia_h, name='p_establecimientos_s32_adole_sin_anemia_h'),
 # ========================================
    # SEGUIMIENTO NOMINAL - ÁMBITO SALUD
    # ========================================
    
    # REDES
    path('get_redes_s32_adole_sin_anemia/<int:redes_id>/', 
         get_redes_s32_adole_sin_anemia, 
         name='get_redes_s32_adole_sin_anemia'),
    path('rpt_s32_adole_sin_anemia_red_excel/', 
         RptAdoleSinAnemia.as_view(), 
         name='rpt_s32_adole_sin_anemia_red_xls'),
    
    # MICROREDES
    path('get_microredes_s32_adole_sin_anemia/<int:microredes_id>/', 
         get_microredes_s32_adole_sin_anemia, 
         name='get_microredes_s32_adole_sin_anemia'),
    path('p_microredes_s32_adole_sin_anemia/', 
         p_microredes_s32_adole_sin_anemia, 
         name='p_microredes_s32_adole_sin_anemia'),
    path('rpt_s32_adole_sin_anemia_microred_excel/', 
         RptAdoleSinAnemiaMicroRed.as_view(), 
         name='rpt_s32_adole_sin_anemia_microred_xls'),
    
    # ESTABLECIMIENTOS
    path('get_establecimientos_s32_adole_sin_anemia/<int:establecimiento_id>/', 
         get_establecimientos_s32_adole_sin_anemia, 
         name='get_establecimientos_s32_adole_sin_anemia'),
    path('p_microredes_establec_s32_adole_sin_anemia/', 
         p_microredes_establec_s32_adole_sin_anemia, 
         name='p_microredes_establec_s32_adole_sin_anemia'),
    path('p_establecimientos_s32_adole_sin_anemia/', 
         p_establecimientos_s32_adole_sin_anemia, 
         name='p_establecimientos_s32_adole_sin_anemia'),
    
    # REPORTE EXCEL
    path('rpt_s32_adole_sin_anemia_establec_excel/', 
         RptAdoleSinAnemiaEstablec.as_view(), 
         name='rpt_s32_adole_sin_anemia_establecimiento_xls'),
    
    
]