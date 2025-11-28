# Standard library imports
import locale
import logging
from datetime import datetime
from io import BytesIO
from typing import Dict, List

# Third-party imports
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import column_index_from_string, get_column_letter

# Django imports
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.models import IntegerField,CharField
from django.db.models.functions import Cast, Substr
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic.base import TemplateView

# Local imports
from base.models import MAESTRO_HIS_ESTABLECIMIENTO, DimPeriodo, Actualizacion
from .queries import obtener_velocimetro, obtener_grafico_mensual, obtener_variables, obtener_variables_detallado, obtener_grafico_por_redes
from .queries import obtener_grafico_por_microredes, obtener_grafico_por_establecimientos

# Initialize logger and user model
logger = logging.getLogger(__name__)
User = get_user_model()

# Constants
VALID_YEARS = ['2024', '2025', '2026']
DEFAULT_YEAR = '2025'
GOBIERNO_REGIONAL = 'GOBIERNO REGIONAL'
DISA_JUNIN = 'JUNIN'

############################
## HELPER FUNCTIONS
############################

def _get_default_velocimetro_data() -> Dict[str, List]:
    """Retorna estructura por defecto para datos del velocímetro."""
    return {
        'numerador': [0],
        'denominador': [0],
        'avance': [0.0]
    }

def _extract_velocimetro_values(row: Dict[str, any]) -> tuple:
    """
    Extrae y valida valores del velocímetro desde una fila de datos.
    Args:
        row: Diccionario con datos de NUM, DEN, AVANCE
    Returns:
        Tupla (numerador, denominador, avance) con valores validados
    """
    numerador = row.get('NUM', 0)
    denominador = row.get('DEN', 0)
    avance = row.get('AVANCE', 0.0)
    
    # Asegurar que los valores no sean None
    numerador = numerador if numerador is not None else 0
    denominador = denominador if denominador is not None else 0
    avance = avance if avance is not None else 0.0
    
    return int(numerador), int(denominador), float(avance)

def _get_redes_queryset():
    """Obtiene queryset de redes de salud filtradas por región Junín."""
    return (
        MAESTRO_HIS_ESTABLECIMIENTO.objects
        .filter(Descripcion_Sector=GOBIERNO_REGIONAL, Disa=DISA_JUNIN)
        .annotate(codigo_red_filtrado=Substr('Codigo_Red', 1, 4))
        .values('Red', 'codigo_red_filtrado')
        .distinct()
        .order_by('Red')
    )

def _get_provincias_queryset():
    """Obtiene queryset de provincias filtradas por sector gubernamental."""
    return (
        MAESTRO_HIS_ESTABLECIMIENTO.objects
        .filter(Descripcion_Sector=GOBIERNO_REGIONAL)
        .annotate(ubigueo_filtrado=Substr('Ubigueo_Establecimiento', 1, 4))
        .values('Provincia', 'ubigueo_filtrado')
        .distinct()
        .order_by('Provincia')
    )


######################################
## PROCESOS DE COMPONENTES Y GRAFICOS 
######################################
## VELOCIMETRO
def process_velocimetro(resultados_velocimetro: List[Dict]) -> Dict[str, List]:
    """
    Procesa los resultados del velocímetro para el formato del frontend.
    Args:
        resultados_velocimetro: Lista con un diccionario conteniendo NUM, DEN, AVANCE
    Returns:
        Diccionario con listas de numerador, denominador y avance
    """
    # Validar entrada
    if not resultados_velocimetro or len(resultados_velocimetro) == 0:
        logger.warning("Sin datos de velocímetro, usando valores por defecto")
        return _get_default_velocimetro_data()
    
    # Procesar el primer (y único) registro
    row = resultados_velocimetro[0]
    
    try:
        numerador, denominador, avance = _extract_velocimetro_values(row)
        
        logger.debug(f"Velocímetro procesado: Num={numerador}, Den={denominador}, Avance={avance}%")
        
        return {
            'numerador': [numerador],
            'denominador': [denominador],
            'avance': [avance]
        }
        
    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"Error procesando datos del velocímetro: {e}, Row: {row}")
        return _get_default_velocimetro_data()

## RESUMEN NUMERADOR Y DENOMINADOR 
def obtener_resumen_indicador(anio, mes_inicio, mes_fin, red, microred, establecimiento, provincia=None, distrito=None):
    """
    Obtiene un resumen detallado del indicador 
    """
    datos_base = obtener_velocimetro(anio, mes_inicio, mes_fin, red, microred, establecimiento, provincia, distrito)
    
    if not datos_base:
        return None
    
    resultado = datos_base[0]
    num = resultado.get('NUM', 0)
    den = resultado.get('DEN', 0)
    avance = resultado.get('AVANCE', 0.0)
    
    # Calcular métricas adicionales
    brecha = den - num
    porcentaje_brecha = (brecha / den * 100) if den > 0 else 0
    
    # Determinar clasificación
    if avance >= 82:
        clasificacion = "CUMPLE"
        color = "success"
        icono = "check-circle"
    elif avance >= 70:
        clasificacion = "EN PROCESO"
        color = "warning"
        icono = "clock"
    else:
        clasificacion = "EN RIESGO"
        color = "danger"
        icono = "exclamation-triangle"
    
    resumen = {
        'numerador': num,
        'denominador': den,
        'avance': round(avance, 2),
        'brecha': brecha,
        'porcentaje_brecha': round(porcentaje_brecha, 2),
        'clasificacion': clasificacion,
        'color': color,
        'icono': icono
    }
    
    return resumen

## GRAFICO MENSUALIZADO 
def process_avance_mensual(resultados_avance_mensual: List[Dict]) -> Dict[str, List]:
    """Procesa los resultados del graficos"""
    data = {
        'num_1': [],
        'den_1': [],
        'cob_1': [],
        'num_2': [],
        'den_2': [],
        'cob_2': [],
        'num_3': [],
        'den_3': [],
        'cob_3': [],
        'num_4': [],
        'den_4': [],
        'cob_4': [],
        'num_5': [],
        'den_5': [],
        'cob_5': [],
        'num_6': [],
        'den_6': [],
        'cob_6': [],
        'num_7': [],
        'den_7': [],
        'cob_7': [],
        'num_8': [],
        'den_8': [],
        'cob_8': [],                
        'num_9': [],
        'den_9': [],
        'cob_9': [],
        'num_10': [],
        'den_10': [],
        'cob_10': [],
        'num_11': [],
        'den_11': [],
        'cob_11': [],
        'num_12': [],
        'den_12': [],
        'cob_12': [],
    }
    for index, row in enumerate(resultados_avance_mensual):
        try:
            # Verifica que el diccionario tenga las claves necesarias
            required_keys = {'num_1','den_1','cob_1','num_2','den_2','cob_2','num_3','den_3','cob_3','num_4','den_4','cob_4','num_5','den_5','cob_5','num_6','den_6','cob_6','num_7','den_7','cob_7','num_8','den_8','cob_8','num_9','den_9','cob_9','num_10','den_10','cob_10','num_11','den_11','cob_11','num_12','den_12','cob_12'}
            
            if not required_keys.issubset(row.keys()):
                raise ValueError(f"La fila {index} no tiene las claves necesarias: {row}")
            # Extraer cada valor, convirtiendo a float
            num_1_value = float(row.get('num_1', 0.0))
            den_1_value = float(row.get('den_1', 0.0))
            cob_1_value = float(row.get('cob_1', 0.0))
            num_2_value = float(row.get('num_2', 0.0))
            den_2_value = float(row.get('den_2', 0.0))
            cob_2_value = float(row.get('cob_2', 0.0))
            num_3_value = float(row.get('num_3', 0.0))
            den_3_value = float(row.get('den_3', 0.0))
            cob_3_value = float(row.get('cob_3', 0.0))
            num_4_value = float(row.get('num_4', 0.0))
            den_4_value = float(row.get('den_4', 0.0))
            cob_4_value = float(row.get('cob_4', 0.0))
            num_5_value = float(row.get('num_5', 0.0))
            den_5_value = float(row.get('den_5', 0.0))
            cob_5_value = float(row.get('cob_5', 0.0))
            num_6_value = float(row.get('num_6', 0.0))
            den_6_value = float(row.get('den_6', 0.0))
            cob_6_value = float(row.get('cob_6', 0.0))
            num_7_value = float(row.get('num_7', 0.0))
            den_7_value = float(row.get('den_7', 0.0))
            cob_7_value = float(row.get('cob_7', 0.0))
            num_8_value = float(row.get('num_8', 0.0))
            den_8_value = float(row.get('den_8', 0.0))
            cob_8_value = float(row.get('cob_8', 0.0))
            num_9_value = float(row.get('num_9', 0.0))
            den_9_value = float(row.get('den_9', 0.0))
            cob_9_value = float(row.get('cob_9', 0.0))
            num_10_value = float(row.get('num_10', 0.0))
            den_10_value = float(row.get('den_10', 0.0))
            cob_10_value = float(row.get('cob_10', 0.0))
            num_11_value = float(row.get('num_11', 0.0))
            den_11_value = float(row.get('den_11', 0.0))
            cob_11_value = float(row.get('cob_11', 0.0))
            num_12_value = float(row.get('num_12', 0.0))
            den_12_value = float(row.get('den_12', 0.0))
            cob_12_value = float(row.get('cob_12', 0.0))
            
            data['num_1'].append(num_1_value)
            data['den_1'].append(den_1_value)
            data['cob_1'].append(cob_1_value)
            data['num_2'].append(num_2_value)
            data['den_2'].append(den_2_value)
            data['cob_2'].append(cob_2_value)
            data['num_3'].append(num_3_value)
            data['den_3'].append(den_3_value)
            data['cob_3'].append(cob_3_value)
            data['num_4'].append(num_4_value)
            data['den_4'].append(den_4_value)
            data['cob_4'].append(cob_4_value)
            data['num_5'].append(num_5_value)
            data['den_5'].append(den_5_value)
            data['cob_5'].append(cob_5_value)
            data['num_6'].append(num_6_value)
            data['den_6'].append(den_6_value)
            data['cob_6'].append(cob_6_value)
            data['num_7'].append(num_7_value)
            data['den_7'].append(den_7_value)
            data['cob_7'].append(cob_7_value)
            data['num_8'].append(num_8_value)
            data['den_8'].append(den_8_value)
            data['cob_8'].append(cob_8_value)
            data['num_9'].append(num_9_value)
            data['den_9'].append(den_9_value)
            data['cob_9'].append(cob_9_value)
            data['num_10'].append(num_10_value)
            data['den_10'].append(den_10_value)
            data['cob_10'].append(cob_10_value)
            data['num_11'].append(num_11_value)
            data['den_11'].append(den_11_value)
            data['cob_11'].append(cob_11_value)
            data['num_12'].append(num_12_value)
            data['den_12'].append(den_12_value)
            data['cob_12'].append(cob_12_value)

        except Exception as e:
            logger.error(f"Error procesando la fila {index}: {str(e)}")
    return data

## GRAFICO VARIABLES 
def process_variables(resultados_variables: List[Dict]) -> Dict[str, List]:
    """Procesa los resultados de las variables"""
    data = {
        'den_variable': [],
        'num_1trim': [],
        'avance_1trim': [],
        'num_2trim': [],
        'avance_2trim': [],
        'num_3trim': [],
        'avance_3trim': []
    }
    for index, row in enumerate(resultados_variables):
        try:
            # Verifica que el diccionario tenga las claves necesarias
            required_keys = {'den_variable','num_1trim','avance_1trim','num_2trim','avance_2trim','num_3trim','avance_3trim'}
            
            if not required_keys.issubset(row.keys()):
                raise KeyError(f"Falta una o más claves en la fila {index}: {required_keys - row.keys()}")
            
            # Extrae los valores
            den_variable = row['den_variable']
            num_1trim = row['num_1trim']
            avance_1trim = row['avance_1trim']
            num_2trim = row['num_2trim']
            avance_2trim = row['avance_2trim']
            num_3trim = row['num_3trim']
            avance_3trim = row['avance_3trim']
            
            # Agrega los valores a la lista
            data['den_variable'].append(den_variable)
            data['num_1trim'].append(num_1trim)
            data['avance_1trim'].append(avance_1trim)
            data['num_2trim'].append(num_2trim)
            data['avance_2trim'].append(avance_2trim)
            data['num_3trim'].append(num_3trim)
            data['avance_3trim'].append(avance_3trim)
            
        except KeyError as e:
            logger.error(f"Error procesando la fila {index}: {str(e)}")
    return data

## TABLLA VARIABLES DETALLADOS
def process_variables_detallado(resultados_variables_detallado: List[Dict]) -> Dict[str, List]:
    """Procesa los resultados de las variables detalladas
    NOTA: Usa prefijo 'detallado_' para las claves para NO sobrescribir los datos agregados"""
    data = {
        'd_anio': [],
        'd_mes': [],
        'd_codigo_red': [],
        'd_red': [],
        'd_codigo_microred': [],
        'd_microred': [],
        'd_codigo_unico': [],
        'd_id_establecimiento': [],
        'd_nombre_establecimiento': [],
        'd_ubigueo_establecimiento': [],
        'd_den_variable': [],
        'd_num_1trim': [],
        'd_avance_1trim': [],
        'd_num_2trim': [],
        'd_avance_2trim': [],
        'd_num_3trim': [],
        'd_avance_3trim': []
    }
    for index, row in enumerate(resultados_variables_detallado):
        try:
            # Verifica que el diccionario tenga las claves necesarias
            required_keys = {'d_anio','d_mes','d_codigo_red','d_red','d_codigo_microred','d_microred','d_codigo_unico','d_id_establecimiento','d_nombre_establecimiento','d_ubigueo_establecimiento','d_den_variable','d_num_1trim','d_avance_1trim','d_num_2trim','d_avance_2trim','d_num_3trim','d_avance_3trim'}
            
            if not required_keys.issubset(row.keys()):
                raise KeyError(f"Falta una o más claves en la fila {index}: {required_keys - row.keys()}")
            
            # Extrae los valores (las claves NO tienen el prefijo 'detallado_' en los datos)
            d_anio = row['d_anio']
            d_mes = row['d_mes']
            d_codigo_red = row['d_codigo_red']
            d_red = row['d_red']
            d_codigo_microred = row['d_codigo_microred']
            d_microred = row['d_microred']
            d_codigo_unico = row['d_codigo_unico']
            d_id_establecimiento = row['d_id_establecimiento']
            d_nombre_establecimiento = row['d_nombre_establecimiento']
            d_ubigueo_establecimiento = row['d_ubigueo_establecimiento']
            d_den_variable = row['d_den_variable']
            d_num_1trim = row['d_num_1trim']
            d_avance_1trim = row['d_avance_1trim']
            d_num_2trim = row['d_num_2trim']
            d_avance_2trim = row['d_avance_2trim']
            d_num_3trim = row['d_num_3trim']
            d_avance_3trim = row['d_avance_3trim']
            
            # Agrega los valores a la lista CON PREFIJO
            data['d_anio'].append(d_anio)
            data['d_mes'].append(d_mes)
            data['d_codigo_red'].append(d_codigo_red)
            data['d_red'].append(d_red)
            data['d_codigo_microred'].append(d_codigo_microred)
            data['d_microred'].append(d_microred)
            data['d_codigo_unico'].append(d_codigo_unico)
            data['d_id_establecimiento'].append(d_id_establecimiento)
            data['d_nombre_establecimiento'].append(d_nombre_establecimiento)
            data['d_ubigueo_establecimiento'].append(d_ubigueo_establecimiento)
            data['d_den_variable'].append(d_den_variable)
            data['d_num_1trim'].append(d_num_1trim)
            data['d_avance_1trim'].append(d_avance_1trim)
            data['d_num_2trim'].append(d_num_2trim)
            data['d_avance_2trim'].append(d_avance_2trim)
            data['d_num_3trim'].append(d_num_3trim)
            data['d_avance_3trim'].append(d_avance_3trim)
            
        except KeyError as e:
            logger.error(f"Error procesando la fila {index}: {str(e)}")
    return data

## GRAFICO DE RANKING POR REDES
def process_grafico_por_redes(resultados_grafico_por_redes: List[Dict]) -> Dict[str, List]:
    """Procesa los resultados del graficos por redes"""
    data = {
            'red_r': [],
            'den_r': [],
            'num_r': [],
            'avance_r': [],
            'brecha_r': [],
    }   
    for index, row in enumerate(resultados_grafico_por_redes):
        try:
            # Verifica que el diccionario tenga las claves necesarias
            required_keys = {'red_r','den_r','num_r','avance_r','brecha_r'}
            
            if not required_keys.issubset(row.keys()):
                raise KeyError(f"Falta una o más claves en la fila {index}: {required_keys - row.keys()}")
            
            # Extrae los valores
            red_r = row['red_r']
            den_r = row['den_r']
            num_r = row['num_r']
            avance_r = row['avance_r']
            brecha_r = row['brecha_r']
            
            # Agrega los valores a la lista
            data['red_r'].append(red_r)
            data['den_r'].append(den_r)
            data['num_r'].append(num_r)
            data['avance_r'].append(avance_r)
            data['brecha_r'].append(brecha_r)

        except KeyError as e:
            logger.warning(f"Fila con estructura inválida (clave faltante: {e}): {row}")
    return data

## GRAFICO DE RANKING POR MICROREDES
def process_grafico_por_microredes(resultados_grafico_por_microredes: List[Dict]) -> Dict[str, List]:
    """Procesa los resultados del graficos por microredes"""
    data = {
            'microred_mr': [],
            'den_mr': [],
            'num_mr': [],
            'avance_mr': [],
            'brecha_mr': [],
    }   
    for index, row in enumerate(resultados_grafico_por_microredes):
        try:
            # Verifica que el diccionario tenga las claves necesarias
            required_keys = {'microred_mr','den_mr','num_mr','avance_mr','brecha_mr'}
            
            if not required_keys.issubset(row.keys()):
                raise KeyError(f"Falta una o más claves en la fila {index}: {required_keys - row.keys()}")
            
            # Extrae los valores
            microred_mr = row['microred_mr']
            den_mr = row['den_mr']
            num_mr = row['num_mr']
            avance_mr = row['avance_mr']
            brecha_mr = row['brecha_mr']
            
            # Agrega los valores a la lista
            data['microred_mr'].append(microred_mr)
            data['den_mr'].append(den_mr)
            data['num_mr'].append(num_mr)
            data['avance_mr'].append(avance_mr)
            data['brecha_mr'].append(brecha_mr)

        except KeyError as e:
            logger.warning(f"Fila con estructura inválida (clave faltante: {e}): {row}")
    return data

## GRAFICO DE RANKING POR ESTABLECIMIENTOS
def process_grafico_por_establecimientos(resultados_grafico_por_establecimientos: List[Dict]) -> Dict[str, List]:
    """Procesa los resultados del graficos por establecimientos"""
    data = {
            'establecimiento_e': [],
            'den_e': [],
            'num_e': [],
            'avance_e': [],
            'brecha_e': [],
    }   
    for index, row in enumerate(resultados_grafico_por_establecimientos):
        try:
            # Verifica que el diccionario tenga las claves necesarias
            required_keys = {'establecimiento_e','den_e','num_e','avance_e','brecha_e'}
            
            if not required_keys.issubset(row.keys()):
                raise KeyError(f"Falta una o más claves en la fila {index}: {required_keys - row.keys()}")
            
            # Extrae los valores
            establecimiento_e = row['establecimiento_e']
            den_e = row['den_e']
            num_e = row['num_e']
            avance_e = row['avance_e']
            brecha_e = row['brecha_e']
            
            # Agrega los valores a la lista
            data['establecimiento_e'].append(establecimiento_e)
            data['den_e'].append(den_e)
            data['num_e'].append(num_e)
            data['avance_e'].append(avance_e)
            data['brecha_e'].append(brecha_e)

        except KeyError as e:
            logger.warning(f"Fila con estructura inválida (clave faltante: {e}): {row}")
    return data

#######################
## PANTALLA PRINCIPAL
#######################

def index_s11_captacion_gestante(request):
    """
    Vista principal para la pantalla de captación de gestantes.

    Maneja tanto la renderización inicial de la página como las peticiones AJAX
    para obtener datos del velocímetro según filtros aplicados.
    """
    # Obtener datos de actualización
    actualizacion = Actualizacion.objects.all()
    
    # Validar y obtener año
    anio = request.GET.get('anio', DEFAULT_YEAR)
    if anio not in VALID_YEARS:
        anio = DEFAULT_YEAR
    
    # Obtener parámetros de filtro
    mes_seleccionado_inicio = request.GET.get('mes_inicio')
    mes_seleccionado_fin = request.GET.get('mes_fin')
    provincia_seleccionada = request.GET.get('provincia_h')
    distrito_seleccionado = request.GET.get('distrito_h')
    red_seleccionada = request.GET.get('red_h')
    microred_seleccionada = request.GET.get('p_microredes_establec_h')
    establecimiento_seleccionado = request.GET.get('p_establecimiento_h')
    
    # Manejar peticiones AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            # Obtener datos del velocímetro con los filtros aplicados
            resultados_velocimetro = obtener_velocimetro(
                anio=anio,
                mes_inicio=mes_seleccionado_inicio,
                mes_fin=mes_seleccionado_fin,
                red=red_seleccionada,
                microred=microred_seleccionada,
                establecimiento=establecimiento_seleccionado,
                provincia=provincia_seleccionada,
                distrito=distrito_seleccionado
            )

            # Obtener resumen del indicador
            resumen = obtener_resumen_indicador(
                anio=anio,
                mes_inicio=mes_seleccionado_inicio,
                mes_fin=mes_seleccionado_fin,
                red=red_seleccionada,
                microred=microred_seleccionada,
                establecimiento=establecimiento_seleccionado,
                provincia=provincia_seleccionada,
                distrito=distrito_seleccionado
            )

            resultados_grafico_mensual = obtener_grafico_mensual(
                anio=anio,
                mes_inicio=mes_seleccionado_inicio,  # Siempre desde Enero,  # Usa el mes de inicio seleccionado
                mes_fin=mes_seleccionado_fin,      # Usa el mes de fin seleccionado
                red=red_seleccionada,
                microred=microred_seleccionada,
                establecimiento=establecimiento_seleccionado,
                provincia=provincia_seleccionada,
                distrito=distrito_seleccionado
            )
            
            # Obtener datos del grafico mensualizado - SIEMPRE todos los meses del año
            # Los filtros de mes NO afectan el gráfico mensual, solo el velocímetro y resumen
            resultados_variables = obtener_variables(
                anio=anio,
                mes_inicio=mes_seleccionado_inicio,
                mes_fin=mes_seleccionado_fin, # Siempre hasta Diciembre
                red=red_seleccionada,
                microred=microred_seleccionada,
                establecimiento=establecimiento_seleccionado,
                provincia=provincia_seleccionada,
                distrito=distrito_seleccionado
            )

            # Obtener datos de variables por trimestre - RESPETA los filtros de mes
            resultados_variables_detallado = obtener_variables_detallado(
                anio=anio,
                mes_inicio=mes_seleccionado_inicio,  # Usa el mes de inicio seleccionado
                mes_fin=mes_seleccionado_fin,        # Usa el mes de fin seleccionado
                red=red_seleccionada,
                microred=microred_seleccionada,
                establecimiento=establecimiento_seleccionado,
                provincia=provincia_seleccionada,
                distrito=distrito_seleccionado
            )
            
            resultados_grafico_por_redes = obtener_grafico_por_redes(
                anio=anio,
                mes_inicio=mes_seleccionado_inicio,  # Usa el mes de inicio seleccionado
                mes_fin=mes_seleccionado_fin,        # Usa el mes de fin seleccionado
                red=red_seleccionada,
                microred=microred_seleccionada,
                establecimiento=establecimiento_seleccionado,
                provincia=provincia_seleccionada,
                distrito=distrito_seleccionado
            )
            
            resultados_grafico_por_microredes = obtener_grafico_por_microredes(
                anio=anio,
                mes_inicio=mes_seleccionado_inicio,  # Usa el mes de inicio seleccionado
                mes_fin=mes_seleccionado_fin,        # Usa el mes de fin seleccionado
                red=red_seleccionada,
                microred=microred_seleccionada,
                establecimiento=establecimiento_seleccionado,
                provincia=provincia_seleccionada,
                distrito=distrito_seleccionado
            )
            
            resultados_grafico_por_establecimientos = obtener_grafico_por_establecimientos(
                anio=anio,
                mes_inicio=mes_seleccionado_inicio,  # Usa el mes de inicio seleccionado
                mes_fin=mes_seleccionado_fin,        # Usa el mes de fin seleccionado
                red=red_seleccionada,
                microred=microred_seleccionada,
                establecimiento=establecimiento_seleccionado,
                provincia=provincia_seleccionada,
                distrito=distrito_seleccionado
            )

            # Procesar datos del velocímetro
            data = {
               **process_velocimetro(resultados_velocimetro),
               **process_avance_mensual(resultados_grafico_mensual),
               **process_variables(resultados_variables),
               **process_variables_detallado(resultados_variables_detallado),
               **process_grafico_por_redes(resultados_grafico_por_redes),
               **process_grafico_por_microredes(resultados_grafico_por_microredes),
               **process_grafico_por_establecimientos(resultados_grafico_por_establecimientos)
            }

                        # Agregar datos del resumen a la respuesta
            if resumen:
                data['r_numerador_resumen'] = resumen['numerador']
                data['r_denominador_resumen'] = resumen['denominador']
                data['r_avance_resumen'] = resumen['avance']
                data['r_brecha'] = resumen['brecha']
                data['r_clasificacion'] = resumen['clasificacion']
                data['r_color'] = resumen['color']
                data['r_icono'] = resumen['icono']
            
            return JsonResponse(data)
            
        except Exception as e:
            logger.error(f"Error al obtener datos de captación de gestantes: {e}", exc_info=True)
            return JsonResponse(
                {'error': 'Error al obtener datos. Por favor, intente nuevamente.'},
                status=500
            )
    
    # Renderizado inicial de la página
    context = {
        'mes_seleccionado_inicio': mes_seleccionado_inicio,
        'mes_seleccionado_fin': mes_seleccionado_fin,
        'actualizacion': actualizacion,
        'provincia_seleccionada': provincia_seleccionada,
        'distrito_seleccionado': distrito_seleccionado,
        'provincias_h': _get_provincias_queryset(),
        'redes_h': _get_redes_queryset(),
    }
    
    return render(request, 's11_captacion_gestante/index_s11_captacion_gestante.html', context)


############################
## FILTROS HORIZONTAL
############################

def get_establecimientos_s11_captacion_gestante_h(request, establecimiento_id):
    """
    Vista para renderizar la página de establecimientos con filtros horizontales.
    
    Args:
        request: HttpRequest
        establecimiento_id: ID del establecimiento (no usado actualmente, 
                           mantenido por compatibilidad con URL)
    
    Returns:
        Render del template con contexto de filtros
    """
    from .utils import build_filtro_context
    
    # Obtener el contexto completo de filtros usando la función reutilizable
    context = build_filtro_context(anio='2024')
    
    return render(request, 's11_captacion_gestante/establecimientos_h.html', context)


def p_microredes_establec_s11_captacion_gestante_h(request):
    """
    Vista parcial HTMX para cargar microredes según la red seleccionada.
    
    Args:
        request: HttpRequest con parámetro GET 'red_h'
    
    Returns:
        Render del partial con microredes filtradas
    """
    from .utils import get_microredes
    
    red_codigo = request.GET.get('red_h', '')
    
    # Usar la función reutilizable
    microredes = get_microredes(codigo_red=red_codigo) if red_codigo else []
    
    context = {
        'microredes': microredes,
        'is_htmx': True
    }
    
    return render(request, 's11_captacion_gestante/partials/p_microredes_establec_h.html', context)


def p_establecimientos_s11_captacion_gestante_h(request):
    """
    Vista parcial HTMX para cargar establecimientos según microred o red seleccionada.
    Args:
        request: HttpRequest con parámetros GET:
                - 'p_microredes_establec_h': código de microred (opcional)
                - 'red_h': código de red (opcional)
    Returns:
        Render del partial con establecimientos filtrados
    """
    from .utils import get_establecimientos
    
    microred_codigo = request.GET.get('p_microredes_establec_h', '')
    red_codigo = request.GET.get('red_h', '')
    
    # Usar la función reutilizable con filtros dinámicos
    establecimientos = get_establecimientos(
        codigo_microred=microred_codigo if microred_codigo else None,
        codigo_red=red_codigo if red_codigo else None
    )
    
    # Convertir a lista para debug si es necesario
    establecimientos_list = list(establecimientos)
    
    context = {
        'establec': establecimientos_list
    }
    
    return render(request, 's11_captacion_gestante/partials/p_establecimientos_h.html', context)


def p_distritos_s11_captacion_gestante_h(request):
    """
    Vista parcial HTMX para cargar distritos según la provincia seleccionada.
    
    Args:
        request: HttpRequest con parámetro GET 'provincia'
    
    Returns:
        Render del partial con distritos filtrados
    """
    from .utils import get_distritos, get_provincias
    
    provincia_ubigueo = request.GET.get('provincia', '')
    
    # Obtener provincias para el contexto
    provincias = get_provincias()
    
    # Obtener distritos usando la función reutilizable
    distritos = get_distritos(ubigueo_provincia=provincia_ubigueo) if provincia_ubigueo else []
    
    context = {
        'distritos': distritos,
        'provincias_h': provincias
    }
    
    return render(request, 's11_captacion_gestante/partials/p_distritos.html', context)


###########################################
## SEGUIMIENTO NOMINAL FILTROS
##########################################

###########################################
## FILTRO AMBITO DE SALUD
###########################################

## ============================================
# CONFIGURACIÓN BASE
# ============================================
FILTROS_BASE = {
    'Descripcion_Sector': 'GOBIERNO REGIONAL',
    'Disa': 'JUNIN'
}


FILTROS_BASE_ESTABLECIMIENTO = {
    'Descripcion_Sector': 'GOBIERNO REGIONAL',
    'Disa': 'JUNIN'
}

# ============================================
# HELPER FUNCTIONS - QUERIES REUTILIZABLES
# ============================================

def _get_redes_queryset():
    """
    Obtiene las redes de salud del gobierno regional de Junín.
    Returns: QuerySet con Codigo_Red, Red y codigo_red_filtrado
    """
    return (
        MAESTRO_HIS_ESTABLECIMIENTO.objects
        .filter(**FILTROS_BASE_ESTABLECIMIENTO)
        .annotate(codigo_red_filtrado=Substr('Codigo_Red', 1, 4))
        .values('Codigo_Red', 'Red', 'codigo_red_filtrado')
        .distinct()
        .order_by('Red')
    )


def _get_meses_queryset(anio=None):
    """
    Obtiene los meses disponibles para los filtros.
    Args:
        anio: Año opcional para filtrar (None = todos los años)
    Returns: QuerySet con Mes y nro_mes
    """
    queryset = DimPeriodo.objects.all()
    
    if anio:
        queryset = queryset.filter(Anio=anio)
    
    return (
        queryset
        .annotate(nro_mes=Cast('NroMes', IntegerField()))
        .values('Mes', 'nro_mes')
        .order_by('nro_mes')
        .distinct()
    )


def _get_microredes_queryset(codigo_red):
    """
    Obtiene las microredes según el código de red.
    Args:
        codigo_red: Código de la red (puede ser parcial para usar startswith)
    Returns: QuerySet con Codigo_MicroRed y MicroRed
    """
    if not codigo_red:
        return []
    
    return (
        MAESTRO_HIS_ESTABLECIMIENTO.objects
        .filter(
            Codigo_Red__startswith=codigo_red,
            **FILTROS_BASE_ESTABLECIMIENTO
        )
        .values('Codigo_MicroRed', 'MicroRed')
        .distinct()
        .order_by('MicroRed')
    )


def _get_establecimientos_queryset(codigo_microred, codigo_red=None):
    """
    Obtiene los establecimientos según la microred.
    Args:
        codigo_microred: Código de la microred
        codigo_red: Código de la red (opcional, para filtro adicional)
    Returns: QuerySet con Codigo_Unico y Nombre_Establecimiento
    """
    if not codigo_microred:
        return []
    
    filtros = {
        'Codigo_MicroRed__startswith': codigo_microred,
        **FILTROS_BASE_ESTABLECIMIENTO
    }
    
    if codigo_red:
        filtros['Codigo_Red__startswith'] = codigo_red
    
    return (
        MAESTRO_HIS_ESTABLECIMIENTO.objects
        .filter(**filtros)
        .values('Codigo_Unico', 'Nombre_Establecimiento')
        .distinct()
        .order_by('Nombre_Establecimiento')
    )


def _get_context_base_con_filtros(include_meses=True, anio_meses=None):
    """
    Genera el contexto base común para los formularios.
    Args:
        include_meses: Si incluir los meses en el contexto
        anio_meses: Año para filtrar meses (None = todos)
    Returns: dict con redes y opcionalmente meses
    """
    context = {
        'redes': _get_redes_queryset(),
    }
    
    if include_meses:
        meses = _get_meses_queryset(anio_meses)
        context.update({
            'mes_inicio': meses,
            'mes_fin': meses,
        })
    
    return context


# ============================================
# VISTAS PRINCIPALES - FORMULARIOS
# ============================================

def get_redes_s11_captacion_gestante(request, redes_id):
    """
    Renderiza el formulario de reportes por REDES.
    """
    context = _get_context_base_con_filtros(include_meses=True)
    return render(request, 's11_captacion_gestante/components/salud/redes.html', context)


def get_microredes_s11_captacion_gestante(request, microredes_id):
    """
    Renderiza el formulario de reportes por MICROREDES.
    """
    context = _get_context_base_con_filtros(include_meses=True, anio_meses='2024')
    return render(request, 's11_captacion_gestante/components/salud/microredes.html', context)


def get_establecimientos_s11_captacion_gestante(request, establecimiento_id):
    """Renderiza el formulario de reportes por ESTABLECIMIENTO."""
    context = {
        'redes': _get_redes_queryset(),
        'mes_inicio': _get_meses_queryset(),
        'mes_fin': _get_meses_queryset(),
    }
    return render(request, 's11_captacion_gestante/components/salud/establecimientos.html', context)


# ============================================
# VISTAS PARTIALS - HTMX
# ============================================

def p_microredes_s11_captacion_gestante(request):
    """
    Partial HTMX: Carga microredes según la red seleccionada.
    Usado en el formulario de MICROREDES (sin encadenamiento).
    
    GET params:
        - red: Código de la red seleccionada
    """
    red = request.GET.get('red', '').strip()
    microredes = list(_get_microredes_queryset(red))
    
    context = {
        'microredes': microredes,
        'red': red,
    }
    
    return render(request, 's11_captacion_gestante/partials/p_microredes.html', context)


def p_microredes_establec_s11_captacion_gestante(request):
    """
    HTMX Partial: Carga microredes según la red seleccionada.
    Se encadena con el select de establecimientos.
    """
    red = request.GET.get('red', '').strip()
    
    # Debug
    print(f"[p_microredes_establec] RED recibida: '{red}'")
    
    microredes = []
    if red:
        microredes = list(
            MAESTRO_HIS_ESTABLECIMIENTO.objects
            .filter(Codigo_Red__startswith=red, **FILTROS_BASE)
            .values('Codigo_MicroRed', 'MicroRed')
            .distinct()
            .order_by('MicroRed')
        )
        print(f"[p_microredes_establec] Microredes encontradas: {len(microredes)}")
    
    return render(request, 's11_captacion_gestante/partials/p_microredes_establec.html', {
        'microredes': microredes,
        'red': red,
    })

# ============================================
# PARTIAL: ESTABLECIMIENTOS
# ============================================
def p_establecimientos_s11_captacion_gestante(request):
    """
    HTMX Partial: Carga establecimientos según la microred seleccionada.
    """
    microred = request.GET.get('microred', '').strip()
    red = request.GET.get('red', '').strip()
    
    # Debug
    print(f"[p_establecimientos] MICRORED: '{microred}', RED: '{red}'")
    
    establecimientos = []
    if microred:
        filtros = {'Codigo_MicroRed': microred, **FILTROS_BASE}
        if red:
            filtros['Codigo_Red__startswith'] = red
        
        establecimientos = list(
            MAESTRO_HIS_ESTABLECIMIENTO.objects
            .filter(**filtros)
            .values('Codigo_Unico', 'Nombre_Establecimiento')
            .distinct()
            .order_by('Nombre_Establecimiento')
        )
        print(f"[p_establecimientos] Establecimientos encontrados: {len(establecimientos)}")
    
    return render(request, 's11_captacion_gestante/partials/p_establecimientos.html', {
        'establecimientos': establecimientos,
    })
######################---------------------------
## FILTRO AMBITO DE MUNICIPIO
######################-------------------------------

## SEGUIMIENTO POR PROVINCIA
def get_provincias_s11_captacion_gestante(request, provincia_id):
    provincias = (
                MAESTRO_HIS_ESTABLECIMIENTO
                .objects.filter(Descripcion_Sector='GOBIERNO REGIONAL')
                .annotate(ubigueo_filtrado=Substr('Ubigueo_Establecimiento', 1, 4))
                .values('Provincia','ubigueo_filtrado')
                .distinct()
                .order_by('Provincia')
    )
    mes_inicio = (
                DimPeriodo
                .objects.filter()
                .annotate(nro_mes=Cast('NroMes', IntegerField())) 
                .values('Mes','nro_mes')
                .order_by('NroMes')
                .distinct()
    ) 
    mes_fin = (
                DimPeriodo
                .objects.filter()
                .annotate(nro_mes=Cast('NroMes', IntegerField())) 
                .values('Mes','nro_mes')
                .order_by('NroMes')
                .distinct()
    )
    context = {
                'provincias': provincias,
                'mes_inicio':mes_inicio,
                'mes_fin':mes_fin,
            }
    
    return render(request, 's11_captacion_gestante/components/municipio/provincias.html', context)

## SEGUIMIENTO POR DISTRITOS
def get_distritos_s11_captacion_gestante(request, distrito_id):
    provincias = (
                MAESTRO_HIS_ESTABLECIMIENTO
                .objects.filter(Descripcion_Sector='GOBIERNO REGIONAL')
                .annotate(ubigueo_filtrado=Substr('Ubigueo_Establecimiento', 1, 4))
                .values('Provincia','ubigueo_filtrado')
                .distinct()
                .order_by('Provincia')
    )
    mes_inicio = (
                DimPeriodo
                .objects.filter()
                .annotate(nro_mes=Cast('NroMes', IntegerField())) 
                .values('Mes','nro_mes')
                .order_by('NroMes')
                .distinct()
    ) 
    mes_fin = (
                DimPeriodo
                .objects.filter()
                .annotate(nro_mes=Cast('NroMes', IntegerField())) 
                .values('Mes','nro_mes')
                .order_by('NroMes')
                .distinct()
    ) 
    context = {
                'provincias': provincias,
                'mes_inicio':mes_inicio,
                'mes_fin':mes_fin,
    }
    return render(request, 's11_captacion_gestante/components/municipio/distritos.html', context)


def p_distrito_s11_captacion_gestante(request):
    provincia_param = request.GET.get('provincia', '')

    # Filtra los establecimientos por sector "GOBIERNO REGIONAL"
    establecimientos = MAESTRO_HIS_ESTABLECIMIENTO.objects.filter(Descripcion_Sector='GOBIERNO REGIONAL')

    # Filtra los establecimientos por el código de la provincia
    if provincia_param:
        establecimientos = establecimientos.filter(Ubigueo_Establecimiento__startswith=provincia_param[:4])
    # Selecciona el distrito y el código Ubigueo
    distritos = establecimientos.values('Distrito', 'Ubigueo_Establecimiento').distinct().order_by('Distrito')
    
    context = {
        'provincia': provincia_param,
        'distritos': distritos
    }
    return render(request, 's11_captacion_gestante/partials/p_distritos.html', context)


########################################
## SEGUIMIENTO REPORTE EXCEL 
#######################################

## REPORTE DE EXCEL
class RptCaptacionGestante(TemplateView):
    def get(self, request, *args, **kwargs):
        # Variables ingresadas
        anio = request.GET.get('anio', '2025')
        mes_inicio = request.GET.get('fecha_inicio', '')
        mes_fin = request.GET.get('fecha_fin', '')
        provincia = request.GET.get('provincia', '')
        distrito = request.GET.get('distrito', '')
        p_red = request.GET.get('red', '')
        p_microredes = request.GET.get('p_microredes', '')
        p_establecimiento = request.GET.get('p_establecimiento', '')
        p_cumple = request.GET.get('cumple', '') 

        # Creación de la consulta
        #print(f"Año: {anio}, Mes Inicio: {mes_inicio}, Mes Fin: {mes_fin}, Provincia: {provincia}, Distrito: {distrito}, Red: {p_red}, Microredes: {p_microredes}, Establecimiento: {p_establecimiento}, Cumple: {p_cumple}")
        resultado_seguimiento_s11_captacion_gestante = obtener_seguimiento_s11_captacion_gestante(anio, mes_inicio, mes_fin, provincia, distrito, p_red, p_microredes, p_establecimiento, p_cumple)
        
        wb = Workbook()
        
        consultas = [
                ('Seguimiento', resultado_seguimiento_s11_captacion_gestante)
        ]
        
        for index, (sheet_name, results) in enumerate(consultas):
            if index == 0:
                ws = wb.active
                ws.title = sheet_name
            else:
                ws = wb.create_sheet(title=sheet_name)
        
            fill_worksheet(ws, results)
        
        ##########################################################################          
        # Establecer el nombre del archivo
        nombre_archivo = "rpt_s11_captacion_gestante.xlsx"
        # Definir el tipo de respuesta que se va a dar
        response = HttpResponse(content_type="application/ms-excel")
        contenido = "attachment; filename={}".format(nombre_archivo)
        response["Content-Disposition"] = contenido
        wb.save(response)

        return response

class RptPnPoblacionMicroRed(TemplateView):
    def get(self, request, *args, **kwargs):
        # Variables ingresadas
        p_departamento = 'JUNIN'
        p_red = request.GET.get('red', '')
        p_microred = request.GET.get('microredes', '')
        p_establec = ''
        p_edades =  request.GET.get('edades','')
        p_cumple = request.GET.get('cumple', '') 
        # Creación de la consulta
        resultado_seguimiento_microred = obtener_seguimiento_s11_captacion_gestante_microred(p_departamento, p_red, p_microred, p_edades, p_cumple)

        wb = Workbook()
        
        consultas = [
                ('Seguimiento', resultado_seguimiento_microred)
        ]
        
        for index, (sheet_name, results) in enumerate(consultas):
            if index == 0:
                ws = wb.active
                ws.title = sheet_name
            else:
                ws = wb.create_sheet(title=sheet_name)
        
            fill_worksheet(ws, results)
        
        ##########################################################################          
        # Establecer el nombre del archivo
        nombre_archivo = "rpt_s11_captacion_gestante_microred.xlsx"
        # Definir el tipo de respuesta que se va a dar
        response = HttpResponse(content_type="application/ms-excel")
        contenido = "attachment; filename={}".format(nombre_archivo)
        response["Content-Disposition"] = contenido
        wb.save(response)

        return response

class RptPnPoblacionEstablec(TemplateView):
    def get(self, request, *args, **kwargs):
        # Variables ingresadas
        p_departamento = 'JUNIN'
        p_red = request.GET.get('red','')
        p_microred = request.GET.get('p_microredes_establec','')  # Corregido
        p_establec = request.GET.get('p_establecimiento','')
        p_mes = request.GET.get('mes', '')
        p_edades = request.GET.get('edades', '')
        # Manejo seguro de fechas - usar valores por defecto si no están presentes
        p_cumple = request.GET.get('cumple', '')
        
        # Creación de la consulta
        resultado_seguimiento = obtener_seguimiento_s11_captacion_gestante_establecimiento(p_departamento,p_establec,p_edades,p_cumple)
                
        wb = Workbook()
        
        consultas = [
                ('Seguimiento', resultado_seguimiento)
        ]
        
        for index, (sheet_name, results) in enumerate(consultas):
            if index == 0:
                ws = wb.active
                ws.title = sheet_name
            else:
                ws = wb.create_sheet(title=sheet_name)
        
            fill_worksheet(ws, results)
        
        ##########################################################################          
        # Establecer el nombre del archivo
        nombre_archivo = "rpt_s11_captacion_gestante_establecimiento.xlsx"
        # Definir el tipo de respuesta que se va a dar
        response = HttpResponse(content_type="application/ms-excel")
        contenido = "attachment; filename={}".format(nombre_archivo)
        response["Content-Disposition"] = contenido
        wb.save(response)

        return response


def fill_worksheet(ws, results): 
# cambia el alto de la columna
    ws.row_dimensions[1].height = 14
    ws.row_dimensions[2].height = 14
    ws.row_dimensions[3].height = 12
    ws.row_dimensions[4].height = 25
    ws.row_dimensions[5].height = 18
    ws.row_dimensions[6].height = 18
    ws.row_dimensions[7].height = 25
    ws.row_dimensions[8].height = 30
    # cambia el ancho de la columna
    ws.column_dimensions['A'].width = 1
    ws.column_dimensions['B'].width = 2
    ws.column_dimensions['C'].width = 9
    ws.column_dimensions['D'].width = 35
    ws.column_dimensions['E'].width = 9
    ws.column_dimensions['F'].width = 3
    ws.column_dimensions['G'].width = 3
    ws.column_dimensions['H'].width = 3
    ws.column_dimensions['I'].width = 3
    ws.column_dimensions['J'].width = 5
    ws.column_dimensions['K'].width = 9
    ws.column_dimensions['L'].width = 30
    ws.column_dimensions['M'].width = 18
    ws.column_dimensions['N'].width = 9
    ws.column_dimensions['O'].width = 4
    ws.column_dimensions['P'].width = 9
    ws.column_dimensions['Q'].width = 35
    ws.column_dimensions['R'].width = 9
    ws.column_dimensions['S'].width = 10
    ws.column_dimensions['T'].width = 9
    ws.column_dimensions['U'].width = 3
    ws.column_dimensions['V'].width = 4
    ws.column_dimensions['W'].width = 5
    ws.column_dimensions['X'].width = 4
    ws.column_dimensions['Y'].width = 9
    ws.column_dimensions['Z'].width = 3
    ws.column_dimensions['AA'].width = 4
    ws.column_dimensions['AB'].width = 5
    ws.column_dimensions['AC'].width = 4
    ws.column_dimensions['AD'].width = 9
    ws.column_dimensions['AE'].width = 3
    ws.column_dimensions['AF'].width = 4
    ws.column_dimensions['AG'].width = 5
    ws.column_dimensions['AH'].width = 9
    ws.column_dimensions['AI'].width = 10
    ws.column_dimensions['AJ'].width = 15
    ws.column_dimensions['AK'].width = 18
    ws.column_dimensions['AL'].width = 18
    ws.column_dimensions['AM'].width = 5
    ws.column_dimensions['AN'].width = 15
    ws.column_dimensions['AO'].width = 5
    ws.column_dimensions['AP'].width = 20
    ws.column_dimensions['AQ'].width = 9
    ws.column_dimensions['AR'].width = 20
    
# Guardar los anchos de las columnas que se van a agrupar
    grouped_widths = {
        'K': 9, 'L': 30, 'M': 18, 'N': 9, 'O': 4, 'P': 9, 'Q': 35, 'R': 9
    }
    
    # Agrupa las columnas de la K a la R para que se puedan ocultar y mostrar con un botón.
    ws.column_dimensions.group('K', 'R', hidden=True)

    # Restaurar explícitamente los anchos después del agrupamiento y configurar outline_level
    for col, width in grouped_widths.items():
        ws.column_dimensions[col].width = width
        ws.column_dimensions[col].outline_level = 1
    
    # linea de division
    ws.freeze_panes = 'S10'
    # Configuración del fondo y el borde
    # Definir el color usando formato aRGB (opacidad completa 'FF' + color RGB)
    fill = PatternFill(start_color='FF60D7E0', end_color='FF60D7E0', fill_type='solid')
    # Definir el color anaranjado usando formato aRGB
    orange_fill = PatternFill(start_color='FFE0A960', end_color='FFE0A960', fill_type='solid')
    # Definir los estilos para gris
    gray_fill = PatternFill(start_color='FFD3D3D3', end_color='FFD3D3D3', fill_type='solid')
    # Definir el estilo de color verde
    green_fill = PatternFill(start_color='FF60E0B3', end_color='FF60E0B3', fill_type='solid')
    # Definir el estilo de color amarillo
    yellow_fill = PatternFill(start_color='FFE0DE60', end_color='FFE0DE60', fill_type='solid')
    # Definir el estilo de color azul
    blue_fill = PatternFill(start_color='FF60A2E0', end_color='FF60A2E0', fill_type='solid')
    # Definir el estilo de color verde 2
    green_fill_2 = PatternFill(start_color='FF60E07E', end_color='FF60E07E', fill_type='solid')   
    
    green_font = Font(name='Arial', size=8, color='00FF00')  # Verde
    red_font = Font(name='Arial', size=8, color='FF0000')    # Rojo
    
    border = Border(left=Side(style='thin', color='00B0F0'),
                    right=Side(style='thin', color='00B0F0'),
                    top=Side(style='thin', color='00B0F0'),
                    bottom=Side(style='thin', color='00B0F0'))
    borde_plomo = Border(left=Side(style='thin', color='A9A9A9'), # Plomo
                    right=Side(style='thin', color='A9A9A9'), # Plomo
                    top=Side(style='thin', color='A9A9A9'), # Plomo
                    bottom=Side(style='thin', color='A9A9A9')) # Plomo
    
    # Configuración del fondo y el borde
    # Definir el color usando formato aRGB (opacidad completa 'FF' + color RGB)
    fill = PatternFill(start_color='FF60D7E0', end_color='FF60D7E0', fill_type='solid')
    # Definir el color anaranjado usando formato aRGB
    orange_fill = PatternFill(start_color='FFE0A960', end_color='FFE0A960', fill_type='solid')
    # Definir los estilos para gris
    gray_fill = PatternFill(start_color='FFD3D3D3', end_color='FFD3D3D3', fill_type='solid')
    # Definir el estilo de color verde
    green_fill = PatternFill(start_color='FF60E0B3', end_color='FF60E0B3', fill_type='solid')
    # Definir el estilo de color amarillo
    yellow_fill = PatternFill(start_color='FFE0DE60', end_color='FFE0DE60', fill_type='solid')
    # Definir el estilo de color azul
    blue_fill = PatternFill(start_color='FF60A2E0', end_color='FF60A2E0', fill_type='solid')
    # Definir el estilo de color verde 2
    green_fill_2 = PatternFill(start_color='FF60E07E', end_color='FF60E07E', fill_type='solid')   
    # Definir el estilo de relleno celeste
    celeste_fill = PatternFill(start_color='FF87CEEB', end_color='FF87CEEB', fill_type='solid')
    # Morado más claro
    morado_claro_fill = PatternFill(start_color='FFE9D8FF', end_color='FFE9D8FF', fill_type='solid')
    # Plomo más claro
    plomo_claro_fill = PatternFill(start_color='FFEDEDED', end_color='FFEDEDED', fill_type='solid')
    # Azul más claro
    azul_claro_fill = PatternFill(start_color='FFD8EFFA', end_color='FFD8EFFA', fill_type='solid')
    # Naranja más claro
    naranja_claro_fill = PatternFill(start_color='FFFFEBD8', end_color='FFFFEBD8', fill_type='solid')
    # Verde más claro
    verde_claro_fill = PatternFill(start_color='FFBDF7BD', end_color='FFBDF7BD', fill_type='solid')
    
    green_font = Font(name='Arial', size=8, color='00FF00')  # Verde
    red_font = Font(name='Arial', size=8, color='FF0000')    # Rojo
    
    border = Border(left=Side(style='thin', color='00B0F0'),
                    right=Side(style='thin', color='00B0F0'),
                    top=Side(style='thin', color='00B0F0'),
                    bottom=Side(style='thin', color='00B0F0'))
    borde_plomo = Border(left=Side(style='thin', color='A9A9A9'), # Plomo
                    right=Side(style='thin', color='A9A9A9'), # Plomo
                    top=Side(style='thin', color='A9A9A9'), # Plomo
                    bottom=Side(style='thin', color='A9A9A9')) # Plomo
    
    borde_plomo = Border(left=Side(style='thin', color='A9A9A9'), # Plomo
                    right=Side(style='thin', color='A9A9A9'), # Plomo
                    top=Side(style='thin', color='A9A9A9'), # Plomo
                    bottom=Side(style='thin', color='A9A9A9')) # Plomo
    
    border_negro = Border(left=Side(style='thin', color='000000'), # negro
                    right=Side(style='thin', color='000000'),
                    top=Side(style='thin', color='000000'), 
                    bottom=Side(style='thin', color='000000')) 
    
    # Merge cells 
    # numerador y denominador
    ws.merge_cells('B5:R5') 
    ws.merge_cells('S5:AR5')
    
    # CABECERA NOMBRES
    ws.merge_cells('B6:R6') 
    ws.merge_cells('S6:AC6')
    ws.merge_cells('AD6:AG6')
    ws.merge_cells('AH6:AR6')
        
    # Auxiliar HORIZONTAL
    ws.merge_cells('AH7:AH8')
    ws.merge_cells('AI7:AI8')
    
    # intervalo
    ws.merge_cells('B7:C7')
    ws.merge_cells('D7:J7')
    ws.merge_cells('K7:L7')
    ws.merge_cells('M7:O7')
    ws.merge_cells('P7:R7')
    ws.merge_cells('S7:X7')
    ws.merge_cells('Y7:AC7')
    ws.merge_cells('AD7:AG7')
    ws.merge_cells('AJ7:AR7')
    
    # COD HIS
    ws.merge_cells('B8:C8')
    ws.merge_cells('D8:R8')
    ws.merge_cells('S8:X8')
    ws.merge_cells('Y8:AC8')
    ws.merge_cells('AD8:AG8')
    ws.merge_cells('AJ8:AR8')

    # Combina cela
    ws['B5'] = 'META (DENOMINADOR)'
    ws['S5'] = 'AVANCE (NUMERADOR)'
    
    # CABECERA GRUPAL
    ws['B6']  = 'PADRON NOMINAL'
    ws['S6']  = 'DOSAJE DE HEMOBLOBINA'
    ws['AD6'] = 'SESION DEMOSTRATIVA'
    
    # INTERVALO
    #ws['S7'] = 'NUMERADOR PARCIAL'

    ws['D7'] = 'Niñas y niños que hayan cumplido entre 6 meses (180 dias) y 12 meses de edad (389 dias) del Padron Nominal, en el mes de medición'
    ws['K7'] = 'Establecimiento de Salud del Padron Nominal'
    ws['M7'] = 'Visita del Padron Nominal'
    ws['P7'] = 'Datos de la Madre del Padron Nominal'
    ws['S7'] = '1° Dosaje de Hemoglobina entre los 170 a 209 dias de edad'
    ws['Y7'] = '3° Dosaje de Hemoglobina entre los 350 y 389 dias de edad'
    ws['AD7'] = 'A partir del 6to mes de nacimiento, el niño cuenta con SD'
    ws['AJ7'] = 'Informacion Territorial del HIS MINSA'
    # CODIGO HIS
    
    ws['S8'] = 'DX = 85018 ó 85018.01 (Valor de Hemoglobina mayor o igual 10.5 g/dl)'
    ws['Y8'] = 'DX = 85018 ó 85018.01 (Valor de Hemoglobina mayor o igual 10.5 g/dl)'
    ws['AD8'] = 'DX = C0010 + TD = D + LAB = "ALI" + LAB = "GL" (opcional el registro del GL)'
    
    ### numerador y denominador     
    ws['B5'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['B5'].font = Font(name = 'Arial', size= 10, bold = True)
    ws['B5'].fill = gray_fill
    ws['B5'].border = border_negro
    
    ws['S5'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['S5'].font = Font(name = 'Arial', size= 10, bold = True)
    ws['S5'].fill = naranja_claro_fill
    ws['S5'].border = border_negro
    
    ### intervalo 
    ws['B6'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['B6'].font = Font(name = 'Arial', size= 10, bold = True)
    ws['B6'].fill = gray_fill
    ws['B6'].border = border_negro
    
    ws['S6'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['S6'].font = Font(name = 'Arial', size= 10, bold = True)
    ws['S6'].fill = gray_fill
    ws['S6'].border = border_negro
    
    
    ws['AD6'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['AD6'].font = Font(name = 'Arial', size= 7)
    ws['AD6'].fill = morado_claro_fill
    ws['AD6'].border = border_negro
    
    ws['AJ6'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['AJ6'].font = Font(name = 'Arial', size= 7)
    ws['AJ6'].fill = morado_claro_fill
    ws['AJ6'].border = border_negro
    
    #intervalos 
    ws['B7'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['B7'].font = Font(name = 'Arial', size= 7)
    ws['B7'].fill = naranja_claro_fill
    ws['B7'].border = border_negro
    
    ws['D7'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['D7'].font = Font(name = 'Arial', size= 7)
    ws['D7'].fill = plomo_claro_fill
    ws['D7'].border = border_negro
    
    ws['K7'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['K7'].font = Font(name = 'Arial', size= 7)
    ws['K7'].fill = plomo_claro_fill
    ws['K7'].border = border_negro
    
    ws['M7'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['M7'].font = Font(name = 'Arial', size= 7)
    ws['M7'].fill = plomo_claro_fill
    ws['M7'].border = border_negro
    
    ws['P7'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['P7'].font = Font(name = 'Arial', size= 7)
    ws['P7'].fill = plomo_claro_fill
    ws['P7'].border = border_negro
    
    ws['S7'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['S7'].font = Font(name = 'Arial', size= 7)
    ws['S7'].fill = plomo_claro_fill
    ws['S7'].border = border_negro
    
    ws['Y7'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['Y7'].font = Font(name = 'Arial', size= 7)
    ws['Y7'].fill = plomo_claro_fill
    ws['Y7'].border = border_negro
    
    ws['AD7'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['AD7'].font = Font(name = 'Arial', size= 7)
    ws['AD7'].fill = plomo_claro_fill
    ws['AD7'].border = border_negro
    
    ws['AH7'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['AH7'].font = Font(name = 'Arial', size= 7)
    ws['AH7'].fill = plomo_claro_fill
    ws['AH7'].border = border_negro
    
    ws['AI7'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['AI7'].font = Font(name = 'Arial', size= 7)
    ws['AI7'].fill = plomo_claro_fill
    ws['AI7'].border = border_negro
    
    ws['AJ7'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['AJ7'].font = Font(name = 'Arial', size= 7)
    ws['AJ7'].fill = plomo_claro_fill
    ws['AJ7'].border = border_negro
    
    # CODIGO HIS
    
    ws['B8'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['B8'].font = Font(name = 'Arial', size= 7)
    ws['B8'].fill = azul_claro_fill
    ws['B8'].border = border_negro
    
    ws['D8'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['D8'].font = Font(name = 'Arial', size= 7)
    ws['D8'].fill = azul_claro_fill
    ws['D8'].border = border_negro
    
    ws['K8'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['K8'].font = Font(name = 'Arial', size= 7)
    ws['K8'].fill = azul_claro_fill
    ws['K8'].border = border_negro
    
    ws['M8'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['M8'].font = Font(name = 'Arial', size= 7)
    ws['M8'].fill = azul_claro_fill
    ws['M8'].border = border_negro
    
    ws['P8'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['P8'].font = Font(name = 'Arial', size= 7)
    ws['P8'].fill = azul_claro_fill
    ws['P8'].border = border_negro
    
    ws['S8'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['S8'].font = Font(name = 'Arial', size= 7)
    ws['S8'].fill = azul_claro_fill
    ws['S8'].border = border_negro
    
    ws['Y8'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['Y8'].font = Font(name = 'Arial', size= 7)
    ws['Y8'].fill = azul_claro_fill
    ws['Y8'].border = border_negro
    
    ws['AD8'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['AD8'].font = Font(name = 'Arial', size= 7)
    ws['AD8'].fill = azul_claro_fill
    ws['AD8'].border = border_negro
    
    ws['AH8'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['AH8'].font = Font(name = 'Arial', size= 7)
    ws['AH8'].fill = azul_claro_fill
    ws['AH8'].border = border_negro
    
    ws['AI8'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['AI8'].font = Font(name = 'Arial', size= 7)
    ws['AI8'].fill = azul_claro_fill
    ws['AI8'].border = border_negro
    
    ws['AJ8'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['AJ8'].font = Font(name = 'Arial', size= 7)
    ws['AJ8'].fill = azul_claro_fill
    ws['AJ8'].border = border_negro
    
    ws['B7'].alignment = Alignment(horizontal= "center", vertical="center")
    ws['B7'].font = Font(name = 'Arial', size= 7, bold = True)
    ws['B7'].fill = plomo_claro_fill
    ws['B7'].border = border_negro
    ws['B7'] = 'INTERVALO'
    
    ws['B8'].alignment = Alignment(horizontal= "center", vertical="center")
    ws['B8'].font = Font(name = 'Arial', size= 7, bold = True)
    ws['B8'].fill = azul_claro_fill
    ws['B8'].border = border_negro
    ws['B8'] = 'COD HIS'
    
    ### BORDE DE CELDAS CONBINADAS

    # NUM y DEN
    inicio_columna = 'B'
    fin_columna = 'AR'
    fila = 5
    from openpyxl.utils import column_index_from_string
    # Convertir letras de columna a índices numéricos
    indice_inicio = column_index_from_string(inicio_columna)
    indice_fin = column_index_from_string(fin_columna)
    # Iterar sobre las columnas en el rango especificado
    for col in range(indice_inicio, indice_fin + 1):
        celda = ws.cell(row=fila, column=col)
        celda.border = border_negro
    
    # NUM y DEN
    inicio_columna = 'B'
    fin_columna = 'AR'
    fila = 6
    from openpyxl.utils import column_index_from_string
    # Convertir letras de columna a índices numéricos
    indice_inicio = column_index_from_string(inicio_columna)
    indice_fin = column_index_from_string(fin_columna)
    # Iterar sobre las columnas en el rango especificado
    for col in range(indice_inicio, indice_fin + 1):
        celda = ws.cell(row=fila, column=col)
        celda.border = border_negro
        
    # INTERVALO
    inicio_columna = 'B'
    fin_columna = 'AR'
    fila = 7
    from openpyxl.utils import column_index_from_string
    # Convertir letras de columna a índices numéricos
    indice_inicio = column_index_from_string(inicio_columna)
    indice_fin = column_index_from_string(fin_columna)
    # Iterar sobre las columnas en el rango especificado
    for col in range(indice_inicio, indice_fin + 1):
        celda = ws.cell(row=fila, column=col)
        celda.border = border_negro
        
    # CODIGO HIS 
    inicio_columna = 'B'
    fin_columna = 'AR'
    fila = 8
    from openpyxl.utils import column_index_from_string
    # Convertir letras de columna a índices numéricos
    indice_inicio = column_index_from_string(inicio_columna)
    indice_fin = column_index_from_string(fin_columna)
    # Iterar sobre las columnas en el rango especificado
    for col in range(indice_inicio, indice_fin + 1):
        celda = ws.cell(row=fila, column=col)
        celda.border = border_negro
    
    ##### imprimer fecha y hora del reporte
    fecha_hora_actual = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    nombre_usuario = getpass.getuser()

    # Obtener el usuario actualmente autenticado
    try:
        user = User.objects.get(is_active=True)
    except User.DoesNotExist:
        user = None
    except User.MultipleObjectsReturned:
        # Manejar el caso donde hay múltiples usuarios activos
        user = User.objects.filter(is_active=True).first()  # Por ejemplo, obtener el primero
    
    # Asignar fecha y hora a la celda A1
    ws['V1'].value = 'Fecha y Hora:'
    ws['W1'].value = fecha_hora_actual

    # Asignar nombre de usuario a la celda A2
    ws['V2'].value = 'Usuario:'
    ws['W2'].value = nombre_usuario
    
    # Formatear las etiquetas en negrita
    etiqueta_font = Font(name='Arial', size=8)
    ws['V1'].font = etiqueta_font
    ws['W1'].font = etiqueta_font
    ws['V2'].font = etiqueta_font
    ws['W2'].font = etiqueta_font

    # Alinear el texto
    ws['V1'].alignment = Alignment(horizontal="right", vertical="center")
    ws['W1'].alignment = Alignment(horizontal="left", vertical="center")
    ws['V2'].alignment = Alignment(horizontal="right", vertical="center")
    ws['W2'].alignment = Alignment(horizontal="left", vertical="center")
    
    ## crea titulo del reporte
    ws['B1'].alignment = Alignment(horizontal= "left", vertical="center")
    ws['B1'].font = Font(name = 'Arial', size= 7, bold = True)
    ws['B1'] = 'OFICINA DE TECNOLOGIAS DE LA INFORMACION'
    
    ws['B2'].alignment = Alignment(horizontal= "left", vertical="center")
    ws['B2'].font = Font(name = 'Arial', size= 7, bold = True)
    ws['B2'] = 'DIRECCION REGIONAL DE SALUD JUNIN'
    
    ws['B4'].alignment = Alignment(horizontal= "left", vertical="center")
    ws['B4'].font = Font(name = 'Arial', size= 12, bold = True)
    ws['B4'] = 'SEGUIMIENTO NOMINAL DEL INDICADOR. PORCENTAJE DE NIÑOS DE 6 A 12 MESES DE EDAD SIN ANEMIA'
    
    ws['B3'].alignment = Alignment(horizontal= "left", vertical="center")
    ws['B3'].font = Font(name = 'Arial', size= 7, bold = True, color='0000CC')
    ws['B3'] ='El usuario se compromete a mantener la confidencialidad de los datos personales que conozca como resultado del reporte realizado, cumpliendo con lo establecido en la Ley N° 29733 - Ley de Protección de Datos Personales y sus normas complementarias.'
        
    ws['B9'].alignment = Alignment(horizontal= "center", vertical="center")
    ws['B9'].font = Font(name = 'Arial', size= 8, bold = True)
    ws['B9'].fill = fill
    ws['B9'].border = border
    ws['B9'] = 'TD'
    
    ws['C9'].alignment = Alignment(horizontal= "center", vertical="center")
    ws['C9'].font = Font(name = 'Arial', size= 8, bold = True)
    ws['C9'].fill = fill
    ws['C9'].border = border
    ws['C9'] = 'NUM DOC'
    
    ws['D9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['D9'].font = Font(name = 'Arial', size= 8, bold = True)
    ws['D9'].fill = fill
    ws['D9'].border = border
    ws['D9'] = 'NOMBRE'      
    
    ws['E9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['E9'].font = Font(name = 'Arial', size= 8, bold = True)
    ws['E9'].fill = fill
    ws['E9'].border = border
    ws['E9'] = 'FECHA NAC' 
    
    ws['F9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['F9'].font = Font(name = 'Arial', size= 8, bold = True)
    ws['F9'].fill = fill
    ws['F9'].border = border
    ws['F9'] = 'ED A'     
    
    ws['G9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['G9'].font = Font(name = 'Arial', size= 8, bold = True)
    ws['G9'].fill = fill
    ws['G9'].border = border
    ws['G9'] = 'ED M'    
    
    ws['H9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['H9'].font = Font(name = 'Arial', size= 8, bold = True)
    ws['H9'].fill = fill
    ws['H9'].border = border
    ws['H9'] = 'ED D'    
    
    ws['I9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['I9'].font = Font(name = 'Arial', size= 8, bold = True)
    ws['I9'].fill = fill
    ws['I9'].border = border
    ws['I9'] = 'SEXO'    
    
    ws['J9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['J9'].font = Font(name = 'Arial', size= 8, bold = True)
    ws['J9'].fill = fill
    ws['J9'].border = border
    ws['J9'] = 'SEGURO'  
    
    ws['K9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['K9'].font = Font(name = 'Arial', size= 8, bold = True)
    ws['K9'].fill = green_fill_2
    ws['K9'].border = border
    ws['K9'] = 'COD EESS'  
    
    ws['L9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['L9'].font = Font(name = 'Arial', size= 8, bold = True)
    ws['L9'].fill = green_fill_2
    ws['L9'].border = border
    ws['L9'] = 'NOMBRE EESS'  
    
    ws['M9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['M9'].font = Font(name = 'Arial', size= 8, bold = True)
    ws['M9'].fill = green_fill_2
    ws['M9'].border = border
    ws['M9'] = 'FRECUENCIA'  
    
    ws['N9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['N9'].font = Font(name = 'Arial', size= 8, bold = True)
    ws['N9'].fill = green_fill_2
    ws['N9'].border = border
    ws['N9'] = 'VISITA'  
    
    ws['O9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['O9'].font = Font(name = 'Arial', size= 8, bold = True)
    ws['O9'].fill = green_fill_2
    ws['O9'].border = border
    ws['O9'] = 'ENC'  
    
    ws['P9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['P9'].font = Font(name = 'Arial', size= 8, bold = True)
    ws['P9'].fill = green_fill
    ws['P9'].border = border
    ws['P9'] = 'DNI MADRE'  
    
    ws['Q9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['Q9'].font = Font(name = 'Arial', size= 8, bold = True, color='000000')
    ws['Q9'].fill = green_fill
    ws['Q9'].border = border
    ws['Q9'] = 'MADRE'    
    
    ws['R9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['R9'].font = Font(name = 'Arial', size= 8, bold = True, color='000000')
    ws['R9'].fill = green_fill
    ws['R9'].border = border
    ws['R9'] = 'CELULAR' 
    
    ws['S9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['S9'].font = Font(name = 'Arial', size= 8, bold = True, color='000000')
    ws['S9'].fill = green_fill_2
    ws['S9'].border = border
    ws['S9'] = 'TAMIZAJE' 
    
    ws['T9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['T9'].font = Font(name = 'Arial', size= 8, bold = True, color='000000')
    ws['T9'].fill = yellow_fill
    ws['T9'].border = border
    ws['T9'] = '1° DOSAJE' 
    
    ws['U9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['U9'].font = Font(name = 'Arial', size= 8, bold = True, color='000000')
    ws['U9'].fill = yellow_fill   
    ws['U9'].border = border
    ws['U9'] = 'TD' 
    
    ws['V9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['V9'].font = Font(name = 'Arial', size= 7, bold = True, color='000000')
    ws['V9'].fill = yellow_fill
    ws['V9'].border = border
    ws['V9'] = 'LAB' 
    
    ws['W9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['W9'].font = Font(name = 'Arial', size= 7, bold = True, color='000000')
    ws['W9'].fill = yellow_fill
    ws['W9'].border = border
    ws['W9'] = 'VAL HB'   
    
    ws['X9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['X9'].font = Font(name = 'Arial', size= 8, bold = True, color='000000')
    ws['X9'].fill = yellow_fill
    ws['X9'].border = border
    ws['X9'] = 'IND' 
    
    ws['Y9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['Y9'].font = Font(name = 'Arial', size= 8, bold = True, color='000000')
    ws['Y9'].fill = green_fill
    ws['Y9'].border = border
    ws['Y9'] = '3° DOSAJE' 
    
    ws['Z9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['Z9'].font = Font(name = 'Arial', size= 8, bold = True, color='000000')
    ws['Z9'].fill = green_fill
    ws['Z9'].border = border
    ws['Z9'] = 'TD' 
    
    ws['AA9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['AA9'].font = Font(name = 'Arial', size= 8, bold = True, color='000000')
    ws['AA9'].fill = green_fill
    ws['AA9'].border = border
    ws['AA9'] = 'LAB' 
    
    ws['AB9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['AB9'].font = Font(name = 'Arial', size= 8, bold = True, color='000000')
    ws['AB9'].fill = green_fill
    ws['AB9'].border = border
    ws['AB9'] = 'VAL HB'     
    
    ws['AC9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['AC9'].font = Font(name = 'Arial', size= 8, bold = True, color='000000')
    ws['AC9'].fill = green_fill
    ws['AC9'].border = border
    ws['AC9'] = 'IND' 
    
    ws['AD9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['AD9'].font = Font(name = 'Arial', size= 8, bold = True, color='000000')
    ws['AD9'].fill = blue_fill
    ws['AD9'].border = border
    ws['AD9'] = 'SESION' 
    
    ws['AE9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['AE9'].font = Font(name = 'Arial', size= 8, bold = True, color='000000')
    ws['AE9'].fill = blue_fill
    ws['AE9'].border = border
    ws['AE9'] = 'TD' 
    
    ws['AF9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['AF9'].font = Font(name = 'Arial', size= 8, bold = True, color='000000')
    ws['AF9'].fill = blue_fill
    ws['AF9'].border = border
    ws['AF9'] = 'LAB' 
    
    ws['AG9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['AG9'].font = Font(name = 'Arial', size= 8, bold = True, color='000000')
    ws['AG9'].fill = blue_fill
    ws['AG9'].border = border
    ws['AG9'] = 'IND' 
    
    ws['AH9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['AH9'].font = Font(name = 'Arial', size= 8, bold = True, color='000000')
    ws['AH9'].fill = orange_fill
    ws['AH9'].border = border
    ws['AH9'] = 'MES EVAL' 
    
    ws['AI9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['AI9'].font = Font(name = 'Arial', size= 8, bold = True, color='000000')
    ws['AI9'].fill = orange_fill
    ws['AI9'].border = border
    ws['AI9'] = 'INDICADOR' 
    
    ws['AJ9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['AJ9'].font = Font(name = 'Arial', size= 8, bold = True, color='000000')
    ws['AJ9'].fill = orange_fill
    ws['AJ9'].border = border
    ws['AJ9'] = 'ZONA ' 
    
    ws['AK9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['AK9'].font = Font(name = 'Arial', size= 8, bold = True, color='000000')
    ws['AK9'].fill = orange_fill
    ws['AK9'].border = border
    ws['AK9'] = ' PROVINCIA' 
    
    ws['AL9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['AL9'].font = Font(name = 'Arial', size= 8, bold = True, color='000000')
    ws['AL9'].fill = orange_fill
    ws['AL9'].border = border
    ws['AL9'] = 'DISTRITO' 
    
    ws['AM9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['AM9'].font = Font(name = 'Arial', size= 8, bold = True, color='000000')
    ws['AM9'].fill = orange_fill
    ws['AM9'].border = border
    ws['AM9'] = 'COD RED' 
    
    ws['AN9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['AN9'].font = Font(name = 'Arial', size= 8, bold = True, color='000000')
    ws['AN9'].fill = orange_fill
    ws['AN9'].border = border
    ws['AN9'] = 'RED' 
    
    ws['AO9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['AO9'].font = Font(name = 'Arial', size= 8, bold = True, color='000000')
    ws['AO9'].fill = orange_fill
    ws['AO9'].border = border
    ws['AO9'] = 'COD MICRO' 
    
    ws['AP9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['AP9'].font = Font(name = 'Arial', size= 8, bold = True, color='000000')
    ws['AP9'].fill = orange_fill
    ws['AP9'].border = border
    ws['AP9'] = 'MICRORED' 
    
    ws['AQ9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['AQ9'].font = Font(name = 'Arial', size= 8, bold = True, color='000000')
    ws['AQ9'].fill = orange_fill
    ws['AQ9'].border = border
    ws['AQ9'] = 'COD EESS' 
    
    ws['AR9'].alignment = Alignment(horizontal= "center", vertical="center", wrap_text=True)
    ws['AR9'].font = Font(name = 'Arial', size= 8, bold = True, color='000000')
    ws['AR9'].fill = orange_fill
    ws['AR9'].border = border
    ws['AR9'] = 'ESTABLECIMIENTO DE SALUD' 
    
    
    # Definir estilos
    header_font = Font(name = 'Arial', size= 8, bold = True)
    centered_alignment = Alignment(horizontal='center')
    border = Border(left=Side(style='thin', color='A9A9A9'),
            right=Side(style='thin', color='A9A9A9'),
            top=Side(style='thin', color='A9A9A9'),
            bottom=Side(style='thin', color='A9A9A9'))
    header_fill = PatternFill(patternType='solid', fgColor='00B0F0')
    
    
    # Definir los caracteres especiales de check y X
    check_mark = '✓'  # Unicode para check
    x_mark = '✗'  # Unicode para X
    sub_cumple = 'CUMPLE'
    sub_no_cumple = 'NO CUMPLE'
    
    # Escribir datos
    for row, record in enumerate(results, start=10):
        for col, value in enumerate(record.values(), start=2):
            cell = ws.cell(row=row, column=col, value=value)

            # Alinear a la izquierda solo en las columnas específicas
            if col in [4, 12, 17, 38, 40, 42, 44]:
                cell.alignment = Alignment(horizontal='left')
            else:
                cell.alignment = Alignment(horizontal='center')

            # Aplicar color en la columna INDICADOR
            if col == 35:
                if isinstance(value, str):
                    value_upper = value.strip().upper()
                    if value_upper == "NO CUMPLE":
                        cell.fill = PatternFill(patternType='solid', fgColor='FF0000')  # Fondo rojo
                        cell.font = Font(name='Arial', size=8, bold = True,color="FFFFFF")  # Letra blanca
                    elif value_upper == "CUMPLE":
                        cell.fill = PatternFill(patternType='solid', fgColor='00FF00')  # Fondo verde
                        cell.font = Font(name='Arial', size=8,  bold = True,color="FFFFFF")  # Letra blanca
                    else:
                        cell.font = Font(name='Arial', size=8, bold = True)
                else:
                    cell.font = Font(name='Arial', size=8,  bold = True)
            
            # Aplicar color de letra SUB INDICADORES
            elif col in [19]:
                if value == 0:
                    cell.value = sub_no_cumple  # Insertar check
                    cell.font = Font(name='Arial', size=7, color="FF0000") 
                elif value == 1:
                    cell.value = sub_cumple # Insertar check
                    cell.font = Font(name='Arial', size=7, color="00B050")
                else:
                    cell.font = Font(name='Arial', size=7)
            # Fuente normal para otras columnas
            
            # Aplicar color de letra SUB GENERALIDADES
            elif col in [19]:
                if value == 0:
                    cell.value = sub_no_cumple  # Insertar check
                    cell.font = Font(name='Arial', size=7, color="FF0000") 
                    cell.fill = PatternFill(patternType='solid', fgColor='FFEDEDED')  
                    cell.fill = gray_fill # Letra roja
                elif value == 1:
                    cell.value = sub_cumple # Insertar check
                    cell.font = Font(name='Arial', size=7, color="00B050")
                    cell.fill = PatternFill(patternType='solid', fgColor='FFEDEDED') 
                    cell.fill = gray_fill# Letra verde
                else:
                    cell.font = Font(name='Arial', size=7)
            # Fuente normal para otras columnas
            else:
                cell.font = Font(name='Arial', size=8)  # Fuente normal para otras columnas
            
            # Aplicar caracteres especiales check y X
            if col in [24, 29, 33]:
                if value == 1:
                    cell.value = check_mark  # Insertar check
                    cell.font = Font(name='Arial', size=10, color='00B050')  # Letra verde
                elif value == 0:
                    cell.value = x_mark  # Insertar X
                    cell.font = Font(name='Arial', size=10, color='FF0000')  # Letra roja
                else:
                    cell.font = Font(name='Arial', size=8)  # Fuente normal si no es 1 o 0
            
            cell.border = border

