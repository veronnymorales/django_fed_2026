import logging
from typing import List, Dict, Optional

from django.db import connection
from base.models import MAESTRO_HIS_ESTABLECIMIENTO

# Initialize logger
logger = logging.getLogger(__name__)

# Constants
DEFAULT_VELOCIMETRO_DATA = {
    'orden': '', 
    'codigo': '',
    'codigo_red': '',
    'codigo_microred': '',
    'id_establecimiento': '',
    'red': '',
    'microred': '',
    'nombre_establecimiento': '',
    'num': 0,
    'den': 0,
    'avance': 0.0
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
def obtener_velocimetro_dashboard(
    anio: str,
    mes_inicio: Optional[str],
    mes_fin: Optional[str],
    red: Optional[str],
    microred: Optional[str],
    establecimiento: Optional[str]
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
        
    Returns:
        Lista con un diccionario conteniendo NUM, DEN y AVANCE.
        Retorna valores por defecto en caso de error o sin datos.
    """
    try:
        with connection.cursor() as cursor:
            # Llamar a la función almacenada con los parámetros en orden
            cursor.callproc('fn_obtener_velocimetro_fed_establecimiento_por_indicador', [
                anio,
                mes_inicio,
                mes_fin,
                red,
                microred,
                establecimiento
            ])
            
            # Obtener las filas resultantes
            rows = cursor.fetchall()
            
            if rows:
                resultados = []
                for row in rows:
                    if len(row) >= 11:
                        resultados.append({
                            'orden': str(row[0]) if row[0] is not None else '',
                            'codigo': str(row[1]) if row[1] is not None else '',
                            'codigo_red': str(row[2]) if row[2] is not None else '',
                            'codigo_microred': str(row[3]) if row[3] is not None else '',
                            'id_establecimiento': str(row[4]) if row[4] is not None else '',
                            'red':str(row[5]) if row[5] is not None else '',
                            'microred': str(row[6]) if row[6] is not None else '',
                            'nombre_establecimiento': str(row[7]) if row[7] is not None else '',
                            'num': row[8] if row[8] is not None else 0,
                            'den': row[9] if row[9] is not None else 0,
                            'avance': float(row[10]) if row[10] is not None else 0.0
                        })
                    else:
                        logger.warning(f"Una fila retornó {len(row)} columnas en lugar de 11, omitiendo...")
                
                if resultados:
                    logger.info(f"Se obtuvieron {len(resultados)} establecimientos para variables detallado")
                    return resultados
                else:
                    logger.warning("No se pudieron procesar filas válidas de variables detallado")
                    return [DEFAULT_VELOCIMETRO_DATA]
            else:
                # Sin datos en la tabla
                logger.warning("La consulta de variables detallado no retornó datos")
                return [DEFAULT_VELOCIMETRO_DATA]
                
    except Exception as e:
        logger.error(f"Error al obtener datos del velocímetro: {e}", exc_info=True)
        return [DEFAULT_VELOCIMETRO_DATA]