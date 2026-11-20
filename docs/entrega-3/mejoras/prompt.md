## Rol y Objetivo
Eres un desarrollador frontend senior especialista en UI/UX empresarial B2B y sistemas basados en plantillas del lado del servidor (**Jinja2 + HTMX + Bootstrap 5 + Chart.js** sobre **FastAPI**). 

Tu tarea es **actualizar la capa visual y la forma en que se presentan los datos** en las vistas existentes del proyecto **Proyecta**, tomando como referencia estética y estructural las capturas ubicadas en la ruta de referencia del proyecto docs\entrega-3\mejoras (`auditoria.PNG`, `dashboard1.PNG`, `dashboard2.PNG`, `dashboard3.PNG` y `parametrosdelamab.PNG`).

## Reglas Estrictas de Ejecución (NO ROMPER NADA)
1. **NO ELIMINAR ELEMENTOS EXISTENTES:** Las capturas de referencia muestran únicamente el área de contenido principal y los bloques de datos. Si una plantilla actual incluye barras de filtros globales, encabezados/hero, barras laterales (sidebar), navegación superior o botones de acción que no aparecen en las capturas, **MANTENLOS INTACTOS**. No borres controles, formularios ni secciones existentes; solo actualiza el diseño y distribución de los bloques de visualización de datos mostrados en las imágenes.
2. **CONSERVAR LÓGICA Y BINDINGS:** Mantén intactas todas las variables de contexto de Jinja2 (`{{ ... }}`), los atributos de HTMX (`hx-get`, `hx-post`, `hx-target`, `hx-swap`), los `id` de los contenedores/canvas y las rutas de endpoints del backend FastAPI.
3. **SISTEMA DE DISEÑO Y PALETA DE COLORES:**
   - **Fondo general de página:** Gris verdoso muy suave / neutro (`#F4F7F6` o `#F5F7F6`).
   - **Superficies (Cards):** Tarjetas blancas (`#FFFFFF`) con bordes sutiles (`1px solid #E2E8F0`), esquinas redondeadas amplias (`border-radius: 12px` o `16px`) y espaciado generoso (`padding: 20px–24px`).
   - **Color primario y acentos:** Verde esmeralda / petróleo corporativo (`#0F6E58` / `#107861`) para cifras destacadas, barras principales, filas seleccionadas y botones primarios; verde menta suave (`#8CD3B5` / `#B4DEC9`) para barras secundarias o tracks de progreso; terracota/ámbar (`#B45309` / `#C2591C`) para líneas de meta, alertas de fecha y brechas por cubrir.
   - **Tipografía y alineación:** Títulos de tarjeta en negrita oscura (`#1E293B`), subtítulos en gris medio (`#64748B`), cifras monetarias en formato tabular (`font-variant-numeric: tabular-nums`) y alineadas a la derecha en tablas.

---

## Especificaciones por Pantalla / Vista a Actualizar

### 1. Vista de Dashboard Ejecutivo — Pestaña "Resumen financiero" (`dashboard1.PNG`)
Reestructura el bloque principal de visualización en una grilla de 2x2 tarjetas blancas:
- **Tarjeta Superior Izquierda ("Forecast mensual frente a la meta"):**
  - Subtítulo: *"Millones de pesos chilenos"* (o la unidad dinámica del contexto).
  - Gráfico combinado en **Chart.js**: barras apiladas con bordes superiores redondeados para *Backlog contractual* (verde oscuro `#0F6E58`) y *MAB* (verde claro `#8CD3B5`), superpuesto con una línea punteada (`borderDash: [5, 5]`) color terracota (`#B45309`) para la *Meta*. Leyenda limpia en la parte inferior izquierda.
- **Tarjeta Superior Derecha ("Composición del forecast"):**
  - Subtítulo: *"Participación en el total del período"*.
  - Barra horizontal segmentada única (`height: 16px`, `border-radius: 8px`) mostrando la proporción entre *Backlog contractual* (`#0F6E58`) y *MAB ponderada* (`#8CD3B5`).
  - Debajo, lista limpia con nombre del concepto, monto en gris debajo y porcentaje en negrita verde a la derecha (`82,2 %`, `17,8 %`).
  - Separador horizontal sutil y bloque inferior con *"Backlog confirmado · incluido en la MAB"* y su monto destacado en negrita.
- **Tarjeta Inferior Izquierda ("Dotación proyectada"):**
  - Subtítulo: *"Headcount al cierre de cada mes"*.
  - Gráfico de barras verticales minimalista sin líneas de grilla horizontales, barras con esquinas redondeadas (`border-radius: 6px`), etiquetas numéricas directamente encima de cada barra y mes en el eje X. Destacar el último mes (o mes foco) en verde oscuro (`#0F6E58`) y los anteriores en verde pastel (`#B4DEC9`).
- **Tarjeta Inferior Derecha ("Actividad de cartera"):**
  - Indicadores KPI limpios dispuestos verticalmente: número grande en verde esmeralda (`32px–36px`, `font-weight: 700`) a la izquierda y etiqueta descriptiva a la derecha (*"Oportunidades activas"*, *"Demandas confirmadas"*).

### 2. Vista de Dashboard Ejecutivo — Pestaña "Detalle operativo y comercial" (`dashboard2.PNG` y `dashboard3.PNG`)
Mantén las pestañas de navegación superiores (*Resumen financiero* / *Detalle operativo y comercial*, con la pestaña activa en botón sólido verde `#0F6E58` con texto blanco) y actualiza las tarjetas de contenido: IMPORTANTE, mostrar las alertas más arriba, para demostrar importancia.
- **Tarjeta Ancha Superior ("Cumplimiento de meta por líder"):**
  - Tabla limpia sin bordes verticales, solo divisores horizontales suaves (`#E2E8F0`).
  - Columnas: *Responsable* (en negrita), *Registros*, *Forecast · CLP*, *Meta · CLP*, *Brecha por cubrir · CLP* (texto en color terracota `#C2591C`), y *Cobertura de meta* (barra de progreso horizontal en verde oscuro sobre pista verde clara + porcentaje numérico a la derecha).
- **Fila Media (2 columnas: "Forecast por sector" y "Forecast por cliente"):**
  - Listas tabulares compactas con nombre, cantidad de registros (`Reg.`), barra de progreso horizontal proporcional al aporte y monto total a la derecha.
- **Fila Inferior Izquierda ("Pipeline por estado" y "Pipeline por flujo"):**
  - *Pipeline por estado*: filas limpias con estado, conteo (`10 reg.`), barra de progreso horizontal y monto total.
  - *Pipeline por flujo*: tabla con columnas *Etapa* (`1 · Pendiente RFP`, etc.), *Registros* y *MAB · CLP*.
- **Fila Inferior Derecha ("Alertas operativas" y "Seguimiento a 90 días"):**
  - *Alertas operativas*: lista con fecha destacada en terracota negrita (`15 nov`), código de registro (`OPD-0015`), nombre de la demanda y ventana de días a la derecha (`30 días`).
  - *Seguimiento a 90 días*: filas clave-valor con estado en texto verde (`Sin vencimientos`, `Sin liberaciones`) y un banner inferior de alerta suave (`background: #FDF3E7`, `border-radius: 10px`) con título en terracota (*"Calidad del dato"*) y mensaje destacado (*"8 registros activos sin perfiles asignados"*).

### 3. Vista de Auditoría (`auditoria.PNG`)
Transforma la vista en un layout maestro-detalle de 2 columnas (60% izquierda / 40% derecha):
- **Columna Izquierda ("Eventos registrados"):**
  - Tabla limpia con columnas: *Fecha y hora*, *Registro* (código en verde negrita `#0F6E58`), *Cambio* y *Usuario*.
  - La fila activa/seleccionada debe resaltarse con fondo verde muy suave (`#E6F2EE`).
  - Pie de tarjeta con paginación minimalista: texto *"1–8 de 60 eventos"* a la izquierda y controles *"Anterior / Siguiente →"* a la derecha.
- **Columna Derecha ("Detalle del evento"):**
  - Tarjeta fija/contextual con etiqueta superior en mayúsculas (*"DETALLE DEL EVENTO"*), título grande (*"Creación de OPD-0041"*), subtítulo con fecha y usuario (`01 mar 2026 · 06:00 / Líder 1`).
  - Lista de atributos clave-valor alineados izquierda/derecha: *Entidad*, *Tipo / estado*, *Flujo*, *Probabilidad / confiabilidad*, *Perfiles* y *Motivo*.
  - Sección inferior separada por línea horizontal: título *"Impacto a 12 meses"* con subtítulo *"Antes → después"* a la derecha, mostrando la comparación directa para *MAB* y *Forecast* (ej. `$0 → Sin dato`).
  - Asegura que al hacer clic en una fila de la tabla izquierda, este panel derecho se actualice dinámicamente (vía HTMX o JS existente).

### 4. Vista de Parámetros de la MAB (`parametrosdelamab.PNG`)
- **Fila Superior (Grilla de 3 tarjetas iguales):**
  - *Horas mensuales* (`180 h`), *Confiabilidad inicial* (`90 %`) y *Meta comercial por líder* (`Líder 1` con selector desplegable).
  - Cada tarjeta muestra el valor vigente en verde grande (`#0F6E58`), subtítulo de vigencia (*"Vigente desde enero de 2026"*), dos inputs en paralelo con fondo gris suave (`#F1F5F3`, sin borde marcado) para el nuevo valor y *"Rige desde (Mes / año)"*, un input ancho para *"Motivo del cambio *"* y el botón sólido verde (*"Guardar cambio"* / *"Guardar meta"*).
- **Tarjeta Inferior Ancha ("Historial de vigencias"):**
  - Encabezado con título a la izquierda y botones de filtro/toggle a la derecha (*"Horas y confiabilidad"* activo en verde sólido vs *"Metas por líder"* en gris claro).
  - Tabla limpia con columnas: *Parámetro*, *Rige desde*, *Valor* (en negrita), *Usuario* y *Fecha de registro*.

---

## Instrucciones de Entrega para Codex
1. Inspecciona primero la estructura de plantillas HTML/Jinja2 y archivos CSS/JS actuales del repositorio para identificar dónde se renderizan estas vistas.
2. Crea o actualiza una hoja de estilos dedicada (ej. `static/css/proyecta-theme.css`) y aplica las clases necesarias en los templates correspondientes.
3. Verifica que ningún filtro, botón existente, barra de navegación o endpoint HTMX se haya eliminado o desconectado.
4. Entrega un resumen breve de los archivos modificados.