from django.urls import path
from .views import (
    index_s11_captacion_gestante,
    get_establecimientos_s11_captacion_gestante_h,
    p_microredes_establec_s11_captacion_gestante_h,
    p_establecimientos_s11_captacion_gestante_h,
    p_distritos_s11_captacion_gestante_h,
)

urlpatterns = [
    
    path('s11_captacion_gestante/', index_s11_captacion_gestante, name='index_s11_captacion_gestante'),

    ### BARRA HORIZONTAL - Filtros
    path('get_establecimientos_s11_captacion_gestante_h/<int:establecimiento_id>/', get_establecimientos_s11_captacion_gestante_h, name='get_establecimientos_s11_captacion_gestante_h'),
    path('p_microredes_establec_s11_captacion_gestante_h/', p_microredes_establec_s11_captacion_gestante_h, name='p_microredes_establec_s11_captacion_gestante_h'),
    path('p_establecimiento_s11_captacion_gestante_h/', p_establecimientos_s11_captacion_gestante_h, name='p_establecimientos_s11_captacion_gestante_h'),
    path('p_distritos_s11_captacion_gestante_h/', p_distritos_s11_captacion_gestante_h, name='p_distritos_s11_captacion_gestante_h'),    
    

]