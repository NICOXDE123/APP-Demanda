# Revisión UX/UI del mockup Proyecta

Fecha: 12 de noviembre de 2026.

Se ejecutó [prompt.md](prompt.md) sobre [proyecta-mvp-mockup.html](proyecta-mvp-mockup.html), utilizando [UI UX Pro Max](../../.agents/skills/ui-ux-pro-max/SKILL.md). Se consultaron sus recomendaciones locales sobre foco de teclado, foco no oculto y validación con resumen de errores.

## Propósito y usuarios

El mockup permite analizar ingresos proyectados y capacidad, y pasar de indicadores a registros de la cartera. Operaciones tiene control global y parámetros; los líderes gestionan su cartera; los ejecutivos consultan en lectura. La acción principal del tablero es explorar los registros detrás de una cifra; en la cartera es consultar, crear o actualizar un registro según el perfil.

## Problemas observados y mejoras

| Prioridad | Problema observado | Cambio implementado |
|---|---|---|
| Alta | Diálogos sin gestión de foco, cierre por Escape ni aislamiento del fondo. | Semántica de diálogo, foco inicial, recorrido contenido con Tab/Shift+Tab, fondo inerte y retorno al control de origen. |
| Alta | Filas y barras del gráfico dependían del clic. | Acceso con teclado mediante Enter/Espacio y nombres accesibles. |
| Alta | Filtros sin etiquetas visibles y controles pequeños. | Etiquetas persistentes, controles de al menos 44 px y estados de foco visibles. |
| Alta | La tabla podía ensanchar toda la página en tablet. | Contenedores ajustables y desplazamiento horizontal localizado en regiones accesibles. |
| Alta | La tarjeta MAB abría solo confirmados, aunque su cifra corresponde a todos los activos. | El acceso muestra los registros activos que componen el indicador. |
| Media | Errores del formulario agrupados sin asociación con los campos. | Resumen enlazado, indicaciones junto a los campos y atributos `aria-invalid`/`aria-describedby`. El guardado conserva su bloqueo mientras faltan datos. |
| Media | El gráfico no ofrecía una alternativa textual completa. | Tabla desplegable con mes, demandas, oportunidades y total en CLP. |
| Media | Texto secundario tenue, indicadores densos y ausencia de título por vista. | Colores secundarios más legibles en ambos temas, jerarquía de títulos, mayor espacio y cifras destacadas. |
| Media | La navegación y los formularios no se adaptaban suficientemente al teléfono. | Navegación en dos columnas, filtros redistribuidos y perfiles del formulario en una columna. |
| Media | Alertas dependientes del color y cambios dinámicos sin anuncio. | Texto junto al indicador de calidad, regiones de estado y anuncio contextual de resultados. |

Se conservaron la identidad verde, tipografías, datos de demostración, fórmulas y módulos existentes. No se añadieron dependencias de frontend ni servicios externos. El mockup indica que los cambios son temporales. Se respeta la preferencia de movimiento reducido.

## Archivos

- `proyecta-mvp-mockup.html`: contenido, etiquetas y puntos de integración.
- `proyecta-mvp-ux.css`: ajustes visuales y adaptaciones de pantalla.
- `proyecta-mvp-ux.js`: accesibilidad, contexto de vistas y validación visual.
- `verificar-mockup.cjs`: comprobación reproducible con Chrome o Edge en modo headless; requiere Node.js con `fetch` y `WebSocket` globales (verificado con Node 24).

Para abrir la propuesta, conservar el HTML, CSS y JS en esta misma carpeta y abrir el HTML en el navegador.

## Verificaciones realizadas

Ejecutar desde la raíz:

```powershell
node docs/mockups/verificar-mockup.cjs
```

Resultado: comprobación satisfactoria en Chrome, sin excepciones JavaScript detectadas.

- Dashboard, cartera, auditoría y parámetros sin desbordamiento de página a **1440, 768, 390 y 320 px**: 16 combinaciones.
- Tabla alternativa del gráfico con tantas filas como meses del horizonte.
- Acceso desde MAB a cartera activa y búsqueda con resultado vacío.
- Formulario inválido bloqueado, campos señalados y creación de un registro sintético válido.
- Diálogo con foco contenido, Tab/Shift+Tab, cierre con Escape y retorno al control de origen.
- Apertura de filas con Enter, restricciones visibles para Ejecutivo y filtro propio para Líder.
- Exportación CSV con el registro creado, cambio a tema oscuro y selector de perfiles.
- Formulario móvil sin desbordamiento horizontal.

Las capturas y el resultado se generan en `.verificacion/`, excluida de Git. Se inspeccionaron visualmente capturas del tablero de escritorio y teléfono y del formulario móvil.

## Límites y pendientes

- La validación corresponde al mockup local. No demuestra conexión con backend, autenticación real ni persistencia.
- No se realizó una auditoría WCAG completa, prueba con lector de pantalla, dispositivos físicos ni comparación entre navegadores. Los cambios de contraste requieren medición exhaustiva antes de producción.
- No se probaron exhaustivamente todas las transiciones de estado, combinaciones de negocio ni modificaciones de parámetros; se conserva su implementación existente.
- Las acciones son locales y sin solicitudes asíncronas: no se añadieron esperas o estados de carga ficticios. Los errores de red y la carga deberán verificarse al integrar servicios reales.
- Las fuentes de Google conservan su dependencia de red y disponen de fuentes alternativas del sistema.
