"""
Utilidades reutilizables para consultas de establecimientos de salud.

Este módulo contiene funciones genéricas que pueden ser utilizadas
por diferentes apps del proyecto Django para obtener datos de
establecimientos, redes, provincias, microredes, etc.
"""

from typing import Dict, List, Optional, Any
from django.db.models import QuerySet, IntegerField
from django.db.models.functions import Cast, Substr

from base.models import MAESTRO_HIS_ESTABLECIMIENTO, DimPeriodo


# Constantes reutilizables
GOBIERNO_REGIONAL = 'GOBIERNO REGIONAL'
DISA_JUNIN = 'JUNIN'
DEFAULT_YEAR = '2024'


def get_redes(
    descripcion_sector: str = GOBIERNO_REGIONAL,
    disa: str = DISA_JUNIN,
    substr_length: int = 4
) -> QuerySet:
    """
    Obtiene las redes de salud filtradas por sector y DISA.
    
    Args:
        descripcion_sector: Descripción del sector (default: GOBIERNO_REGIONAL)
        disa: Código de la DISA (default: JUNIN)
        substr_length: Longitud del substring para el código de red (default: 4)
    
    Returns:
        QuerySet con Red y codigo_red_filtrado
    
    Example:
        >>> redes = get_redes()
        >>> redes = get_redes(descripcion_sector='ESSALUD', disa='LIMA')
    """
    return (
        MAESTRO_HIS_ESTABLECIMIENTO.objects
        .filter(Descripcion_Sector=descripcion_sector, Disa=disa)
        .annotate(codigo_red_filtrado=Substr('Codigo_Red', 1, substr_length))
        .values('Red', 'codigo_red_filtrado')
        .distinct()
        .order_by('Red')
    )


def get_provincias(
    descripcion_sector: str = GOBIERNO_REGIONAL,
    disa: Optional[str] = None,
    substr_length: int = 4
) -> QuerySet:
    """
    Obtiene las provincias filtradas por sector y opcionalmente por DISA.
    
    Args:
        descripcion_sector: Descripción del sector (default: GOBIERNO_REGIONAL)
        disa: Código de la DISA (opcional)
        substr_length: Longitud del substring para el ubigeo (default: 4)
    
    Returns:
        QuerySet con Provincia y ubigueo_filtrado
    
    Example:
        >>> provincias = get_provincias()
        >>> provincias = get_provincias(disa='JUNIN')
    """
    filtros = {'Descripcion_Sector': descripcion_sector}
    if disa:
        filtros['Disa'] = disa
    
    return (
        MAESTRO_HIS_ESTABLECIMIENTO.objects
        .filter(**filtros)
        .annotate(ubigueo_filtrado=Substr('Ubigueo_Establecimiento', 1, substr_length))
        .values('Provincia', 'ubigueo_filtrado')
        .distinct()
        .order_by('Provincia')
    )


def get_periodos_mes(anio: str = DEFAULT_YEAR) -> QuerySet:
    """
    Obtiene los meses disponibles para un año específico.
    
    Args:
        anio: Año para filtrar los periodos (default: 2024)
    
    Returns:
        QuerySet con Mes y nro_mes ordenados por número de mes
    
    Example:
        >>> meses = get_periodos_mes('2024')
        >>> meses = get_periodos_mes('2025')
    """
    return (
        DimPeriodo.objects
        .filter(Anio=anio)
        .annotate(nro_mes=Cast('NroMes', IntegerField()))
        .values('Mes', 'nro_mes')
        .order_by('NroMes')
        .distinct()
    )


def get_microredes(
    codigo_red: str,
    descripcion_sector: str = GOBIERNO_REGIONAL,
    disa: str = DISA_JUNIN
) -> QuerySet:
    """
    Obtiene las microredes de una red específica.
    
    Args:
        codigo_red: Código de la red de salud
        descripcion_sector: Descripción del sector (default: GOBIERNO_REGIONAL)
        disa: Código de la DISA (default: JUNIN)
    
    Returns:
        QuerySet con Codigo_MicroRed y MicroRed
    
    Example:
        >>> microredes = get_microredes('1001')
    """
    return (
        MAESTRO_HIS_ESTABLECIMIENTO.objects
        .filter(
            Codigo_Red=codigo_red,
            Descripcion_Sector=descripcion_sector,
            Disa=disa
        )
        .values('Codigo_MicroRed', 'MicroRed')
        .distinct()
        .order_by('MicroRed')
    )


def get_establecimientos(
    descripcion_sector: str = GOBIERNO_REGIONAL,
    disa: str = DISA_JUNIN,
    codigo_microred: Optional[str] = None,
    codigo_red: Optional[str] = None,
    ubigueo: Optional[str] = None
) -> QuerySet:
    """
    Obtiene establecimientos de salud con filtros dinámicos.
    
    Args:
        descripcion_sector: Descripción del sector (default: GOBIERNO_REGIONAL)
        disa: Código de la DISA (default: JUNIN)
        codigo_microred: Código de microred (opcional)
        codigo_red: Código de red (opcional, busca por startswith)
        ubigueo: Código de ubigeo (opcional, busca por startswith)
    
    Returns:
        QuerySet con Codigo_Unico y Nombre_Establecimiento
    
    Example:
        >>> # Todos los establecimientos de JUNIN
        >>> establec = get_establecimientos()
        >>> # Establecimientos de una microred específica
        >>> establec = get_establecimientos(codigo_microred='100101')
        >>> # Establecimientos de una red
        >>> establec = get_establecimientos(codigo_red='1001')
        >>> # Establecimientos de un distrito
        >>> establec = get_establecimientos(ubigueo='1201')
    """
    filtros = {
        'Descripcion_Sector': descripcion_sector,
        'Disa': disa
    }
    
    # Agregar filtros opcionales
    if codigo_microred:
        filtros['Codigo_MicroRed'] = codigo_microred
    
    if codigo_red:
        filtros['Codigo_Red__startswith'] = codigo_red
    
    if ubigueo:
        filtros['Ubigueo_Establecimiento__startswith'] = ubigueo
    
    return (
        MAESTRO_HIS_ESTABLECIMIENTO.objects
        .filter(**filtros)
        .values('Codigo_Unico', 'Nombre_Establecimiento')
        .distinct()
        .order_by('Nombre_Establecimiento')
    )


def get_distritos(
    ubigueo_provincia: str,
    descripcion_sector: str = GOBIERNO_REGIONAL,
    disa: Optional[str] = None
) -> QuerySet:
    """
    Obtiene los distritos de una provincia específica.
    
    Args:
        ubigueo_provincia: Código de ubigeo de la provincia (primeros 4 dígitos)
        descripcion_sector: Descripción del sector (default: GOBIERNO_REGIONAL)
        disa: Código de la DISA (opcional)
    
    Returns:
        QuerySet con Ubigueo_Establecimiento y Distrito
    
    Example:
        >>> distritos = get_distritos('1201')  # DISA JUNIN, provincia de Huancayo
        >>> distritos = get_distritos('1202', disa='JUNIN')
    """
    filtros = {
        'Ubigueo_Establecimiento__startswith': ubigueo_provincia,
        'Descripcion_Sector': descripcion_sector
    }
    
    if disa:
        filtros['Disa'] = disa
    
    return (
        MAESTRO_HIS_ESTABLECIMIENTO.objects
        .filter(**filtros)
        .values('Ubigueo_Establecimiento', 'Distrito')
        .distinct()
        .order_by('Distrito')
    )


def build_filtro_context(
    anio: str = DEFAULT_YEAR,
    descripcion_sector: str = GOBIERNO_REGIONAL,
    disa: str = DISA_JUNIN
) -> Dict[str, Any]:
    """
    Construye un diccionario de contexto con datos comunes para filtros.
    
    Esta función es útil para vistas que necesitan mostrar múltiples
    selectores de filtros (redes, provincias, meses).
    
    Args:
        anio: Año para los periodos (default: 2024)
        descripcion_sector: Descripción del sector (default: GOBIERNO_REGIONAL)
        disa: Código de la DISA (default: JUNIN)
    
    Returns:
        Diccionario con redes_h, provincias_h y mes_inicio
    
    Example:
        >>> context = build_filtro_context('2025')
        >>> # En una vista:
        >>> context.update(build_filtro_context())
    """
    return {
        'redes_h': get_redes(descripcion_sector, disa),
        'provincias_h': get_provincias(descripcion_sector, disa),
        'mes_inicio': get_periodos_mes(anio),
    }
