# Integración de Great Tables en Django

## Resumen de Cambios

Se ha integrado exitosamente **Great Tables** (biblioteca de Python) en lugar de DataTables (JavaScript) para el componente de tabla de variables detallado.

## Archivos Modificados

### 1. **Nuevos Archivos Creados**

#### `s11_captacion_gestante/table_utils.py`

- Funciones de utilidad para generar tablas con Great Tables
- `generate_variables_detallado_table_grouped()`: Genera tabla HTML con agrupación por Red y MicroRed
- Incluye estilos personalizados de Bootstrap
- Formateo automático de números y porcentajes

### 2. **Archivos Modificados**

#### `s11_captacion_gestante/views.py`

**Línea 27**: Agregado import de `generate_variables_detallado_table_grouped`

**Líneas 508-515**: Modificado procesamiento de datos

```python
# Procesar datos de variables detallado
processed_variables_detallado = process_variables_detallado(resultados_variables_detallado)

# Generar HTML de la tabla usando Great Tables
tabla_html = generate_variables_detallado_table_grouped(processed_variables_detallado)

# Agregar el HTML de la tabla a la respuesta JSON
data = {
   ...
   'tabla_variables_detallado_html': tabla_html  # ← Nuevo campo
}
```

#### `templates/s11_captacion_gestante/components/chart/table_variables_detallado.html`

**Cambios completos**:

- ❌ Eliminado todo el código de DataTables (294 líneas → 60 líneas)
- ❌ Removido JavaScript complejo de agrupación y colapso
- ❌ Eliminada dependencia de RowGroup plugin
- ✅ Implementado renderizado simple con HTML del backend
- ✅ Mantenidos estilos CSS para personalización de Great Tables

```javascript
// Antes: ~250 líneas de JavaScript con DataTables
// Ahora: ~15 líneas simples
window.renderTablaVariablesDetallado = function (data, params) {
  const container = document.getElementById(
    "detalle-avance-variables-detallado-container"
  );

  if (data.tabla_variables_detallado_html) {
    container.innerHTML = data.tabla_variables_detallado_html;
  }
};
```

#### `requirements.txt`

Agregadas nuevas dependencias:

```
great-tables==0.20.0
pandas==2.2.3
```

## Ventajas de Great Tables vs DataTables

### ✅ Ventajas

1. **Backend Rendering**:

   - La tabla se genera en el servidor (Python)
   - No requiere procesamiento pesado en el navegador
   - Mejor rendimiento inicial

2. **Código más Limpio**:

   - De 294 líneas → 60 líneas en el template
   - Sin dependencias de jQuery adicionales
   - Mantenimiento más fácil

3. **Estilos Consistentes**:

   - Great Tables integra bien con Bootstrap
   - Estilos personalizables usando Python
   - No requiere CSS/JS externo para funcionalidades básicas

4. **Agrupación Jerárquica**:

   - Agrupación nativa por Red → MicroRed
   - Formato: "RED_NAME → MICRORED_NAME"
   - Estilos diferenciados para cada nivel

5. **Formateo Automático**:
   - Números con decimales controlados
   - Porcentajes formateados automáticamente
   - Alineación correcta de columnas

### ⚠️ Consideraciones

1. **Interactividad**:

   - DataTables tenía colapsar/expandir grupos
   - Great Tables muestra todos los datos expandidos
   - Para interactividad avanzada, considerar agregar JavaScript adicional

2. **Paginación**:
   - DataTables tenía paginación del lado del cliente
   - Great Tables muestra todos los datos
   - Si hay muchos registros, considerar paginación del backend

## Características Implementadas

### Agrupación

- ✅ Agrupación por Red y MicroRed
- ✅ Encabezados de grupo con estilos personalizados (azul #007bff)
- ✅ Formato: "RED_NAME → MICRORED_NAME"

### Formateo

- ✅ Porcentajes con 1 decimal
- ✅ Números sin decimales para trimestres
- ✅ Alineación a la derecha para números
- ✅ Color azul (#0066cc) y negrita para porcentajes

### Estilos

- ✅ Encabezados oscuros (#343a40) con texto blanco
- ✅ Filas alternas con fondo gris claro (#f8f9fa)
- ✅ Bordes consistentes
- ✅ Card de Bootstrap con header azul
- ✅ Badge con conteo de registros

### Otros

- ✅ Título con icono de FontAwesome
- ✅ Subtítulo descriptivo
- ✅ Responsive (table-responsive)
- ✅ Manejo de datos vacíos

## Uso

La tabla se renderiza automáticamente cuando se aplican filtros. No se requiere interacción adicional del usuario.

```javascript
// El flujo es:
1. Usuario aplica filtros
2. AJAX request a Django
3. Django genera HTML con Great Tables
4. Frontend inserta el HTML en el contenedor
5. Tabla mostrada ✅
```

## Próximos Pasos (Opcional)

Si deseas agregar más interactividad:

1. **Colapsar/Expandir Grupos**:

   - Agregar JavaScript para ocultar/mostrar filas de grupos
   - Usar atributos data-\* para identificar grupos

2. **Búsqueda del Lado del Cliente**:

   - Implementar filtrado simple con JavaScript
   - Filtrar por establecimiento, red, o microred

3. **Exportar a Excel/PDF**:

   - Great Tables puede exportar a múltiples formatos
   - Agregar botones de descarga

4. **Paginación**:
   - Si hay muchos registros (>100)
   - Implementar paginación del backend

## Instalación en Otros Entornos

Para desplegar en producción u otros entornos:

```bash
pip install -r requirements.txt
```

Las dependencias necesarias ya están en `requirements.txt`:

- great-tables==0.20.0
- pandas==2.2.3

## Notas Técnicas

- Great Tables usa Pandas internamente para manipulación de datos
- El HTML generado es estático pero estilizado
- Compatible con todos los navegadores modernos
- No requiere JavaScript para funcionalidad básica

## Soporte

Great Tables documentation: https://posit-dev.github.io/great-tables/
