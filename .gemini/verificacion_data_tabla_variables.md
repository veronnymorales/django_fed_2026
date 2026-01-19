# Verificación de Datos: Tabla Variables Detallado

## Estado: ✅ CONFIGURACIÓN CORRECTA

### 1. Datos Enviados desde Backend (`views.py` línea 561)

La función `process_variables_detallado()` envía los siguientes campos:

| Campo                          | Tipo      | Descripción                    |
| ------------------------------ | --------- | ------------------------------ |
| `d_anio`                       | Array     | Año                            |
| `d_mes`                        | Array     | Mes                            |
| `d_codigo_red`                 | Array     | Código de Red                  |
| **`d_red`**                    | **Array** | **Nombre de Red** ✅           |
| `d_codigo_microred`            | Array     | Código de MicroRed             |
| **`d_microred`**               | **Array** | **Nombre de MicroRed** ✅      |
| `d_codigo_unico`               | Array     | Código Único                   |
| `d_id_establecimiento`         | Array     | ID Establecimiento             |
| **`d_nombre_establecimiento`** | **Array** | **Nombre Establecimiento** ✅  |
| `d_ubigueo_establecimiento`    | Array     | Ubigeo                         |
| **`d_den_variable`**           | **Array** | **Denominador** ✅             |
| **`d_num_1trim`**              | **Array** | **Numerador 1er Trimestre** ✅ |
| **`d_avance_1trim`**           | **Array** | **Avance % 1er Trimestre** ✅  |
| **`d_num_2trim`**              | **Array** | **Numerador 2do Trimestre** ✅ |
| **`d_avance_2trim`**           | **Array** | **Avance % 2do Trimestre** ✅  |
| **`d_num_3trim`**              | **Array** | **Numerador 3er Trimestre** ✅ |
| **`d_avance_3trim`**           | **Array** | **Avance % 3er Trimestre** ✅  |

### 2. Datos Consumidos por la Tabla (`table_variables_detallado.html`)

La función `prepareTableData(data)` consume:

```javascript
function prepareTableData(data) {
  const dataLength = data.d_anio?.length || 0;

  for (let i = 0; i < dataLength; i++) {
    tableData.push([
      safeGet(data.d_red, i), // ✅ Columna 0: Red
      safeGet(data.d_microred, i), // ✅ Columna 1: MicroRed
      safeGet(data.d_nombre_establecimiento, i), // ✅ Columna 2: Establecimiento
      safeGet(data.d_den_variable, i), // ✅ Columna 3: Denominador
      safeGet(data.d_num_1trim, i, 0), // ✅ Columna 4: Num 1° Trim
      formatPercent(data.d_avance_1trim[i], 0), // ✅ Columna 5: 1T %
      safeGet(data.d_num_2trim, i, 0), // ✅ Columna 6: Num 2° Trim
      formatPercent(data.d_avance_2trim[i], 0), // ✅ Columna 7: 2T %
      safeGet(data.d_num_3trim, i, 0), // ✅ Columna 8: Num 3° Trim
      formatPercent(data.d_avance_3trim[i], 0), // ✅ Columna 9: 3T %
      avance1trim, // ✅ Columna 10: Avg 1T (oculto)
    ]);
  }
}
```

### 3. Estructura de la Tabla HTML

| Columna # | Título          | Campo de Datos             | Visible       | Tipo                    |
| --------- | --------------- | -------------------------- | ------------- | ----------------------- |
| 0         | Red             | `d_red`                    | Sí (agrupado) | Texto                   |
| 1         | MicroRed        | `d_microred`               | Sí            | Texto                   |
| 2         | Establecimiento | `d_nombre_establecimiento` | Sí            | Texto                   |
| 3         | Den             | `d_den_variable`           | Sí            | Número                  |
| 4         | 1° Trim         | `d_num_1trim`              | Sí            | Número                  |
| 5         | 1T %            | `d_avance_1trim`           | Sí            | Porcentaje (con fondo)  |
| 6         | 2° Trim         | `d_num_2trim`              | Sí            | Número                  |
| 7         | 2T %            | `d_avance_2trim`           | Sí            | Porcentaje (solo texto) |
| 8         | 3° Trim         | `d_num_3trim`              | Sí            | Número                  |
| 9         | 3T %            | `d_avance_3trim`           | Sí            | Porcentaje (solo texto) |
| 10        | Avg1T           | `d_avance_1trim`           | No            | Número (para ordenar)   |
| 11        | RedAvg          | Calculado                  | No            | Número (para ordenar)   |

### 4. Agrupación y Ordenamiento

**Agrupación por Red:**

- La tabla usa `rowGroup.dataSrc: [0]` para agrupar por la columna 0 (`d_red`)
- Cada grupo muestra el promedio de `1T %` de todos los establecimientos de esa red
- Los grupos son colapsables

**Ordenamiento:**

1. Primero por promedio de RED (columna 11, descendente)
2. Luego por `1T %` individual (columna 10, descendente)

### 5. Filtros Aplicados

Los datos respetan los filtros de la vista:

- ✅ Año: 2025 (hardcoded en la línea 535 de views.py)
- ✅ Mes inicio y fin: según selección del usuario
- ✅ Red, MicroRed, Establecimiento: según selección
- ✅ Provincia, Distrito: según selección

### 6. Coloración de Celdas

**1T % (con fondo de color):**

- Rojo: < 70%
- Amarillo: 70% - 82%
- Verde: >= 82%

**2T % y 3T % (solo color de texto - lógica INVERSA):**

- Verde: < 20% (menor es mejor)
- Naranja: 20% - 50%
- Rojo: >= 50%

---

## ✅ Conclusión

**TODAS las variables están correctamente configuradas** y la tabla debe consumir los datos sin problemas. La estructura de datos enviada desde el backend coincide perfectamente con lo que espera el frontend.

### Campos Clave Verificados:

- ✅ `d_red` - para agrupar
- ✅ `d_microred` - columna visible
- ✅ `d_nombre_establecimiento` - columna visible
- ✅ `d_den_variable` - denominador
- ✅ `d_num_1trim`, `d_num_2trim`, `d_num_3trim` - numeradores
- ✅ `d_avance_1trim`, `d_avance_2trim`, `d_avance_3trim` - porcentajes de avance

### Cantidades Esperadas:

- Número de registros: `data.d_anio.length`
- Número de columnas visibles: 10
- Número de grupos (Redes): Variable según filtros
