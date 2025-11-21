import django_filters
from .models import MAESTRO_HIS_ESTABLECIMIENTO

class EstablecimientoFilter(django_filters.FilterSet):
    provincia = django_filters.CharFilter(field_name="Provincia", lookup_expr='icontains')
    distrito = django_filters.CharFilter(field_name="Distrito", lookup_expr='icontains')

    class Meta:
        model = MAESTRO_HIS_ESTABLECIMIENTO
        fields = ['Provincia', 'Distrito']