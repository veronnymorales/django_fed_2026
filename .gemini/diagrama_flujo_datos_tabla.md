# Diagrama de Flujo de Datos: Tabla Variables Detallado

## 📊 Flujo Completo desde Backend hasta Frontend

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USUARIO                                    │
│  Selecciona filtros: Año, Mes, Red, MicroRed, Establecimiento      │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FRONTEND (JavaScript)                            │
│  index_s11_captacion_gestante.html (línea 242-280)                │
│                                                                     │
│  1. Captura evento submit del formulario                           │
│  2. Construye queryString con filtros                              │
│  3. Hace fetch a la vista con XMLHttpRequest                       │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    BACKEND - VISTA                                  │
│  views.py::index_s11_captacion_gestante (líneas 458-595)           │
│                                                                     │
│  1. Recibe request con filtros                                     │
│  2. Valida que es request AJAX                                     │
│  3. Extrae parámetros: anio, mes_inicio, mes_fin, red, etc.       │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    BACKEND - QUERY                                  │
│  queries.py::obtener_variables_detallado (líneas 321-407)          │
│                                                                     │
│  1. Llama stored procedure: fn_obtener_variables_detallado         │
│  2. Pasa parámetros: anio='2025', mes_inicio, mes_fin, etc.       │
│  3. Obtiene resultados de PostgreSQL                               │
│                                                                     │
│  RETORNA: List[Dict] con 17 campos por registro                    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  BACKEND - PROCESAMIENTO                            │
│  views.py::process_variables_detallado (líneas 343-413)            │
│                                                                     │
│  ENTRADA: List[Dict] desde obtener_variables_detallado             │
│                                                                     │
│  TRANSFORMACIÓN:                                                    │
│  for row in resultados_variables_detallado:                        │
│    - Extrae: d_anio, d_mes, d_red, d_microred, etc.               │
│    - Valida: required_keys en cada fila                            │
│    - Agrega a arrays: data['d_anio'].append(d_anio)               │
│                                                                     │
│  SALIDA: Dict[str, List] con 17 arrays                             │
│  {                                                                  │
│    'd_anio': [2025, 2025, ...],                                    │
│    'd_mes': [1, 1, ...],                                           │
│    'd_codigo_red': ['1', '1', ...],                                │
│    'd_red': ['VALLE DEL MANTARO', 'VALLE DEL MANTARO', ...],      │
│    'd_microred': ['CHILCA', 'CHILCA', ...],                        │
│    'd_nombre_establecimiento': ['CS CHILCA', 'PS SAN JOSE', ...], │
│    'd_den_variable': [100, 85, ...],                               │
│    'd_num_1trim': [75, 60, ...],                                   │
│    'd_avance_1trim': [75.0, 70.5, ...],                            │
│    'd_num_2trim': [12, 15, ...],                                   │
│    'd_avance_2trim': [12.0, 17.6, ...],                            │
│    'd_num_3trim': [5, 3, ...],                                     │
│    'd_avance_3trim': [5.0, 3.5, ...]                               │
│  }                                                                  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  BACKEND - INTEGRACIÓN                              │
│  views.py::index_s11_captacion_gestante (líneas 557-562)           │
│                                                                     │
│  data = {                                                           │
│    **process_velocimetro(resultados_velocimetro),                  │
│    **process_avance_mensual(resultados_grafico_mensual),           │
│    **process_variables(resultados_variables),                      │
│    **process_variables_detallado(resultados_variables_detallado), ◄─ AQUÍ
│    **process_grafico_por_redes(resultados_grafico_por_redes)       │
│  }                                                                  │
│                                                                     │
│  return JsonResponse(data)  # Envía JSON al frontend               │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│              FRONTEND - RECEPCIÓN DE DATOS                          │
│  index_s11_captacion_gestante.html (líneas 257-275)                │
│                                                                     │
│  .then(data => {                                                    │
│    console.log('✅ Datos recibidos:', data);                       │
│                                                                     │
│    // Llama a todas las funciones de renderizado                   │
│    if (window.renderChartVelocimetro) ...                          │
│    if (window.renderChartAvanceNumDen) ...                         │
│    if (window.renderChartAvanceMensual) ...                        │
│    if (window.renderChartAvanceVariables) ...                      │
│    if (window.renderTablaVariablesDetallado)                       │
│      window.renderTablaVariablesDetallado(data, params); ◄─ AQUÍ    │
│    if (window.renderChartRedRanking) ...                           │
│  })                                                                 │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│          FRONTEND - PREPARACIÓN DE DATOS                            │
│  table_variables_detallado.html::prepareTableData (líneas 294-332) │
│                                                                     │
│  ENTRADA: data (objeto con todas las claves 'd_*')                 │
│                                                                     │
│  PROCESO:                                                           │
│  const dataLength = data.d_anio?.length || 0;                      │
│                                                                     │
│  for (let i = 0; i < dataLength; i++) {                            │
│    tableData.push([                                                 │
│      safeGet(data.d_red, i),              // Col 0: Red            │
│      safeGet(data.d_microred, i),         // Col 1: MicroRed       │
│      safeGet(data.d_nombre_establecimiento, i), // Col 2: Estab.   │
│      safeGet(data.d_den_variable, i),     // Col 3: Den            │
│      safeGet(data.d_num_1trim, i, 0),     // Col 4: Num 1T         │
│      formatPercent(data.d_avance_1trim[i]), // Col 5: 1T %         │
│      safeGet(data.d_num_2trim, i, 0),     // Col 6: Num 2T         │
│      formatPercent(data.d_avance_2trim[i]), // Col 7: 2T %         │
│      safeGet(data.d_num_3trim, i, 0),     // Col 8: Num 3T         │
│      formatPercent(data.d_avance_3trim[i]), // Col 9: 3T %         │
│      avance1trim                           // Col 10: Avg1T (hidden)│
│    ]);                                                              │
│  }                                                                  │
│                                                                     │
│  SALIDA: Array de arrays (tableData)                               │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│        FRONTEND - CÁLCULO DE PROMEDIOS POR RED                      │
│  table_variables_detallado.html::calculateRedAverages              │
│  (líneas 341-355)                                                   │
│                                                                     │
│  PROCESO:                                                           │
│  const redAverages = {};                                            │
│                                                                     │
│  tableData.forEach((row) => {                                       │
│    const red = row[0];                    // Nombre de la RED       │
│    const percent = row[10];               // Avance 1T %            │
│                                                                     │
│    if (!redAverages[red]) {                                         │
│      redAverages[red] = { sum: 0, count: 0 };                      │
│    }                                                                │
│    redAverages[red].sum += percent;                                 │
│    redAverages[red].count++;                                        │
│  });                                                                │
│                                                                     │
│  // Calcula promedio final por RED                                 │
│  Object.keys(redAverages).forEach((red) => {                        │
│    redAverages[red].avg = redAverages[red].sum / redAverages[red].count;│
│  });                                                                │
│                                                                     │
│  SALIDA: Objeto con promedios por RED                              │
│  {                                                                  │
│    'VALLE DEL MANTARO': { sum: 450.5, count: 6, avg: 75.08 },     │
│    'JAUJA': { sum: 380.2, count: 5, avg: 76.04 },                 │
│    ...                                                              │
│  }                                                                  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│         FRONTEND - AGREGAR PROMEDIOS Y ORDENAR                      │
│  table_variables_detallado.html::addRedAveragesAndSort             │
│  (líneas 365-381)                                                   │
│                                                                     │
│  PROCESO:                                                           │
│  // Agregar promedio de RED a cada fila                            │
│  tableData.forEach((row) => {                                       │
│    const red = row[0];                                              │
│    row.push(redAverages[red].avg);  // Col 11: Promedio de RED     │
│  });                                                                │
│                                                                     │
│  // Ordenar por promedio de RED (desc), luego por 1T % (desc)     │
│  tableData.sort((a, b) => {                                         │
│    const avgDiff = b[11] - a[11];   // Promedio RED                │
│    return avgDiff !== 0 ? avgDiff : b[10] - a[10]; // 1T %         │
│  });                                                                │
│                                                                     │
│  SALIDA: tableData ordenado y con columna 11 agregada              │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│            FRONTEND - INICIALIZACIÓN DE DATATABLE                   │
│  table_variables_detallado.html::initializeDataTable               │
│  (líneas 627-666)                                                   │
│                                                                     │
│  CONFIGURACIÓN:                                                     │
│  tablaInstance = $("#tabla-variables-detallado").DataTable({       │
│    data: tableData,              // Datos procesados                │
│    columns: getColumnsConfig(),  // 12 columnas (10 visible + 2 hidden)│
│    order: [[11, 'desc'], [10, 'desc']], // Orden por RED y 1T %   │
│    paging: false,                // Sin paginación                  │
│    searching: false,             // Sin búsqueda                    │
│    rowGroup: {                                                      │
│      dataSrc: [0],               // Agrupar por col 0 (RED)         │
│      startRender: renderGroupHeader  // Renderizar encabezado       │
│    }                                                                │
│  });                                                                │
│                                                                     │
│  EVENTOS:                                                           │
│  - Click en grupo: expandir/colapsar                               │
│  - Botón "Expandir": expandir todos                                │
│  - Botón "Colapsar": colapsar todos                                │
│                                                                     │
│  COLORACIÓN DE CELDAS:                                              │
│  - Col 5 (1T %): con fondo de color según umbrales                │
│  - Col 7 (2T %): solo texto de color (lógica inversa)             │
│  - Col 9 (3T %): solo texto de color (lógica inversa)             │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  TABLA RENDERIZADA                                  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ 🔽 RED: VALLE DEL MANTARO [6] ━━━━━━━━━ 75.1% ░░░░░░░        │ │
│  ├───┬──────────┬────────────────┬─────┬────────┬───────┬────┐   │ │
│  │   │ MicroRed │ Establecimiento│ Den │ 1° T   │ 1T %  │... │   │ │
│  ├───┼──────────┼────────────────┼─────┼────────┼───────┼────┤   │ │
│  │   │ CHILCA   │ CS CHILCA      │ 100 │ 75     │ 75.0% │... │   │ │
│  │   │ CHILCA   │ PS SAN JOSE    │ 85  │ 60     │ 70.5% │... │   │ │
│  │   │ ...      │ ...            │ ... │ ...    │ ...   │... │   │ │
│  └───┴──────────┴────────────────┴─────┴────────┴───────┴────┘   │ │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ 🔽 RED: JAUJA [5] ━━━━━━━━━━━ 76.0% ░░░░░░░                 │ │
│  ├───┬──────────┬────────────────┬─────┬────────┬───────┬────┐   │ │
│  │   │ ...      │ ...            │ ... │ ...    │ ...   │... │   │ │
│  └───┴──────────┴────────────────┴─────┴────────┴───────┴────┘   │ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
                        👤 USUARIO VE LA TABLA
```

---

## 🔑 Campos Clave en el Flujo

| Campo Backend              | Campo Frontend                  | Uso en Tabla                                 |
| -------------------------- | ------------------------------- | -------------------------------------------- |
| `d_anio`                   | `data.d_anio`                   | Validación de datos (length)                 |
| `d_red`                    | `data.d_red`                    | **Columna 0** (agrupación)                   |
| `d_microred`               | `data.d_microred`               | **Columna 1** (visible)                      |
| `d_nombre_establecimiento` | `data.d_nombre_establecimiento` | **Columna 2** (visible)                      |
| `d_den_variable`           | `data.d_den_variable`           | **Columna 3** (visible)                      |
| `d_num_1trim`              | `data.d_num_1trim`              | **Columna 4** (visible)                      |
| `d_avance_1trim`           | `data.d_avance_1trim`           | **Columnas 5 y 10** (visible + ordenamiento) |
| `d_num_2trim`              | `data.d_num_2trim`              | **Columna 6** (visible)                      |
| `d_avance_2trim`           | `data.d_avance_2trim`           | **Columna 7** (visible)                      |
| `d_num_3trim`              | `data.d_num_3trim`              | **Columna 8** (visible)                      |
| `d_avance_3trim`           | `data.d_avance_3trim`           | **Columna 9** (visible)                      |
| N/A (calculado)            | N/A                             | **Columna 11** (promedio RED, ordenamiento)  |

---

## 🎨 Umbrales de Coloración

### Columna 5: 1T % (con fondo)

```
     0%                70%              82%              100%
     ├─────────────────┼────────────────┼─────────────────┤
     │      ROJO       │    AMARILLO    │      VERDE      │
     │   < 70%         │   70% - 82%    │     >= 82%      │
     │ #ff6b6b (bg)    │ #ffd93d (bg)   │  #6bcf7f (bg)   │
```

### Columnas 7 y 9: 2T %, 3T % (solo texto - LÓGICA INVERSA)

```
     0%                20%              50%              100%
     ├─────────────────┼────────────────┼─────────────────┤
     │      VERDE      │    NARANJA     │      ROJO       │
     │   < 20%         │   20% - 50%    │     >= 50%      │
     │ #28a745 (text)  │ #ff8c00 (text) │ #ff6b6b (text)  │
     │  Menor es MEJOR │                │ Mayor es PEOR   │
```

---

## ⚙️ Configuración de DataTables

```javascript
{
  data: tableData,                  // Array de arrays
  columns: [
    { title: "Red" },               // Col 0 - Agrupada
    { title: "MicroRed" },          // Col 1
    { title: "Establecimiento" },   // Col 2
    { title: "Den" },               // Col 3
    { title: "1° Trim", className: "number-cell" },  // Col 4
    { title: "1T %", className: "percent-cell", createdCell: applyPercentColorWithBackground }, // Col 5
    { title: "2° Trim", className: "number-cell" },  // Col 6
    { title: "2T %", className: "percent-cell", createdCell: applyPercentColorTextOnly },      // Col 7
    { title: "3° Trim", className: "number-cell" },  // Col 8
    { title: "3T %", className: "percent-cell", createdCell: applyPercentColorTextOnly },      // Col 9
    { title: "Avg1T", visible: false },    // Col 10 - Oculta
    { title: "RedAvg", visible: false }    // Col 11 - Oculta
  ],
  order: [[11, "desc"], [10, "desc"]], // Ordenar por RedAvg, luego Avg1T
  rowGroup: {
    dataSrc: [0],                    // Agrupar por columna 0 (Red)
    startRender: renderGroupHeader   // Función personalizada
  },
  paging: false,                     // Sin paginación
  searching: false,                  // Sin búsqueda
  info: false                        // Sin información
}
```

---

## ✅ Verificaciones Automáticas

El código incluye múltiples validaciones:

### Backend:

1. ✅ Validación de claves requeridas en cada fila
2. ✅ Manejo de valores None/NULL
3. ✅ Logging de errores con contexto
4. ✅ Valores por defecto en caso de error

### Frontend:

1. ✅ Validación de existencia de arrays (`data.d_anio?.length`)
2. ✅ Función `safeGet()` para acceso seguro a arrays
3. ✅ Validación de extensión RowGroup antes de usar
4. ✅ Manejo de valores NaN en formatPercent()
5. ✅ Try-catch en procesamiento de filas

---

## 🔍 Puntos de Logging para Debugging

### Backend (views.py):

```python
logger.info(f"Se obtuvieron {len(resultados)} establecimientos para variables detallado")
logger.warning("No se pudieron procesar filas válidas de variables detallado")
logger.error(f"Error al obtener datos de variables detallado: {e}")
logger.error(f"Error procesando la fila {index}: {str(e)}")
```

### Frontend (JavaScript):

```javascript
console.log("🎯 Iniciando renderizado de tabla con agrupación");
console.log("📊 Claves disponibles:", Object.keys(data));
console.log("📏 Total de registros:", dataLength);
console.log("📊 Promedios por RED:", redAverages);
console.log("📊 Filas procesadas:", sortedData.length);
console.log("✅ Tabla renderizada con éxito");
console.log("📁 Tabla colapsada automáticamente");
```

---

## 🎯 Conclusión del Flujo

**ESTADO: ✅ FLUJO COMPLETO Y CORRECTO**

El flujo de datos desde el backend hasta el frontend está completamente verificado y funciona correctamente. No se requieren cambios en la implementación actual.
