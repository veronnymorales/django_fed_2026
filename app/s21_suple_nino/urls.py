from django.urls import path
from .views import (
    index_s21_suple_nino,
    get_establecimientos_s21_suple_nino_h,
    p_microredes_establec_s21_suple_nino_h,
    p_establecimientos_s21_suple_nino_h,
    get_redes_s21_suple_nino,
    get_microredes_s21_suple_nino,
    get_establecimientos_s21_suple_nino,
    p_microredes_s21_suple_nino,
    p_microredes_establec_s21_suple_nino,
    p_establecimientos_s21_suple_nino,
    RptSupleNino,
    RptSupleNinoMicroRed,
    RptSupleNinoEstablec
)

urlpatterns = [
    
    path('s21_suple_nino/', index_s21_suple_nino, name='index_s21_suple_nino'),

    ### BARRA HORIZONTAL - Filtros
    path('get_establecimientos_s21_suple_nino_h/<int:establecimiento_id>/', get_establecimientos_s21_suple_nino_h, name='get_establecimientos_s21_suple_nino_h'),
    path('p_microredes_establec_s21_suple_nino_h/', p_microredes_establec_s21_suple_nino_h, name='p_microredes_establec_s21_suple_nino_h'),
    path('p_establecimiento_s21_suple_nino_h/', p_establecimientos_s21_suple_nino_h, name='p_establecimientos_s21_suple_nino_h'),
 # ========================================
    # SEGUIMIENTO NOMINAL - ÁMBITO SALUD
    # ========================================
    
    # REDES
    path('get_redes_s21_suple_nino/<int:redes_id>/', 
         get_redes_s21_suple_nino, 
         name='get_redes_s21_suple_nino'),
    path('rpt_s21_suple_nino_red_excel/', 
         RptSupleNino.as_view(), 
         name='rpt_s21_suple_nino_red_xls'),
    
    # MICROREDES
    path('get_microredes_s21_suple_nino/<int:microredes_id>/', 
         get_microredes_s21_suple_nino, 
         name='get_microredes_s21_suple_nino'),
    path('p_microredes_s21_suple_nino/', 
         p_microredes_s21_suple_nino, 
         name='p_microredes_s21_suple_nino'),
    path('rpt_s21_suple_nino_microred_excel/', 
         RptSupleNinoMicroRed.as_view(), 
         name='rpt_s21_suple_nino_microred_xls'),
    
    # ESTABLECIMIENTOS
    path('get_establecimientos_s21_suple_nino/<int:establecimiento_id>/', 
         get_establecimientos_s21_suple_nino, 
         name='get_establecimientos_s21_suple_nino'),
    path('p_microredes_establec_s21_suple_nino/', 
         p_microredes_establec_s21_suple_nino, 
         name='p_microredes_establec_s21_suple_nino'),
    path('p_establecimientos_s21_suple_nino/', 
         p_establecimientos_s21_suple_nino, 
         name='p_establecimientos_s21_suple_nino'),
    
    # REPORTE EXCEL
    path('rpt_s21_suple_nino_establec_excel/', 
         RptSupleNinoEstablec.as_view(), 
         name='rpt_s21_suple_nino_establecimiento_xls'),
    
    
]