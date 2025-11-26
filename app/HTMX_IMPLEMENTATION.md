# HTMX Hierarchical Table Implementation - Documentation

## Resumen de Implementación

Se ha implementado una tabla jerárquica interactiva usando HTMX que permite:

- **Carga diferida (lazy loading)** de datos por niveles
- **Jerarquía**: Red → MicroRed → Establecimientos
- **Sin recargar la página** usando HTMX
- **Estilo moderno** con gradientes y animaciones
- **Gran Tables inspirado** para formato de datos tabulares

---

## Cambios Realizados

### 1. **Template Principal**

📄 `app/templates/s11_captacion_gestante/components/chart/table_variables_detallado.html`

**Cambios:**

- ❌ Eliminado: DataTables y RowGroup plugin
- ✅ Agregado: Sistema HTMX de carga jerárquica
- ✅ Agregado: Estilos CSS modernos con gradientes
- ✅ Agregado: Funcionalidad JavaScript para expandir/colapsar

**Características:**

- Vista inicial: Solo encabezados de Red (colapsado)
- Al hacer clic en Red → Carga MicroRedes vía HTMX
- Al hacer clic en MicroRed → Carga Establecimientos vía HTMX
- Botones "Expandir Todo" y "Colapsar Todo"

---

### 2. **Views de Django**

📄 `app/s11_captacion_gestante/views.py`

**Nuevas Vistas Agregadas:**

#### `htmx_get_redes(request)`

- **Propósito**: Retorna HTML con encabezados de todas las Redes
- **Datos**: Agrupa por Red y cuenta registros
- **Template**: `partials/htmx_redes.html`

#### `htmx_get_microredes(request)`

- **Propósito**: Retorna HTML con MicroRedes de una Red específica
- **Parámetro**: `red` (código de Red)
- **Template**: `partials/htmx_microredes.html`

#### `htmx_get_establecimientos(request)`

- **Propósito**: Retorna HTML con tabla de Establecimientos
- **Parámetro**: `microred` (código de MicroRed)
- **Template**: `partials/htmx_establecimientos.html`
- **Estilo**: Formato inspirado en Great Tables

---

### 3. **Partial Templates**

#### 📄 `partials/htmx_redes.html`

```django
- Lista de Redes con contador de registros
- Elemento colapsable por cada Red
- Iconos de expansión/colapso
```

#### 📄 `partials/htmx_microredes.html`

```django
- Lista de MicroRedes dentro de una Red
- Elemento colapsable por cada MicroRed
- Estilos con indentación visual
```

#### 📄 `partials/htmx_establecimientos.html`

```django
- Tabla estilizada con datos de Establecimientos
- Columnas: Establecimiento, Variable, Trimestres (1°, 2°, 3°)
- Estilos inspirados en Great Tables
- Contador de registros
```

---

### 4. **URLs**

📄 `app/s11_captacion_gestante/urls.py`

**Nuevos Endpoints:**

```python
path('htmx/redes/', htmx_get_redes, name='htmx_get_redes')
path('htmx/microredes/', htmx_get_microredes, name='htmx_get_microredes')
path('htmx/establecimientos/', htmx_get_establecimientos, name='htmx_get_establecimientos')
```

---

## Flujo de Datos

```
┌─────────────────────────────────────────────────────────┐
│  1. Renderizado Inicial                                 │
│     renderTablaVariablesDetallado(data, params)         │
│     └─> Muestra loading spinner                         │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  2. Cargar Redes                                         │
│     GET /s11_captacion_gestante/htmx/redes/             │
│     └─> Retorna HTML con encabezados de Red             │
│         (todos colapsados)                               │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  3. Usuario hace clic en una Red                        │
│     GET /htmx/microredes/?red=XXXX                      │
│     └─> Retorna HTML con MicroRedes de esa Red          │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  4. Usuario hace clic en una MicroRed                   │
│     GET /htmx/establecimientos/?microred=YYYY           │
│     └─> Retorna HTML con tabla de Establecimientos      │
│         (estilo Great Tables)                             │
└─────────────────────────────────────────────────────────┘
```

---

## Estilos CSS

### Clases Principales

| Clase                        | Uso                    | Estilo                             |
| ---------------------------- | ---------------------- | ---------------------------------- |
| `.red-header`                | Encabezado de Red      | Gradiente morado, hover con sombra |
| `.microred-header`           | Encabezado de MicroRed | Gradiente verde, indentado         |
| `.establecimiento-container` | Contenedor de tabla    | Fondo gris claro, indentado        |
| `.gt-table`                  | Tabla estilizada       | Estilo Great Tables                |
| `.icon-toggle`               | Icono de colapso       | Rotación animada                   |

### Diseño Visual

- **Red**: Gradiente morado (#667eea → #764ba2)
- **MicroRed**: Gradiente verde (#48bb78 → #38a169)
- **Establecimientos**: Tabla con zebra striping
- **Animaciones**: Transiciones suaves (0.3s)
- **Hover effects**: Transformación y sombras

---

## Parámetros de Filtro

Todos los endpoints HTMX respetan los siguientes filtros:

```javascript
{
  anio: '2025',
  mes_inicio: '1',
  mes_fin: '12',
  red: '',
  microred: '',
  establecimiento: '',
  provincia: '',
  distrito: ''
}
```

---

## Beneficios de la Implementación

✅ **Performance**: Carga solo datos necesarios (lazy loading)  
✅ **UX**: Sin recarga de página, transiciones suaves  
✅ **Escalabilidad**: Maneja grandes volúmenes de datos eficientemente  
✅ **Mantenibilidad**: Código modular y bien organizado  
✅ **Diseño**: Interfaz moderna y profesional  
✅ **Accesibilidad**: Indicadores visuales claros (iconos, colores)

---

## Próximos Pasos (Opcional)

### Para implementar Great Tables completo:

1. **Instalar Great Tables**:

   ```bash
   pip install great-tables
   ```

2. **Modificar `htmx_get_establecimientos`**:

   ```python
   from great_tables import GT, style, loc

   # Crear DataFrame
   import pandas as pd
   df = pd.DataFrame(establecimientos_data)

   # Crear Great Table
   gt_table = (
       GT(df)
       .tab_header(
           title="Establecimientos",
           subtitle="Datos por Trimestre"
       )
       .fmt_percent(columns=['1T %', '2T %', '3T %'])
       .tab_style(
           style=style.fill(color='#f0f9ff'),
           locations=loc.body(columns=['1° Trim', '2° Trim', '3° Trim'])
       )
   )

   # Renderizar como HTML
   html = gt_table.as_raw_html()
   ```

---

## Testing

### Verificar Funcionamiento:

1. ✅ Abrir página principal
2. ✅ Ver solo encabezados de Red (colapsados)
3. ✅ Hacer clic en una Red → Ver MicroRedes
4. ✅ Hacer clic en una MicroRed → Ver tabla de Establecimientos
5. ✅ Probar "Expandir Todo" → Todas las jerarquías abiertas
6. ✅ Probar "Colapsar Todo" → Todo cerrado
7. ✅ Verificar que filtros (año, mes, provincia, etc.) funcionen

---

## Troubleshooting

### Si no aparecen datos:

- Verificar que `obtener_variables_detallado()` retorne datos
- Revisar console del navegador para errores JavaScript
- Verificar que las URLs estén correctas en `urls.py`

### Si los estilos no se aplican:

- Confirmar que el CSS esté dentro del template
- Verificar que no haya conflictos con CSS global

### Si HTMX no carga:

- Verificar que los endpoints retornen status 200
- Revisar logs de Django para errores en las views

---

## Autor

Implementación HTMX Hierarchical Table  
Fecha: 2025-11-26
