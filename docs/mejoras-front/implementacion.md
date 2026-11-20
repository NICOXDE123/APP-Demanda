# Mejora visual de Proyecta

Se aplicó el prompt de esta carpeta con la skill `ui-ux-pro-max` al frontend
Jinja2 + Bootstrap + Chart.js. Alcance acordado: notebooks y computadores;
la implementación móvil queda para versiones futuras.

## Cambios

- Tokens semánticos con variantes claras y oscuras: fondo, tarjetas elevadas,
  bordes, sombras, filas alternadas, hover y estados.
- Indicadores con borde superior por categoría, etiquetas en mayúsculas,
  cifras de 24–32 px y números tabulares. Forecast muestra cobertura real y Gap
  identifica superávit o brecha. No se inventan comparaciones con meses anteriores.
- Backlog con gradiente vertical y MAB con gradiente tramado para distinguir las
  series sin depender del color. Meta con puntos delineados, línea discontinua
  y tooltips que muestran las series del mes juntas. Se conservan controles
  por teclado, selección de series y preferencia de tema al redibujar.
- Píldoras con texto para tipo y estado de registros; los cambios de estado
  en auditoría reutilizan la misma presentación. Otros campos conservan su valor.
- Tablas con filas alternadas, hover y foco de fila, cabeceras diferenciadas
  y totales destacados. Se conservan las regiones de desplazamiento horizontal.
- En notebooks de 1200–1599 px el gráfico y la serie mensual ocupan filas
  separadas; en monitores más amplios se muestran juntos. Sin cambios de cálculo,
  permisos, persistencia ni auditoría del negocio.

## Validación

- Python 3.12: `109 passed` con cobertura del dominio de `92,86 %` (mínimo 90 %).
- `node tests/e2e/verificar_frontend.cjs`: correcto en Chrome/Edge headless,
  con datos sintéticos locales, ambos temas y anchos de 1280, 1366, 1440 y 1920 px.
- Verificados contraste de texto secundario, navegación, pestaña activa y estados;
  contraste de bordes y MAB; separación de superficies; cifras sin desbordes;
  gradientes/trama; persistencia del tema y selección de series; formularios,
  conservación de borradores y recuperación de vista previa tras desconexión.
- Sin excepciones JavaScript. `git diff --check` sin errores.
- Capturas revisadas del dashboard, gráfico y registros; auditoría capturada con
  la semilla local (sin eventos). El flujo E2E no crea cambios de estado válidos,
  por lo que las píldoras de eventos se revisan con los mismos tokens del listado.

## Capturas

| Vista | Claro | Oscuro |
|---|---|---|
| Dashboard · notebook 1366 px | [Claro](evidencias/dashboard-light-1366.png) | [Oscuro](evidencias/dashboard-dark-1366.png) |
| Gráfico · 1440 px | [Claro](evidencias/grafico-claro.png) | [Oscuro](evidencias/grafico-oscuro.png) |
| Registros · 1440 px | [Claro](evidencias/registros-light.png) | [Oscuro](evidencias/registros-dark.png) |
| Auditoría · 1440 px | [Claro](evidencias/auditoria-light.png) | [Oscuro](evidencias/auditoria-dark.png) |
