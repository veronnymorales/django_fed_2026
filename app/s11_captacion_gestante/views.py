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
from django.db.models import IntegerField
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
                mes_inicio='1',  # Siempre desde Enero,  # Usa el mes de inicio seleccionado
                mes_fin='12',      # Usa el mes de fin seleccionado
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


############################
## HTMX HIERARCHICAL TABLE
############################

def htmx_get_redes(request):
    """
    Vista HTMX para cargar los encabezados de Redes (nivel 1).
    Retorna HTML con cada Red como un grupo colapsable inicialmente cerrado.
    """
    try:
        # Obtener parámetros de filtros
        anio = request.GET.get('anio', DEFAULT_YEAR)
        mes_inicio = request.GET.get('mes_inicio', '1')
        mes_fin = request.GET.get('mes_fin', '12')
        provincia = request.GET.get('provincia', '')
        distrito = request.GET.get('distrito', '')
        red = request.GET.get('red', '')
        microred = request.GET.get('microred', '')
        establecimiento = request.GET.get('establecimiento', '')

        # Obtener datos detallados (necesitamos esto para agrupar por Red)
        resultados = obtener_variables_detallado(
            anio=anio,
            mes_inicio=mes_inicio,
            mes_fin=mes_fin,
            red=red,
            microred=microred,
            establecimiento=establecimiento,
            provincia=provincia,
            distrito=distrito
        )

        # Agrupar por Red
        redes_dict = {}
        for row in resultados:
            red_nombre = row.get('Red', 'Sin Red')
            red_codigo = row.get('Codigo_Red', '')
            
            if red_nombre not in redes_dict:
                redes_dict[red_nombre] = {
                    'codigo': red_codigo,
                    'count': 0
                }
            redes_dict[red_nombre]['count'] += 1

        # Ordenar redes alfabéticamente
        redes_sorted = sorted(redes_dict.items(), key=lambda x: x[0])

        context = {
            'redes': redes_sorted
        }

        return render(request, 's11_captacion_gestante/partials/htmx_redes.html', context)

    except Exception as e:
        logger.error(f"Error en htmx_get_redes: {e}", exc_info=True)
        return HttpResponse('<div class="alert alert-danger">Error al cargar las Redes</div>', status=500)


def htmx_get_microredes(request):
    """
    Vista HTMX para cargar MicroRedes dentro de una Red específica (nivel 2).
    Retorna HTML con cada MicroRed como un grupo colapsable.
    """
    try:
        # Obtener parámetros de filtros
        anio = request.GET.get('anio', DEFAULT_YEAR)
        mes_inicio = request.GET.get('mes_inicio', '1')
        mes_fin = request.GET.get('mes_fin', '12')
        provincia = request.GET.get('provincia', '')
        distrito = request.GET.get('distrito', '')
        red = request.GET.get('red', '')
        microred = request.GET.get('microred', '')
        establecimiento = request.GET.get('establecimiento', '')

        # Obtener datos detallados filtrados por Red
        resultados = obtener_variables_detallado(
            anio=anio,
            mes_inicio=mes_inicio,
            mes_fin=mes_fin,
            red=red,
            microred=microred,
            establecimiento=establecimiento,
            provincia=provincia,
            distrito=distrito
        )

        # Agrupar por MicroRed
        microredes_dict = {}
        for row in resultados:
            red_codigo = row.get('Codigo_Red', '')
            microred_nombre = row.get('MicroRed', 'Sin MicroRed')
            microred_codigo = row.get('Codigo_MicroRed', '')
            
            if microred_nombre not in microredes_dict:
                microredes_dict[microred_nombre] = {
                    'codigo': microred_codigo,
                    'red_codigo': red_codigo,
                    'count': 0
                }
            microredes_dict[microred_nombre]['count'] += 1

        # Ordenar microredes alfabéticamente
        microredes_sorted = sorted(microredes_dict.items(), key=lambda x: x[0])

        context = {
            'microredes': microredes_sorted,
            'red_codigo': red
        }

        return render(request, 's11_captacion_gestante/partials/htmx_microredes.html', context)

    except Exception as e:
        logger.error(f"Error en htmx_get_microredes: {e}", exc_info=True)
        return HttpResponse('<div class="alert alert-danger">Error al cargar las MicroRedes</div>', status=500)


def htmx_get_establecimientos(request):
    """
    Vista HTMX para cargar Establecimientos dentro de una MicroRed (nivel 3).
    Utiliza Great Tables para dar formato elegante a los datos tabulares.
    """
    try:
        # Obtener parámetros de filtros
        anio = request.GET.get('anio', DEFAULT_YEAR)
        mes_inicio = request.GET.get('mes_inicio', '1')
        mes_fin = request.GET.get('mes_fin', '12')
        provincia = request.GET.get('provincia', '')
        distrito = request.GET.get('distrito', '')
        red = request.GET.get('red', '')
        microred = request.GET.get('microred', '')
        establecimiento = request.GET.get('establecimiento', '')

        # Obtener datos detallados filtrados por MicroRed
        resultados = obtener_variables_detallado(
            anio=anio,
            mes_inicio=mes_inicio,
            mes_fin=mes_fin,
            red=red,
            microred=microred,
            establecimiento=establecimiento,
            provincia=provincia,
            distrito=distrito
        )

        # Agrupar por Establecimiento
        establecimientos_data = []
        for row in resultados:
            establecimiento_nombre = row.get('Nombre_Establecimiento', 'Sin Nombre')
            variable = row.get('den_variable', '')
            
            establecimientos_data.append({
                'Establecimiento': establecimiento_nombre,
                'Variable': variable,
                '1° Trim': row.get('num_1trim', 0),
                '1T %': f"{row.get('avance_1trim', 0.0):.1f}%",
                '2° Trim': row.get('num_2trim', 0),
                '2T %': f"{row.get('avance_2trim', 0.0):.1f}%",
                '3° Trim': row.get('num_3trim', 0),
                '3T %': f"{row.get('avance_3trim', 0.0):.1f}%",
            })

        context = {
            'establecimientos': establecimientos_data,
            'microred_codigo': microred,
            'red_codigo': red
        }

        return render(request, 's11_captacion_gestante/partials/htmx_establecimientos.html', context)

    except Exception as e:
        logger.error(f"Error en htmx_get_establecimientos: {e}", exc_info=True)
        return HttpResponse('<div class="alert alert-danger">Error al cargar los Establecimientos</div>', status=500)

