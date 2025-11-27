import logging
from typing import List, Dict, Optional

from django.db import connection
from base.models import MAESTRO_HIS_ESTABLECIMIENTO

# Initialize logger
logger = logging.getLogger(__name__)

# Constants
DEFAULT_VELOCIMETRO_DATA = {'NUM': 0, 'DEN': 0, 'AVANCE': 0.0}

DEFAULT_GRAFICO_MENSUALIZADO_DATA = {
    'num_1': 0, 'den_1': 0, 'cob_1': 0.0,
    'num_2': 0, 'den_2': 0, 'cob_2': 0.0,
    'num_3': 0, 'den_3': 0, 'cob_3': 0.0,
    'num_4': 0, 'den_4': 0, 'cob_4': 0.0,
    'num_5': 0, 'den_5': 0, 'cob_5': 0.0,
    'num_6': 0, 'den_6': 0, 'cob_6': 0.0,
    'num_7': 0, 'den_7': 0, 'cob_7':0.0,
    'num_8': 0, 'den_8': 0, 'cob_8': 0.0,
    'num_9': 0, 'den_9': 0, 'cob_9': 0.0,
    'num_10': 0, 'den_10': 0, 'cob_10': 0.0,
    'num_11': 0, 'den_11': 0, 'cob_11': 0.0,
    'num_12': 0, 'den_12': 0, 'cob_12': 0.0
}

DEFAULT_VARIABLES_DATA = {
    'den_variable': 0,
    'num_1trim': 0,
    'avance_1trim': 0.0,
    'num_2trim': 0,
    'avance_2trim': 0.0,
    'num_3trim': 0,
    'avance_3trim': 0.0
}

DEFAULT_VARIABLES_DETALLADO_DATA = {
    'd_anio': '',
    'd_mes': '',
    'd_codigo_red': '',
    'd_red': '',
    'd_codigo_microred': '',
    'd_microred': '',
    'd_codigo_unico': '',
    'd_id_establecimiento': '',
    'd_nombre_establecimiento': '',
    'd_ubigueo_establecimiento': '',
    'd_den_variable': 0,
    'd_num_1trim': 0,
    'd_avance_1trim': 0.0,
    'd_num_2trim': 0,
    'd_avance_2trim': 0.0,
    'd_num_3trim': 0,
    'd_avance_3trim': 0.0
}

DEFAULT_VARIABLES_GRAFICO_REDES = {
    'red_r': '',
    'den_r': 0,
    'num_r': 0,
    'avance_r': 0.0,
    'brecha_r': 0
}

DEFAULT_VARIABLES_GRAFICO_MICRORED = {
    'microred_mr': '',
    'den_mr': 0,
    'num_mr': 0,
    'avance_mr': 0.0,
    'brecha_mr': 0
}

DEFAULT_VARIABLES_GRAFICO_ESTABLECIMIENTOS = {
    'establecimiento_e': '',
    'den_e': 0,
    'num_e': 0,
    'avance_e': 0.0,
    'brecha_e': 0
}

def obtener_distritos(provincia: str) -> List[Dict[str, str]]:
    """
    Obtiene la lista de distritos para una provincia específica.
    Args:
        provincia: Nombre de la provincia
    Returns:
        Lista de diccionarios con los distritos
    """
    distritos = (
        MAESTRO_HIS_ESTABLECIMIENTO.objects
        .filter(Provincia=provincia)
        .values('Distrito')
        .distinct()
        .order_by('Distrito')
    )
    return list(distritos)

## velocimetro
def obtener_velocimetro(
    anio: str,
    mes_inicio: Optional[str],
    mes_fin: Optional[str],
    red: Optional[str],
    microred: Optional[str],
    establecimiento: Optional[str],
    provincia: Optional[str],
    distrito: Optional[str]
) -> List[Dict[str, float]]:
    """
    Obtiene los datos del velocímetro de captación de gestantes.
    
    Llama a la función almacenada 'fn_obtener_velocimetro' en PostgreSQL
    para obtener el numerador, denominador y porcentaje de avance.
    
    Args:
        anio: Año de consulta
        mes_inicio: Mes de inicio del rango
        mes_fin: Mes fin del rango
        red: Red de salud (opcional)
        microred: Microred de salud (opcional)
        establecimiento: Establecimiento de salud (opcional)
        provincia: Provincia (opcional)
        distrito: Distrito (opcional)
        
    Returns:
        Lista con un diccionario conteniendo NUM, DEN y AVANCE.
        Retorna valores por defecto en caso de error o sin datos.
    """
    try:
        with connection.cursor() as cursor:
            # Llamar a la función almacenada con los parámetros en orden
            cursor.callproc('fn_obtener_velocimetro', [
                anio,
                mes_inicio,
                mes_fin,
                red,
                microred,
                establecimiento,
                provincia,
                distrito
            ])
            
            # Obtener la fila resultante (siempre es 1 fila debido a la agregación)
            row = cursor.fetchone()
            
            if row:
                # Construir respuesta: row[0]=NUM, row[1]=DEN, row[2]=AVANCE
                return [{
                    'NUM': row[0] if row[0] is not None else 0,
                    'DEN': row[1] if row[1] is not None else 0,
                    'AVANCE': float(row[2]) if row[2] is not None else 0.0
                }]
            else:
                # Sin datos en la tabla
                logger.warning("La consulta de velocímetro no retornó datos")
                return [DEFAULT_VELOCIMETRO_DATA]
                
    except Exception as e:
        logger.error(f"Error al obtener datos del velocímetro: {e}", exc_info=True)
        return [DEFAULT_VELOCIMETRO_DATA]

## grafico mensualizado
def obtener_grafico_mensual(
    anio: str,
    mes_inicio: Optional[str],
    mes_fin: Optional[str],
    red: Optional[str],
    microred: Optional[str],
    establecimiento: Optional[str],
    provincia: Optional[str],
    distrito: Optional[str]
) -> List[Dict[str, float]]:
    """
    Obtiene los datos del grafico mensual de captación de gestantes.
    
    Llama a la función almacenada 'fn_obtener_grafico_mensualizado' en PostgreSQL
    para obtener el numerador, denominador y porcentaje de avance mensual.
    
    Args:
        anio: Año de consulta
        mes_inicio: Mes de inicio del rango
        mes_fin: Mes fin del rango
        red: Red de salud (opcional)
        microred: Microred de salud (opcional)
        establecimiento: Establecimiento de salud (opcional)
        provincia: Provincia (opcional)
        distrito: Distrito (opcional)
        
    Returns:
        Lista con un diccionario conteniendo num_1-12, den_1-12, cob_1-12.
        Retorna valores por defecto en caso de error o sin datos.
    """
    try:
        with connection.cursor() as cursor:
            # Llamar a la función almacenada con los parámetros en orden
            cursor.callproc('fn_grafico_mensualizado', [
                anio,
                mes_inicio,
                mes_fin,
                red,
                microred,
                establecimiento,
                provincia,
                distrito
            ])
            
            # Obtener la fila resultante
            row = cursor.fetchone()
            
            if row and len(row) >= 36:
                # La función almacenada devuelve 36 columnas:
                # row[0-11]: num_1 a num_12
                # row[12-23]: den_1 a den_12
                # row[24-35]: cob_1 a cob_12
                return [{
                    'num_1': int(row[0]) if row[0] is not None else 0,
                    'den_1': int(row[1]) if row[1] is not None else 0,
                    'cob_1': float(row[2]) if row[2] is not None else 0.0,
                    'num_2': int(row[3]) if row[3] is not None else 0,
                    'den_2': int(row[4]) if row[4] is not None else 0,
                    'cob_2': float(row[5]) if row[5] is not None else 0.0,
                    'num_3': int(row[6]) if row[6] is not None else 0,
                    'den_3': int(row[7]) if row[7] is not None else 0,
                    'cob_3': float(row[8]) if row[8] is not None else 0.0,
                    'num_4': int(row[9]) if row[9] is not None else 0,
                    'den_4': int(row[10]) if row[10] is not None else 0,
                    'cob_4': float(row[11]) if row[11] is not None else 0.0,
                    'num_5': int(row[12]) if row[12] is not None else 0,
                    'den_5': int(row[13]) if row[13] is not None else 0,
                    'cob_5': float(row[14]) if row[14] is not None else 0.0,
                    'num_6': int(row[15]) if row[15] is not None else 0,
                    'den_6': int(row[16]) if row[16] is not None else 0,
                    'cob_6': float(row[17]) if row[17] is not None else 0.0,
                    'num_7': int(row[18]) if row[18] is not None else 0,
                    'den_7': int(row[19]) if row[19] is not None else 0,
                    'cob_7': float(row[20]) if row[20] is not None else 0.0,
                    'num_8': int(row[21]) if row[21] is not None else 0,
                    'den_8': int(row[22]) if row[22] is not None else 0,
                    'cob_8': float(row[23]) if row[23] is not None else 0.0,
                    'num_9': int(row[24]) if row[24] is not None else 0,
                    'den_9': int(row[25]) if row[25] is not None else 0,
                    'cob_9': float(row[26]) if row[26] is not None else 0.0,
                    'num_10': int(row[27]) if row[27] is not None else 0,
                    'den_10': int(row[28]) if row[28] is not None else 0,
                    'cob_10': float(row[29]) if row[29] is not None else 0.0,
                    'num_11': int(row[30]) if row[30] is not None else 0,
                    'den_11': int(row[31]) if row[31] is not None else 0,
                    'cob_11': float(row[32]) if row[32] is not None else 0.0,
                    'num_12': int(row[33]) if row[33] is not None else 0,
                    'den_12': int(row[34]) if row[34] is not None else 0,
                    'cob_12': float(row[35]) if row[35] is not None else 0.0
                }]
            else:
                # Sin datos en la tabla o número incorrecto de columnas
                if row:
                    logger.warning(f"La consulta de grafico mensualizado retornó {len(row)} columnas en lugar de 36")
                else:
                    logger.warning("La consulta de grafico mensualizado no retornó datos")
                return [DEFAULT_GRAFICO_MENSUALIZADO_DATA]
                
    except Exception as e:
        logger.error(f"Error al obtener datos del grafico mensualizado: {e}", exc_info=True)
        return [DEFAULT_GRAFICO_MENSUALIZADO_DATA]

## grafico variables
def obtener_variables(
    anio: str,
    mes_inicio: Optional[str],
    mes_fin: Optional[str],
    red: Optional[str],
    microred: Optional[str],
    establecimiento: Optional[str],
    provincia: Optional[str],
    distrito: Optional[str]
) -> List[Dict[str, float]]:
    """
    Obtiene los datos agregados de variables de captación de gestantes.
    
    Llama a la función almacenada 'fn_obtener_variables' en PostgreSQL
    para obtener el numerador, denominador y porcentaje de avance por trimestre (agregado).
    
    Args:
        anio: Año de consulta
        mes_inicio: Mes de inicio del rango
        mes_fin: Mes fin del rango
        red: Red de salud (opcional)
        microred: Microred de salud (opcional)
        establecimiento: Establecimiento de salud (opcional)
        provincia: Provincia (opcional)
        distrito: Distrito (opcional)
        
    Returns:
        Lista con un diccionario conteniendo den_variable, num_1trim-3trim, avance_1trim-3trim.
        Retorna valores por defecto en caso de error o sin datos.
    """
    try:
        with connection.cursor() as cursor:
            # Llamar a la función almacenada con los parámetros en orden
            cursor.callproc('fn_obtener_variables', [
                anio,
                mes_inicio,
                mes_fin,
                red,
                microred,
                establecimiento,
                provincia,
                distrito
            ])
            
            # Obtener la fila resultante
            row = cursor.fetchone()
            
            if row and len(row) >= 7:
                return [{
                    'den_variable': int(row[0]) if row[0] is not None else 0,
                    'num_1trim': int(row[1]) if row[1] is not None else 0,
                    'avance_1trim': float(row[2]) if row[2] is not None else 0.0,
                    'num_2trim': int(row[3]) if row[3] is not None else 0,
                    'avance_2trim': float(row[4]) if row[4] is not None else 0.0,
                    'num_3trim': int(row[5]) if row[5] is not None else 0,
                    'avance_3trim': float(row[6]) if row[6] is not None else 0.0
                }]
            else:
                # Sin datos en la tabla o número incorrecto de columnas
                if row:
                    logger.warning(f"La consulta de variables retornó {len(row)} columnas en lugar de 7")
                else:
                    logger.warning("La consulta de variables no retornó datos")
                return [DEFAULT_VARIABLES_DATA]
                
    except Exception as e:
        logger.error(f"Error al obtener datos de variables: {e}", exc_info=True)
        return [DEFAULT_VARIABLES_DATA]

## tabla variables detallado
def obtener_variables_detallado(
    anio: str,
    mes_inicio: Optional[str],
    mes_fin: Optional[str],
    red: Optional[str],
    microred: Optional[str],
    establecimiento: Optional[str],
    provincia: Optional[str],
    distrito: Optional[str]
) -> List[Dict[str, float]]:
    """
    Obtiene los datos detallados de variables de captación de gestantes.
    
    Llama a la función almacenada 'fn_obtener_variables_detallado' en PostgreSQL
    para obtener información detallada por establecimiento.
    
    Args:
        anio: Año de consulta
        mes_inicio: Mes de inicio del rango
        mes_fin: Mes fin del rango
        red: Red de salud (opcional)
        microred: Microred de salud (opcional)
        establecimiento: Establecimiento de salud (opcional)
        provincia: Provincia (opcional)
        distrito: Distrito (opcional)
        
    Returns:
        Lista con diccionarios conteniendo información detallada por establecimiento.
        Retorna valores por defecto en caso de error o sin datos.
    """
    try:
        with connection.cursor() as cursor:
            # Llamar a la función almacenada con los parámetros en orden
            cursor.callproc('fn_obtener_variables_detallado', [
                anio,
                mes_inicio,
                mes_fin,
                red,
                microred,
                establecimiento,
                provincia,
                distrito
            ])
            
            # Obtener TODAS las filas resultantes (todos los establecimientos)
            rows = cursor.fetchall()
            
            if rows:
                resultados = []
                for row in rows:
                    if len(row) >= 17:
                        resultados.append({
                            'd_anio': str(row[0]) if row[0] is not None else '',
                            'd_mes': str(row[1]) if row[1] is not None else '',
                            'd_codigo_red': str(row[2]) if row[2] is not None else '',
                            'd_red': str(row[3]) if row[3] is not None else '',
                            'd_codigo_microred': str(row[4]) if row[4] is not None else '',
                            'd_microred': str(row[5]) if row[5] is not None else '',
                            'd_codigo_unico': str(row[6]) if row[6] is not None else '',
                            'd_id_establecimiento': str(row[7]) if row[7] is not None else '',
                            'd_nombre_establecimiento': str(row[8]) if row[8] is not None else '',
                            'd_ubigueo_establecimiento': str(row[9]) if row[9] is not None else '',
                            'd_den_variable': int(row[10]) if row[10] is not None else 0,
                            'd_num_1trim': int(row[11]) if row[11] is not None else 0,
                            'd_avance_1trim': float(row[12]) if row[12] is not None else 0.0,
                            'd_num_2trim': int(row[13]) if row[13] is not None else 0,
                            'd_avance_2trim': float(row[14]) if row[14] is not None else 0.0,
                            'd_num_3trim': int(row[15]) if row[15] is not None else 0,
                            'd_avance_3trim': float(row[16]) if row[16] is not None else 0.0
                        })
                    else:
                        logger.warning(f"Una fila retornó {len(row)} columnas en lugar de 17, omitiendo...")
                
                if resultados:
                    logger.info(f"Se obtuvieron {len(resultados)} establecimientos para variables detallado")
                    return resultados
                else:
                    logger.warning("No se pudieron procesar filas válidas de variables detallado")
                    return [DEFAULT_VARIABLES_DETALLADO_DATA]
            else:
                # Sin datos en la tabla
                logger.warning("La consulta de variables detallado no retornó datos")
                return [DEFAULT_VARIABLES_DETALLADO_DATA]
                
    except Exception as e:
        logger.error(f"Error al obtener datos de variables detallado: {e}", exc_info=True)
        return [DEFAULT_VARIABLES_DETALLADO_DATA]

## grafico ranking redes de salud
def obtener_grafico_por_redes(
    anio: str,
    mes_inicio: Optional[str],
    mes_fin: Optional[str],
    red: Optional[str],
    microred: Optional[str],
    establecimiento: Optional[str],
    provincia: Optional[str],
    distrito: Optional[str]
) -> List[Dict[str, float]]:
    """
    Obtiene los datos detallados de ranking de redes de salud.
    
    Llama a la función almacenada 'fn_grafico_redes' en PostgreSQL
    para obtener información detallada por establecimiento.
    
    Args:
        anio: Año de consulta
        mes_inicio: Mes de inicio del rango
        mes_fin: Mes fin del rango
        red: Red de salud (opcional)
        microred: Microred de salud (opcional)
        establecimiento: Establecimiento de salud (opcional)
        provincia: Provincia (opcional)
        distrito: Distrito (opcional)
        
    Returns:
        Lista con diccionarios conteniendo información detallada por establecimiento.
        Retorna valores por defecto en caso de error o sin datos.
    """
    try:
        with connection.cursor() as cursor:
            # Llamar a la función almacenada con los parámetros en orden
            cursor.callproc('fn_grafico_redes', [
                anio,
                mes_inicio,
                mes_fin,
                red,
                microred,
                establecimiento,
                provincia,
                distrito
            ])
            
            # Obtener TODAS las filas resultantes (todos los establecimientos)
            rows = cursor.fetchall()
            
            if rows:
                resultados = []
                for row in rows:
                    if len(row) >= 5:
                        resultados.append({
                            'red_r': str(row[0]) if row[0] is not None else '',
                            'den_r': int(row[1]) if row[1] is not None else 0,
                            'num_r': int(row[2]) if row[2] is not None else 0,
                            'avance_r': float(row[3]) if row[3] is not None else 0.0,
                            'brecha_r': int(row[4]) if row[4] is not None else 0,
                        })
                    else:
                        logger.warning(f"Una fila retornó {len(row)} columnas en lugar de 5, omitiendo...")
                
                if resultados:
                    logger.info(f"Se obtuvieron {len(resultados)} establecimientos para variables detallado")
                    return resultados
                else:
                    logger.warning("No se pudieron procesar filas válidas de variables detallado")
                    return [DEFAULT_VARIABLES_GRAFICO_REDES]
            else:
                # Sin datos en la tabla
                logger.warning("La consulta de variables detallado no retornó datos")
                return [DEFAULT_VARIABLES_GRAFICO_REDES]
                
    except Exception as e:
        logger.error(f"Error al obtener datos de variables detallado: {e}", exc_info=True)
        return [DEFAULT_VARIABLES_GRAFICO_REDES]

## grafico ranking microredes de salud
def obtener_grafico_por_microredes(
    anio: str,
    mes_inicio: Optional[str],
    mes_fin: Optional[str],
    red: Optional[str],
    microred: Optional[str],
    establecimiento: Optional[str],
    provincia: Optional[str],
    distrito: Optional[str]
) -> List[Dict[str, float]]:
    """
    Obtiene los datos detallados de ranking de microredes de salud.
    
    Llama a la función almacenada 'fn_grafico_microredes' en PostgreSQL
    para obtener información detallada por establecimiento.
    
    Args:
        anio: Año de consulta
        mes_inicio: Mes de inicio del rango
        mes_fin: Mes fin del rango
        red: Red de salud (opcional)
        microred: Microred de salud (opcional)
        establecimiento: Establecimiento de salud (opcional)
        provincia: Provincia (opcional)
        distrito: Distrito (opcional)
        
    Returns:
        Lista con diccionarios conteniendo información detallada por establecimiento.
        Retorna valores por defecto en caso de error o sin datos.
    """
    try:
        with connection.cursor() as cursor:
            # Llamar a la función almacenada con los parámetros en orden
            cursor.callproc('fn_grafico_microredes', [
                anio,
                mes_inicio,
                mes_fin,
                red,
                microred,
                establecimiento,
                provincia,
                distrito
            ])
            
            # Obtener TODAS las filas resultantes (todos los establecimientos)
            rows = cursor.fetchall()
            
            if rows:
                resultados = []
                for row in rows:
                    if len(row) >= 5:
                        resultados.append({
                            'microred_mr': str(row[0]) if row[0] is not None else '',
                            'den_mr': int(row[1]) if row[1] is not None else 0,
                            'num_mr': int(row[2]) if row[2] is not None else 0,
                            'avance_mr': float(row[3]) if row[3] is not None else 0.0,
                            'brecha_mr': int(row[4]) if row[4] is not None else 0,
                        })
                    else:
                        logger.warning(f"Una fila retornó {len(row)} columnas en lugar de 5, omitiendo...")
                
                if resultados:
                    logger.info(f"Se obtuvieron {len(resultados)} establecimientos para variables detallado")
                    return resultados
                else:
                    logger.warning("No se pudieron procesar filas válidas de variables detallado")
                    return [DEFAULT_VARIABLES_GRAFICO_MICRORED]
            else:
                # Sin datos en la tabla
                logger.warning("La consulta de variables detallado no retornó datos")
                return [DEFAULT_VARIABLES_GRAFICO_MICRORED]
                
    except Exception as e:
        logger.error(f"Error al obtener datos de variables detallado: {e}", exc_info=True)
        return [DEFAULT_VARIABLES_GRAFICO_MICRORED]

## grafico ranking establecimientos de salud
def obtener_grafico_por_establecimientos(
    anio: str,
    mes_inicio: Optional[str],
    mes_fin: Optional[str],
    red: Optional[str],
    microred: Optional[str],
    establecimiento: Optional[str],
    provincia: Optional[str],
    distrito: Optional[str]
) -> List[Dict[str, float]]:
    """
    Obtiene los datos detallados de ranking de establecimientos de salud.
    
    Llama a la función almacenada 'fn_grafico_establecimientos' en PostgreSQL
    para obtener información detallada por establecimiento.
    
    Args:
        anio: Año de consulta
        mes_inicio: Mes de inicio del rango
        mes_fin: Mes fin del rango
        red: Red de salud (opcional)
        microred: Microred de salud (opcional)
        establecimiento: Establecimiento de salud (opcional)
        provincia: Provincia (opcional)
        distrito: Distrito (opcional)
        
    Returns:
        Lista con diccionarios conteniendo información detallada por establecimiento.
        Retorna valores por defecto en caso de error o sin datos.
    """
    try:
        with connection.cursor() as cursor:
            # Llamar a la función almacenada con los parámetros en orden
            cursor.callproc('fn_grafico_establecimientos', [
                anio,
                mes_inicio,
                mes_fin,
                red,
                microred,
                establecimiento,
                provincia,
                distrito
            ])
            
            # Obtener TODAS las filas resultantes (todos los establecimientos)
            rows = cursor.fetchall()
            
            if rows:
                resultados = []
                for row in rows:
                    if len(row) >= 5:
                        resultados.append({
                            'establecimiento_e': str(row[0]) if row[0] is not None else '',
                            'den_e': int(row[1]) if row[1] is not None else 0,
                            'num_e': int(row[2]) if row[2] is not None else 0,
                            'avance_e': float(row[3]) if row[3] is not None else 0.0,
                            'brecha_e': int(row[4]) if row[4] is not None else 0,
                        })
                    else:
                        logger.warning(f"Una fila retornó {len(row)} columnas en lugar de 5, omitiendo...")
                
                if resultados:
                    logger.info(f"Se obtuvieron {len(resultados)} establecimientos para variables detallado")
                    return resultados
                else:
                    logger.warning("No se pudieron procesar filas válidas de variables detallado")
                    return [DEFAULT_VARIABLES_GRAFICO_ESTABLECIMIENTOS]
            else:
                # Sin datos en la tabla
                logger.warning("La consulta de variables detallado no retornó datos")
                return [DEFAULT_VARIABLES_GRAFICO_ESTABLECIMIENTOS]
                
    except Exception as e:
        logger.error(f"Error al obtener datos de variables detallado: {e}", exc_info=True)
        return [DEFAULT_VARIABLES_GRAFICO_ESTABLECIMIENTOS]
