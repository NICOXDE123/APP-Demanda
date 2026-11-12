# Leonardo Aguilera — UI / Dashboards

## Resultado esperado

Construir un dashboard explicable y reportes que respeten filtros y permisos. Tu frente incluye proyección de lectura, backend del dashboard y exportación, además de las vistas.

**Tareas base:** T080–T091 y T134–T141. Lee [el flujo común](README.md), `AGENTS.md` y los documentos del frente. Todas las rutas parten de la raíz.

## Archivos y contenidos

Son entregables previstos; inspecciona su existencia. Los nombres abreviados de una fila comparten el directorio del primer archivo.

| Archivo o grupo | Contenido esperado |
|---|---|
| `src/proyecta/infrastructure/datastore/dashboard_repository.py` | Persistencia/consultas de `ResumenMensual`, con filtros e índices. |
| `src/proyecta/application/use_cases/dashboard.py` | Agregación de los 11 indicadores, filtros y detalle sobre registros visibles; consumir el motor. |
| `src/proyecta/interfaces/api/v1/dashboard.py` | API del dashboard, validación y control de acceso según OpenAPI. |
| `src/proyecta/interfaces/web/templates/dashboard/index.html`; `detail.html` | Indicadores/filtros y navegación desde cada cifra hasta los registros que la explican. |
| `src/proyecta/interfaces/web/static/js/dashboard.js` | Gráficos Chart.js y series; presentar resultados calculados en el servidor. |
| `scripts/rebuild_resumen.py` | CLI para reconstruir la proyección y comunicar sus resultados. |
| `src/proyecta/application/use_cases/reportes.py` | Consultas R-01 a R-13 con los mismos filtros y permisos del dashboard. |
| `src/proyecta/infrastructure/export/xlsx.py` | Escritura XLSX en streaming, sanitización de fórmulas y filtrado por owner. |
| `src/proyecta/interfaces/api/v1/exportaciones.py` | Descarga con validación de filtros y autorización. |
| `src/proyecta/interfaces/web/templates/registros/list.html` | Integración de botones de exportación T139, coordinada con Bryam. |
| `tests/contract/test_dashboard.py`; `tests/integration/test_dashboard.py` | Contrato, totales, filtros y detalle. |
| `tests/integration/test_dashboard_perf.py` | Medición reproducible con 1.000 registros y 300 activos. |
| `tests/contract/test_export.py`; `tests/integration/test_export.py` | Formato XLSX, permisos, filtros e intentos de inyección de fórmulas. |

## Orden de ejecución

1. Revisa los resultados del motor con Nicolás y las políticas con Felipe. Comprueba que Fundación esté completa antes de iniciar US4.
2. Con US3 disponible, escribe T080–T081 y construye proyección, agregación, API y vistas.
3. Acuerda con los autores de escrituras cómo mantener `ResumenMensual` actualizado; agrega reconstrucción y compara resultados con el motor.
4. Ejecuta T090 y registra p95, datos, entorno y resultados. Coordina índices y consultas con Matías.
5. Después de US4 y US6, implementa US9: reportes y exportación segura. Coordina T139 con Bryam antes de modificar `registros/list.html`.

## Validación y entrega

Cada indicador debe permitir rastrear su cifra. Un líder solo ve sus registros en listados, totales, detalle y exportaciones. Backlog confirmado es una vista de MAB: no sumarlo como bolsa adicional. Objetivo de T090: dashboard <2 s p95 con el conjunto especificado.

Cuando estén implementadas las tareas, ejecuta:

```powershell
uv run pytest tests/contract/test_dashboard.py tests/integration/test_dashboard.py tests/integration/test_dashboard_perf.py -q
uv run pytest tests/contract/test_export.py tests/integration/test_export.py -q
```

Adjunta capturas y evidencia de filtros, detalle, exportación y rendimiento. Nicolás revisa coherencia numérica; Roberto, permisos/exportaciones; Bryam, componentes y navegación. Entrega instrucciones para reconstruir la proyección.

## Prompt personal para una IA

Añade al prompt común:

```text
Soy Leonardo Aguilera, responsable de UI / Dashboards.
Lee docs/guias-equipo/leonardo-aguilera.md.
Primer lote: T080, después de verificar Fundación y el contrato del motor.
Escribe pruebas de contrato de /dashboard basadas en OpenAPI, roles y filtros.
No inventes campos o cifras ni dupliques fórmulas en JavaScript.
Documenta las dependencias que faltan y el contrato esperado de Nicolás.
```

## Catálogo de tareas del frente

Detalle tomado de `specs/001-proyecta-mvp/tasks.md` al preparar esta guía. Ese archivo conserva el estado oficial y las dependencias; si cambia, actualiza este catálogo. Las rutas abreviadas se interpretan con el directorio de la primera ruta y la tabla de archivos anterior. Las etiquetas [P] no permiten omitir dependencias ni editar un archivo compartido al mismo tiempo.

- **T080**: [P] [US4] Contrato de `/dashboard` en `tests/contract/test_dashboard.py`.
- **T081**: [P] [US4] Integración de totales, filtros y detalle en `tests/integration/test_dashboard.py`.
- **T082**: [P] [US4] Repositorio y proyección `ResumenMensual` en `src/proyecta/infrastructure/datastore/dashboard_repository.py`.
- **T083**: [P] [US4] Servicio de agregación del dashboard en `src/proyecta/application/use_cases/dashboard.py`.
- **T084**: [US4] Ruta API de dashboard en `src/proyecta/interfaces/api/v1/dashboard.py`.
- **T085**: [US4] Filtros y totales sobre registros visibles en `src/proyecta/application/use_cases/dashboard.py`.
- **T086**: [P] [US4] Plantilla del dashboard con los 11 datos en `src/proyecta/interfaces/web/templates/dashboard/index.html`.
- **T087**: [P] [US4] Componentes Chart.js y series en `src/proyecta/interfaces/web/static/js/dashboard.js`.
- **T088**: [US4] Parciales de detalle y navegación hasta el registro en `src/proyecta/interfaces/web/templates/dashboard/detail.html`.
- **T089**: [US4] Comando de reconstrucción de `ResumenMensual` en `scripts/rebuild_resumen.py`.
- **T090**: [US4] Prueba de rendimiento con 1.000 registros y 300 activos en `tests/integration/test_dashboard_perf.py`.
- **T091**: [US4] Ejecutar la suite de US4 y corregir fallos en `tests/contract/test_dashboard.py` y `tests/integration/test_dashboard.py`.
- **T134**: [P] [US9] Contrato de exportación en `tests/contract/test_export.py`.
- **T135**: [P] [US9] Integración de `.xlsx`, permisos e inyección de fórmulas en `tests/integration/test_export.py`.
- **T136**: [US9] Escritor `.xlsx` en streaming en `src/proyecta/infrastructure/export/xlsx.py`.
- **T137**: [US9] Consultas de reportes `R-01` a `R-13` en `src/proyecta/application/use_cases/reportes.py`.
- **T138**: [US9] Rutas API de exportación en `src/proyecta/interfaces/api/v1/exportaciones.py`.
- **T139**: [US9] Botones y enlaces de exportación en `src/proyecta/interfaces/web/templates/dashboard/index.html` y `registros/list.html`.
- **T140**: [US9] Sanitización de fórmulas y filtrado por owner en `src/proyecta/infrastructure/export/xlsx.py`.
- **T141**: [US9] Ejecutar la suite de US9 y corregir fallos en `tests/contract/test_export.py` y `tests/integration/test_export.py`.
