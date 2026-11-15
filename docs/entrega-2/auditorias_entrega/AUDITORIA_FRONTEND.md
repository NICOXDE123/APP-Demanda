# Auditoría frontend de Proyecta

> Seguimiento: los cambios de escritorio autorizados se documentan en [IMPLEMENTACION_ESCRITORIO.md](IMPLEMENTACION_ESCRITORIO.md). Este informe conserva el diagnóstico previo a la implementación.

**Fecha:** 12 de noviembre de 2026. **Alcance:** aplicación FastAPI/Jinja2 actual del directorio de trabajo, incluidos los cambios locales preexistentes. **Entrega:** diagnóstico y plan; no se modifica la aplicación.

## 1. Las tres mejoras que implementaría primero

1. **Hacer reconocible la ubicación y el regreso al listado.** Marcar la sección activa en el menú con texto en negrita, subrayado o indicador persistente y `aria-current="page"`; mantener «Registros» activo dentro de una ficha. Conservar los filtros al volver. Resuelve la falta de orientación al abrir una URL directamente y la pérdida de contexto durante el análisis.
2. **Corregir los contrastes compartidos y el foco del menú.** El menú alcanza aproximadamente 4,04:1 y el texto secundario sobre el fondo general, 4,4486:1: ambos quedan por debajo del mínimo de texto normal. Ajustar también límites de campos y la serie MAB del gráfico. Resolverlo en los estilos compartidos evita arreglos diferentes por pantalla.
3. **Acercar las tareas principales en móvil y contener las tablas.** Corregir primero el desborde global de Parámetros a 320 px. Después compactar filtros secundarios, priorizar indicadores y añadir accesos internos en la ficha: en 390 px, «Estado y flujo» empieza alrededor de y=2093 y «Bitácora» en y=3412. Hoy una consulta o actualización cotidiana exige recorrer mucho contenido previo.

El modo oscuro y el favicon son mejoras válidas, pero no deberían desplazar estos problemas de lectura, orientación y ejecución de tareas.

## 2. Método, producto y cobertura

Se utilizó la skill [UI UX Pro Max](../../../.agents/skills/ui-ux-pro-max/SKILL.md), su checklist de revisión y la búsqueda específica de resumen de errores. La búsqueda de gráficos no produjo una coincidencia suficientemente específica para esta composición mensual; no se adoptaron sus recomendaciones de cambiar de gráfico. Las propuestas del gráfico se apoyan en la implementación observada y en los criterios W3C citados al final.

Proyecta permite a **Líderes** mantener sus oportunidades y demandas; a **Operaciones**, gestionar registros, parámetros y confiabilidad; y a **Ejecutivos**, consultar proyecciones y su trazabilidad. Los flujos relevantes son iniciar sesión, filtrar el forecast, abrir registros que explican una cifra, revisar componentes mensuales, crear registros y mantener perfiles, estados y bitácora.

### Entorno y procedimiento

- Leídos `README.md`, `ENTREGA_2.md`, `pyproject.toml`, `src/proyecta/README.md`, `tests/README.md`, `docs/equipo.md`, rutas, plantillas, CSS y JS de la web.
- No había servicio escuchando en 8000/8080 al inicio. Se levantó una instancia local con `.venv\Scripts\python.exe -m uvicorn proyecta.main:app --host 127.0.0.1 --port 8000`, siguiendo el punto de entrada documentado y sin instalar dependencias.
- Navegador real **Chrome headless**, controlado mediante DevTools; se inspeccionaron DOM, estilos calculados, dimensiones y capturas temporales. No se auditó el mockup de `docs/mockups/` como si fuera la aplicación.
- Escritorio **1440 × 900**, intermedio **768 × 900** y emulación móvil **390 × 844** y **320 × 844**, en píxeles CSS. La emulación móvil no sustituye un dispositivo físico.
- Acceso con las cuentas sintéticas locales de Operaciones, Líder 1 y Ejecutivo. No se incluyen contraseñas en este informe.
- Se creó un registro sintético de prueba, se agregó una entrada de bitácora y se guardó un cambio de horas con vigencia futura para verificar confirmación e historial. Estos cambios fueron únicamente en la instancia local en memoria; no se escribieron datos de negocio en archivos ni servicios externos.

### Rutas y flujos revisados

| Ruta o flujo | Comprobación en navegador | Tamaños / rol |
|---|---|---|
| `/login` → `/` | Inicio de sesión; título, etiquetas y cuentas de demostración | 1440; tres roles al iniciar sus sesiones |
| `/` | Indicadores, gráfico, serie mensual, tablas de cortes y alertas | Los cuatro tamaños; Operaciones. Comprobación adicional de dashboard por Líder y Ejecutivo en 1440 |
| `/registros?activos=1` | Listado, filtros, acceso a ficha y presencia de alta según rol | Los cuatro tamaños; Operaciones. Lista por Líder y Ejecutivo en 1440 |
| `/registros/{id}` | Ficha `OPD-0011 · Fábrica de software`; tablas, perfiles, contrato, formularios y bitácora | Los cuatro tamaños; Operaciones |
| `/registros?activos=1` → «Nuevo registro» → ficha | Modal, validación de perfil incompleto, conservación de datos, alta correcta y confirmación | 390; Operaciones |
| Ficha creada → Bitácora | Envío correcto y mensaje «Entrada agregada a la bitácora» | 390; Operaciones |
| `/parametros` | Formularios, historias y restricciones de edición | Los cuatro tamaños; Operaciones. Solo lectura para Líder/Ejecutivo en 1440 |
| `/parametros/horas` | Guardado por formulario y retorno a `/parametros?ok=1` con confirmación | 1440; Operaciones |
| `/auditoria` | Estado sin eventos y tabla con evento de creación sintético | Los cuatro tamaños sin eventos; 390 con datos |
| `/?q=zz-auditoria-sin-resultados` y `/registros?q=zz-auditoria-sin-resultados` | Gráfico y tablas sin coincidencias, mensajes y recuperación | 390; Operaciones |
| `/no-existe` y `/registros/no-es-uuid` | Error HTML 404 frente a error de validación JSON | 390; Operaciones |
| Preferencia oscura del sistema | Emulación de `prefers-color-scheme: dark` y recarga | 1440; Operaciones |

**Teclado:** se enviaron eventos nativos de Tab, Enter y Escape. Se comprobó apertura del menú móvil y actualización de `aria-expanded`; apertura del modal con foco en Servicio; recorrido de controles; cierre con Escape y retorno a «Nuevo registro»; apertura del detalle mensual con Enter; y estilos de foco de los enlaces del menú. No se certifica exhaustivamente el ciclo de foco: en un recorrido largo de 100 Tab hubo una transición fuera del contenido del diálogo que no se aisló de la navegación del propio navegador. No se registra como defecto confirmado.

### Limitaciones

- Revisión local, no de un despliegue público: `ENTREGA_2.md` todavía tiene un marcador de URL. No se probaron latencia, suspensión del hosting ni caducidad real de sesión.
- Las plantillas `registros/calculo.html` y `sugerencias/index.html` existen, pero no se encontraron rutas web que las rendericen en los routers montados por `main.py`. Se revisaron solo en código; no son pantallas funcionales confirmadas.
- No se recorrieron todas las transiciones de estado, tarifas, conflictos 409, errores 403 ni todas las combinaciones de filtros. Sus problemas de conservación de campos se identifican como inferencias cuando corresponde.
- No hubo pruebas con lector de pantalla, Safari, Firefox, dispositivo táctil físico ni zoom real al 400 %. El ancho de 320 px aporta una comprobación de reflujo, no una certificación completa WCAG.
- El canvas no ofrece foco para sus puntos. No se verificó exhaustivamente el comportamiento del tooltip con toque físico. La disponibilidad de valores sin hover se comprobó mediante su tabla equivalente.
- Se inspeccionaron capturas temporales, pero este entregable conserva únicamente el Markdown solicitado. Las medidas y pasos de reproducción incluidos permiten comprobar los problemas sin depender de imágenes temporales.
- No se ejecutó la suite de dominio: no se cambió código de aplicación y esta entrega es una auditoría de interfaz, no un informe de regresión funcional.

## 3. Veredicto de las seis observaciones

| Hipótesis | Veredicto y dónde se aprecia | Efecto y propuesta |
|---|---|---|
| Modo oscuro | **Se confirma su ausencia.** Al emular sistema oscuro, el fondo continúa en `#f8f9fa`; `<html>` no recibe `data-bs-theme`. No hay selector ni código de persistencia. | Añadir Sistema/Claro/Oscuro usando el soporte de Bootstrap y adaptar los colores propios y Chart.js. Es una preferencia de uso; su ausencia por sí sola no demuestra incumplimiento AA. Véase H10. |
| Breadcrumbs | **Parcial.** La ficha ya muestra «Registros › OPD-0011». No hay una jerarquía profunda que justifique migas en todas las secciones. | Mantener y dar semántica a la ruta existente; preservar filtros al volver. Ejemplo: «Registros › OPD-0011 · Fábrica de software». Los detalles mensuales se expanden dentro de la ficha; no inventar otra ruta. H01. |
| Identificación activa / oscurecer hero | **Se confirma la falta de selección.** En las cuatro secciones todos los enlaces tienen `active=false` y carecen de `aria-current`, incluso entrando por URL directa. | La aplicación actual tiene navbar verde y encabezados, sin un hero independiente. Oscurecer esa franja no identifica cuál sección está abierta. Usar selección por texto/peso/indicador y estado semántico; en móvil, mostrar también la sección junto al menú cerrado. H01. |
| Contraste y jerarquía | **Se confirma con matices.** Fallan pares concretos; otros textos secundarios sí cumplen sobre blanco. También hay densidad y prioridad insuficiente en móvil. | Corregir pares medidos y foco; no tratar todos los grises, todos los bordes o todos los textos pequeños como una infracción. H02–H04. |
| Gráficos | **Parcial.** El gráfico mensual usa una composición adecuada y ya tiene leyenda, período y tabla equivalente. MAB tiene poco contraste; el canvas y su leyenda no son operables por teclado; el vacío no se explica. | Conservar barras apiladas + meta, mejorar color/patrón, unidades y acceso a tabla; ofrecer controles HTML para cualquier interacción que se mantenga exclusiva del canvas. H05 y H07. |
| Favicon | **Se confirma que falta un símbolo útil.** `base.html` declara `href="data:,"`, un recurso vacío; no apunta a un archivo de identidad. | Incorporar símbolo sencillo de Proyecta y variantes pequeñas. No es un fallo HTTP 404 del recurso actual: el recurso está intencionalmente vacío. Comprobar la pestaña en navegador visible al implementar. H11. |

## 4. Hallazgos priorizados

**P1:** impacto alto o barrera de lectura/tarea; **P2:** fricción relevante; **P3:** mejora posterior. **N:** observado en navegador; **C:** causa o alcance inferido en código. Las rutas de archivos indicadas a continuación son relativas a `src/proyecta/interfaces/web/`, salvo indicación contraria.

### H01 · P1 · Ubicación sin selección y regreso sin contexto

**Ruta/componente:** navegación global y `/registros/{id}`.

**Evidencia (N):** Dashboard, Registros, Parámetros MAB y Auditoría mantienen exactamente el mismo estado de menú. El encabezado sí cambia, por lo que no hay ausencia total de orientación. La ficha incluye una miga «Registros › OPD-0011», cuyo enlace vuelve siempre a `/registros?activos=1`.

**Causa (C):** `templates/base.html` no asigna clases de selección ni `aria-current`. `templates/registros/ficha.html` construye un retorno fijo, sin transportar los filtros de origen.

**Impacto:** al abrir enlaces o alternar pestañas del navegador se debe releer el contenido para ubicarse. Volver desde una ficha no conserva el corte analizado y puede excluir registros no activos. No se encontraron pestañas internas en la aplicación actual.

**Solución:** resolver la sección desde la ruta en el render compartido; marcar el enlace activo con peso 600/700, subrayado o barra visible y `aria-current="page"`. En la ficha mantener «Registros» seleccionado, pudiendo usar `aria-current="location"` para representar la sección contenedora. Mostrar el nombre actual en el encabezado móvil cuando el menú está cerrado. Convertir la miga existente en lista dentro de `nav aria-label="Migas de pan"`, indicando el elemento actual. Transportar un retorno local validado o los parámetros de filtros; no usar un retorno arbitrario externo.

**Aceptación:** cargar directamente cada una de las cuatro secciones y una ficha; comprobar selección coherente en 1440 y 390, con y sin menú desplegado, teclado y escala de grises. Filtrar por sector y período, abrir ficha y volver: URL, filtros y totales del listado conservan el contexto. No añadir migas redundantes a las páginas de primer nivel.

### H02 · P1 · Contraste de texto y foco compartidos

**Componente:** navbar, texto secundario, controles y gráfico.

**Medición:** colores calculados del navegador o colores explícitos de Chart.js; composición alfa sobre el fondo real y luminancia relativa sRGB. Los cocientes se muestran redondeados para lectura, pero se comparan con el umbral sin redondear. Texto normal requiere 4,5:1; texto grande, 3:1; señales gráficas esenciales y de controles, 3:1. Referencias [1] y [2].

| Elemento / estado | Primer plano y fondo | Relación | Evaluación |
|---|---|---:|---|
| Enlaces del menú en reposo, 16 px; usuario/rol, 14 px | Blanco al 55 % sobre `#0b4f4a`; compuesto aprox. `#91b0ae` | ≈4,04:1 | **Falla 1.4.3 AA** para texto normal. No se aplica la excepción del logotipo a estos enlaces. |
| Texto `.text-secondary` sobre fondo general; aviso sintético y párrafos introductorios | `#6c757d` / `#f8f9fa` | 4,4486:1 | **Falla 1.4.3 AA**, aunque se acerque al mínimo. |
| Mismo secundario dentro de tarjeta blanca | `#6c757d` / `#ffffff` | 4,6893:1 | Cumple 1.4.3; no oscurecerlo por una supuesta falla universal. |
| Borde de campos blancos, estado normal | `#dee2e6` / `#ffffff` | 1,3022:1 | Señal débil de identificación; revisar 1.4.11 donde este borde es la única señal del área editable. La etiqueta aporta nombre, no delimita el control. |
| Barra MAB frente al fondo del gráfico | `#5fb3a8` / `#ffffff` | 2,4706:1 | Bajo el objetivo 3:1 para señal gráfica esencial de 1.4.11. La tabla conserva una vía alternativa de lectura. |
| Backlog y Meta del gráfico frente a blanco | `#0b4f4a`; `#c2410c` / blanco | 9,4107:1; 5,1784:1 | Cumplen el umbral gráfico; conservar identidad verde y acento naranja. |
| Advertencias mensuales `.text-warning`, si se generan | `#ffc107` / blanco | 1,6300:1 | **Falla potencial 1.4.3**, identificada en código; no se forzó una advertencia mensual visible en el recorrido. No confundir con badges amarillos de texto oscuro. |

**Foco (N/C):** al tabular a «Registros», el estilo calculado del enlace tiene `outline: none` y una sombra azul al 25 %. La regla Bootstrap de `.nav-link:focus-visible` prevalece sobre el selector global menos específico de `app.css`. Sobre la navbar verde esa sombra es una señal débil; no basta definir un outline global para asegurar que se vea en todos los componentes. Debe verificarse 2.4.7 junto con 1.4.11 [2][4]. No se atribuye a AA el criterio 2.4.13 de apariencia del foco, que es AAA.

**Solución:** definir tokens compartidos de texto secundario, advertencia, borde funcional y foco; configurar variables de Bootstrap desde `static/css/app.css`, sin editar el vendor. Usar texto de menú blanco opaco o una opacidad que supere 4,5:1; oscurecer ligeramente el secundario usado sobre fondo terciario; dar a advertencias texto oscuro con fondo claro. Añadir `.navbar .nav-link:focus-visible` con anillo claro y separación visible, distinguiendo foco y selección. Ajustar MAB con H05.

**Archivos:** `static/css/app.css`, `templates/base.html`, `templates/registros/ficha.html`, `static/js/app.js`.

**Aceptación:** medir cada par real en reposo, hover, foco, seleccionado y error, sobre ambos fondos existentes; texto normal ≥4,5:1 y señales esenciales ≥3:1. Tab por marca, enlaces, menú móvil, botones, campos, tarjetas KPI y cerrar modal: el foco se localiza sin depender del hover. No se exige contraste de control activo a controles deshabilitados ni a divisores puramente decorativos.

### H03 · P1 · Tabla de Parámetros ensancha la página a 320 px

**Ruta:** `/parametros`.

**Evidencia (N):** emulando 320 px, `documentElement.clientWidth=320`, pero `scrollWidth≈340` e `innerWidth≈340`. La tabla «Historia de confiabilidad inicial» llega hasta x≈340; el viewport móvil amplía el área de layout. En 390 px no se reprodujo este desborde global.

**Causa (C):** las tablas de historia de `templates/parametros.html` no tienen el contenedor `.tabla-scroll` usado en las otras vistas.

**Impacto:** obliga a desplazar o reduce la escala aparente de toda la página. La excepción de tablas bidimensionales en 1.4.10 [3] no justifica hacer desbordar la página completa.

**Solución:** envolver cada historia en el patrón de tabla desplazable existente, permitir ajuste de texto en nombres y fechas cuando sea razonable y asegurar que los hijos de columnas puedan encogerse. No ocultar el problema con `overflow-x:hidden` en el body.

**Aceptación:** con semilla y con el nuevo historial de horas, en 320, 390 y 768 px el ancho de documento no excede el ancho de layout. Cada tabla conserva todas sus columnas mediante scroll propio. Verificar además 400 % de zoom real en navegador visible.

### H04 · P1 · Filtros, indicadores y ficha ocultan la tarea principal en móvil

**Rutas:** `/`, `/registros` y `/registros/{id}`.

**Evidencia (N):** a 390 px, el gráfico empieza alrededor de y=1292 y Alertas en y=3966. En la ficha `OPD-0011`, Estado y flujo aparece en y=2093 y Bitácora en y=3412. En 768 px la ficha también queda apilada; sus columnas solo se separan a partir de `xxl` (1400 px). Los filtros compartidos ocupan alrededor de 400 px de altura antes de los indicadores o filas.

**Impacto:** las acciones frecuentes quedan detrás del cálculo de doce meses y la auditoría. Los doce KPI tienen un peso visual similar, aunque Forecast, Meta y Gap responden primero a la pregunta ejecutiva.

**Solución:** conservar componentes y Bootstrap. Mantener visibles período, búsqueda y filtros principales; agrupar el resto en «Más filtros», mostrando cuántos están activos y un resumen persistente. Priorizar Forecast, Meta, Gap y HC, con acceso claro al resto. Añadir en la ficha enlaces internos «Resumen», «Perfiles», «Estado y flujo», «Datos», «Bitácora» y «Auditoría»; colocar un resumen operativo antes de la tabla extensa. Evaluar columnas desde `xl` únicamente si los campos siguen siendo legibles.

**Archivos:** `templates/_filtros.html`, `templates/dashboard.html`, `templates/registros/ficha.html`, `static/css/app.css`.

**Aceptación:** a 390 × 844, con filtros secundarios cerrados, la primera pantalla permite leer el Forecast y reconocer el acceso al gráfico y filtros; cada sección de la ficha se alcanza con un enlace de teclado/toque sin recorrer las tablas anteriores. Los filtros ocultos siguen reflejados en el resumen y conservan sus valores al aplicar y volver. Medidas exactas de posición pueden variar por tipografía y datos; comprobar la tarea, no un número fijo de píxeles.

### H05 · P2 · Gráfico mensual adecuado, con lectura e interacción mejorables

**Ruta/componente:** `/`, «Forecast mensual vs. meta». Es el único gráfico funcional encontrado en las rutas montadas.

**Pregunta que debe responder:** «¿Cuánto Forecast aporta cada mes, cuánto corresponde a Backlog contractual y a MAB, y a qué distancia está de la meta?».

**Evidencia (N):** las barras apiladas muestran composición y la línea muestra Meta. El período figura en el encabezado y los meses incluyen año; el eje vertical parte de cero y usa `$… M`. Hay leyenda con los tres nombres y una tabla con Backlog, MAB, Forecast, Meta y HC. El canvas tiene descripción accesible que remite a la tabla. Esto ya permite consultar cifras sin hover.

**Problemas:** la MAB clara tiene 2,47:1 contra blanco (H02). El eje abrevia «M» sin expandirlo junto al gráfico. El canvas tiene `tabIndex=-1`; la leyenda dibujada y la exploración de puntos no son controles HTML de teclado. En móvil el gráfico ocupa una tarjeta de ancho reducido y la tabla equivalente queda debajo, con scroll horizontal; la configuración no adapta la densidad de etiquetas al ancho. El riesgo de etiquetas densas se infiere del código: no se afirma una superposición concreta no medida.

**Solución:** mantener esta combinación de gráfico; no convertirla en torta, barras al 100 % ni bandas de incertidumbre que los datos no proporcionan. Añadir «Millones de CLP» al eje o subtítulo y el horizonte junto al título. Oscurecer MAB y combinar color con patrón o tratamiento de borde; mantener la línea Meta diferenciada por forma/trazo. Añadir «Ver datos mensuales» con enlace a la tabla y un resumen de brecha. Si se conserva ocultar series desde la leyenda, dar controles HTML equivalentes con nombre y estado; no basta añadir `tabindex` al canvas. Si se desea mostrar valores al tocar, definir selección persistente de mes y probarla físicamente.

**Archivos:** `static/js/app.js`, `templates/dashboard.html`, `static/css/app.css`.

**Aceptación:** para vistas de 3, 6 y 12 meses en 1440 y 390 px se entiende período y unidad, se distinguen las series en escala de grises y se obtiene el valor exacto de cualquier mes sin ratón. Cualquier acción de ocultar/mostrar series puede ejecutarse con teclado y anuncia estado. La tabla mantiene su independencia de Chart.js. El vacío se resuelve con H07.

**Fuera del flujo activo (C):** `templates/registros/calculo.html` contiene otro canvas, `grafico-forecast`, pero no hay ruta montada que use esa plantilla y el JS común solo inicializa `grafico`. No presentarlo como un gráfico visible roto. Si se habilita en el futuro, primero conectar render, datos e inicialización y definir qué añade a la tabla ya existente.

### H06 · P2 · Tablas desplazables difíciles de explorar en móvil

**Rutas:** listado, serie mensual, ficha y auditoría.

**Evidencia (N):** a 390 px, el listado tiene 324 px útiles para una tabla de aproximadamente 986 px; Auditoría con evento, 324 para 902 px; serie mensual, 324 para 472 px. Forecast y estados quedan lejos del código del registro. Los contenedores no declaran nombre accesible ni `tabindex`; algunas tablas tienen enlaces internos y otras no. No se comprobó que todas sean inaccesibles por teclado: versiones modernas de Chrome pueden enfocar algunos contenedores desplazables automáticamente.

**Impacto:** se pierde la relación entre registro y cifra y el gesto horizontal no se anuncia. El scroll interno de una tabla de datos no constituye por sí solo una falla de reflujo.

**Solución:** reutilizar `.tabla-scroll` con un nombre relacionado con su encabezado y foco visible cuando necesite recibir teclado. Añadir indicación de columnas adicionales cuando exista overflow. Mantener código y servicio visibles mediante columna fija o una presentación resumida por registro en móvil, con estado y Forecast antes de columnas secundarias. Añadir encabezados a tablas que hoy no los tienen, como «Principales clientes» y los pipelines, para que cada cifra tenga nombre explícito.

**Archivos:** `templates/dashboard.html`, `templates/registros/lista.html`, `templates/registros/ficha.html`, `templates/auditoria.html`, `static/css/app.css`.

**Aceptación:** llegar al Forecast del mismo registro con toque y con teclado sin perder su identificación; cada cifra tiene encabezado; las regiones no producen trampas de foco ni ensanchan la página. No duplicar dos versiones legibles simultáneamente para lectores de pantalla.

### H07 · P2 · Vacío sin explicar y recuperación inconsistente

**Rutas:** dashboard sin coincidencias, listado y Auditoría.

**Evidencia (N):** la búsqueda `zz-auditoria-sin-resultados` deja todas las barras de ingresos en cero, pero mantiene la línea Meta y un Gap de la meta completa. Los cortes por sector, owner y pipeline quedan con títulos o tablas vacías; no hay mensaje general «sin coincidencias». El listado sí informa «No hay registros con estos filtros». Auditoría muestra «Sin eventos con estos filtros», también en una sesión recién iniciada sin historial, y no tiene una acción Limpiar junto a Filtrar.

**Impacto:** puede confundirse ausencia de coincidencias con un forecast realmente nulo y brecha confirmada, o ausencia de auditoría con filtro incorrecto.

**Solución:** mostrar número de registros en dashboard y un vacío explícito con «Limpiar filtros». Mantener la meta si esa es la regla de negocio, pero explicar que corresponde a los sectores/período y que los filtros de registros pueden no afectarla. Para las tarjetas vacías, usar mensajes breves coherentes. En Auditoría distinguir «sin eventos registrados» de «sin coincidencias» y ofrecer restablecer filtros.

**Archivos:** `templates/dashboard.html`, `templates/registros/lista.html`, `templates/auditoria.html`; contexto en `routes/dashboard.py` y `routes/admin.py` si se necesitan contadores sin filtrar.

**Aceptación:** una búsqueda imposible muestra cero coincidencias y recuperación visible; ningún panel queda solo con encabezado vacío. La meta que permanece se explica junto al resultado. Limpiar Auditoría elimina todos sus filtros y restaura el listado.

### H08 · P2 · Validación resumida sin localizar el campo; preservación desigual

**Rutas:** modal de alta, ficha y Parámetros.

**Evidencia (N):** al enviar un perfil con tarifa e ingreso pero sin HC, el alta vuelve abierta, conserva Servicio y enfoca el resumen «Perfil 1: completa HC y tarifa con números y el ingreso con una fecha válida». Hay `role="alert"`, pero cero campos con `aria-invalid` y ningún enlace desde el resumen al campo. El error no distingue cuál de los tres valores falla.

**Evidencia adicional (C):** `_accion()` devuelve el formulario a `ficha`, pero solo algunos controles usan `form` para restaurarlo. Tarifas, contenido de bitácora y varios datos se renderizan desde el registro o vacíos; `_parametros()` no recibe los valores enviados al fallar. Por ello no está garantizada la conservación de todos los campos tras un error. No se reprodujeron cada uno de esos errores durante el recorrido.

**Impacto:** obliga a localizar una fila lejos del resumen y puede exigir repetir información en formularios extensos.

**Solución:** mantener el resumen enfocado ya existente; devolver errores por campo, dar IDs estables a las filas de perfil y enlazar cada error a su control. Añadir mensaje específico, `aria-invalid` y `aria-describedby`. Conservar los valores del formulario que falló en ficha y parámetros sin copiarlos accidentalmente a otros formularios con nombres repetidos. En conflicto 409, ofrecer revisar datos actuales y conservar el borrador para comparación.

**Archivos:** `templates/registros/nuevo.html`, `templates/registros/ficha.html`, `templates/parametros.html`, `routes/registros.py`, `routes/admin.py`.

**Aceptación:** error de HC identifica y enfoca HC de la fila correcta; un valor inválido de tarifa conserva importe, vigencia y motivo; un rechazo de bitácora conserva contenido y próxima acción; un error de parámetros conserva los tres campos. Verificar 422 y 409 con pruebas enfocadas antes de implementar, según las reglas del repositorio.

### H09 · P2 · Vista previa puede quedar obsoleta sin avisar

**Ruta/componente:** modal, `#vista-previa`.

**Evidencia (N):** tras cargar una vista previa válida, se simuló desconexión y se cambió un campo: el panel conservó el cálculo previo y no apareció una alerta de desconexión. Se verificó ausencia de feedback; no se afirma que se haya guardado un cálculo incorrecto. El cálculo definitivo se ejecuta en servidor.

**Causa (C):** `hx-post` con debounce actualiza el fragmento, pero no hay indicador propio ni manejadores de `htmx:sendError`/`htmx:responseError`; tampoco una marca visible de cálculo pendiente. El preview se solicita incluso cuando el diálogo está cerrado por su trigger `load`.

**Impacto:** las cifras anteriores pueden parecer vigentes mientras la última edición está pendiente o falló.

**Solución:** marcar «Actualizando vista previa…» al iniciar, «No se pudo actualizar» con reintento en error y estado «cálculo anterior» cuando corresponda. Anunciar resultado en región `status` sin mover foco por cada tecla. Evitar solicitudes mientras el modal está cerrado y mostrar feedback de envío en guardados para reducir envíos repetidos.

**Archivos:** `templates/registros/nuevo.html`, `templates/registros/_vista_previa.html`, `static/js/app.js`.

**Aceptación:** con latencia simulada y cambio de tarifa se distingue pendiente de actualizado; en desconexión no queda una cifra vieja presentada como actual. Reintentar actualiza; no mueve foco ni crea un registro. Un guardado correcto mantiene su confirmación existente.

### H10 · P3 · Tema claro fijo; implementar oscuro de forma integral

**Componente:** tema global.

**Evidencia (N/C):** `prefers-color-scheme: dark` se cumple en emulación, pero el fondo sigue claro. No hay selector ni lectura/escritura de preferencia en `app.js`. Bootstrap ya incluye variables y estilos por `data-bs-theme`, por lo que hay una base aprovechable.

**Solución:** selector «Sistema / Claro / Oscuro» accesible en la navegación y disponible con menú móvil. Guardar la elección explícita en almacenamiento local; para Sistema reaccionar a cambios de `matchMedia`. Aplicar tema antes del primer pintado mediante recurso propio compatible con la CSP. Compartir tokens, sin añadir otra librería.

**Adaptaciones necesarias:** fondo general, tarjetas y tablas; textos principales/secundarios; enlaces; bordes y placeholders; select, fechas y campos de solo lectura; badges y alertas de éxito/error/advertencia; hover, selección, disabled y foco; modal/backdrop y vista previa; navbar verde. En Chart.js configurar explícitamente color de textos, leyenda, ticks, grilla, tooltips y series, y actualizar la instancia al cambiar tema: el canvas no hereda automáticamente todo el tema CSS.

**Archivos:** `templates/base.html`, `static/css/app.css`, `static/js/app.js` y marcado de estados en las plantillas que lo necesite.

**Aceptación:** primera visita sigue al sistema; la elección explícita persiste tras recarga y navegación; Sistema vuelve a seguir cambios del SO. Probar gráfico, alta, ficha, Parámetros y Auditoría en ambos temas con la matriz de contraste H02. No introducir un parpadeo claro evidente al cargar el tema oscuro. Esta mejora no es requisito WCAG AA por sí misma.

### H11 · P3 · Favicon vacío

**Evidencia (N/C):** el enlace del DOM y de `templates/base.html` es `data:,`, sin imagen reconocible. Chrome headless no muestra la barra de pestañas: la apariencia de una pestaña visible queda pendiente; el recurso vacío sí está confirmado.

**Solución:** un símbolo simple de Proyecta, con pocos trazos y fondo/contorno que sobreviva sobre pestañas claras y oscuras; SVG y respaldo PNG/ICO de 16/32 px en estáticos. No reducir el nombre completo a 16 px. Mantener la identidad verde existente.

**Archivos:** `templates/base.html` y recursos nuevos dentro de `static/`, únicamente tras aprobar implementación.

**Aceptación:** el recurso responde 200 con tipo de imagen correcto; en navegador visible se reconoce a 16 px, con pestaña clara/oscura y varias pestañas abiertas. Sin solicitud fallida ni cambios de CSP innecesarios.

### H12 · P2 · Errores de URL rompen el lenguaje y la estructura de la web

**Rutas:** `/no-existe` y `/registros/no-es-uuid`.

**Evidencia (N):** la primera muestra tarjeta HTML con «No encontrado», detalle «Not Found» en inglés y retorno al dashboard. La segunda presenta JSON de validación de UUID, sin menú, encabezado ni acción de recuperación; el navegador móvil usa el ancho de layout predeterminado de esa respuesta sin viewport.

**Causa (C):** `src/proyecta/main.py` personaliza `StarletteHTTPException`, pero no la validación de parámetros de FastAPI para rutas web.

**Impacto:** un enlace incorrecto o truncado deja al usuario en una respuesta técnica que no explica cómo continuar.

**Solución:** tratar errores de validación de rutas web con la plantilla compartida y mensaje «El enlace del registro no es válido», enlace a Registros y Dashboard. Mantener JSON para `/api/` y no exponer detalles de implementación al usuario. Traducir el 404 genérico.

**Aceptación:** ID mal formado y UUID válido inexistente producen una página comprensible y navegable en 390 y 1440, con su estado HTTP apropiado; los errores de API siguen estructurados como exige su contrato.

## 5. Plan de trabajo agrupado

Estimaciones de implementación para una persona familiarizada con el repositorio, incluyendo verificaciones focalizadas. Son rangos orientativos, no compromisos de calendario; no incluyen aprobación ni cambios del dominio.

| Orden | Intervención / hallazgos | Impacto | Esfuerzo | Dependencias y comprobación principal |
|---:|---|---|---|---|
| 1 | Navegación compartida, sección actual y retorno filtrado — H01 | Alto | 0,5–1 día | Acordar estado de sección en render común; URL directa, regreso y teclado en móvil/escritorio |
| 2 | Tokens claros, texto secundario, bordes funcionales y foco — H02 | Alto | 0,5–1 día | Sin cambiar vendor; medir matriz real de estados. Definir nombres de tokens reutilizables por H10 |
| 3 | Contención de historia de parámetros y patrón común de tablas — H03/H06 | Alto | 0,5–1,5 días | Reusar `.tabla-scroll`; corregir ancho global primero, luego lectura por registro y teclado |
| 4 | Prioridad móvil y accesos dentro de ficha — H04 | Alto | 1–2 días | Coordinar filtros con conservación de H01; comprobar tareas a 320/390/768/1440 |
| 5 | Validación por campo y conservación de borradores — H08 | Alto al fallar una tarea | 1–2 días | Modelo de errores por formulario; pruebas de 422/409 previas, sin alterar cálculo ni auditoría |
| 6 | Gráfico, tabla equivalente y vacíos coherentes — H05/H07 | Medio-alto | 0,75–1,5 días | Aplicar tokens H02 y layout H04; aclarar alcance actual de metas; teclado y cero coincidencias |
| 7 | Feedback de preview y guardado — H09 | Medio | 0,5–1 día | Coordinar errores con H08; latencia, desconexión, reintento y anuncios sin mover foco |
| 8 | Errores HTML consistentes — H12 | Medio | 0,25–0,5 día | Separación web/API en manejadores; comprobar ID inválido y 404 |
| 9 | Tema Sistema/Claro/Oscuro — H10 | Medio | 1–2 días | Tokens H02 y actualización de Chart.js H05; no hacerlo como inversión global de colores |
| 10 | Favicon — H11 | Bajo; identificación de pestaña | 0,25 día | Símbolo aprobado y revisión en navegador visible |

La primera intervención de accesibilidad debe conservar el salto al contenido, etiquetas visibles y autocompletado del login. También conviene mantener el diálogo nativo, cierre con Escape, mensajes de guardado con `role="status"`, tabla equivalente del gráfico y fórmulas explicadas. Son recursos existentes útiles; no hay motivo observado para reemplazar Bootstrap, HTMX o Chart.js.

Antes de cada implementación de comportamiento, escribir la prueba que reproduzca el defecto cuando corresponda a una historia del repositorio. Después ejecutar las comprobaciones de integración afectadas y el recorrido visual/teclado; si se modifica código de aplicación, completar los checks exigidos por el repositorio. Una futura revisión de accesibilidad debe incluir lector de pantalla, zoom real y móvil físico.

## 6. Referencias y alcance normativo

Las recomendaciones de densidad, prioridad móvil, migas y tema son decisiones de usabilidad; no se presentan automáticamente como incumplimientos WCAG. La ubicación mediante migas no es una obligación general AA. Las mediciones de contraste son comprobaciones concretas, no una declaración de conformidad integral.

1. [W3C — WCAG 2.2, 1.4.3 Contrast (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html): umbrales de texto y excepciones.
2. [W3C — WCAG 2.2, 1.4.11 Non-text Contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html): controles, estados y objetos gráficos necesarios para comprender la información.
3. [W3C — WCAG 2.2, 1.4.10 Reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html): reflujo a 320 px CSS y excepción limitada para contenidos bidimensionales.
4. [W3C — WCAG 2.2, 2.4.7 Focus Visible](https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html): foco visible, relación con contraste y distinción respecto del criterio AAA de apariencia.

**Estado de la entrega:** informe listo para revisión. La modificación de la aplicación queda pendiente de la aprobación solicitada en el prompt.
