import logging
from typing import List, Dict, Optional

from django.db import connection
from base.models import MAESTRO_HIS_ESTABLECIMIENTO

# Initialize logger
logger = logging.getLogger(__name__)

# Constants
DEFAULT_VELOCIMETRO_DATA = {'NUM': 0, 'DEN': 0, 'AVANCE': 0.0}


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