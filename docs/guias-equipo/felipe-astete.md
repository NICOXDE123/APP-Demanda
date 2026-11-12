# Felipe Astete — Backend / Estados

## Resultado esperado

Implementar permisos, transiciones y procesos operativos con auditoría, conservando las reglas de negocio y consumiendo el motor único.

**Tareas base:** T028, T040–T041, T052–T059, T061–T063 y T092–T115. **T060:** Bryam implementa y tú revisas su integración. Lee [el flujo común](README.md), `AGENTS.md` y los documentos del frente. Las rutas parten de la raíz.

## Archivos y contenidos

Son entregables previstos. Los nombres abreviados de una fila comparten el directorio del primer archivo, salvo ruta explícita.

| Archivo o grupo | Contenido esperado |
|---|---|
| `src/proyecta/domain/permissions.py` | Políticas por rol/propiedad. Roberto amplía el mismo archivo en T131. |
| `src/proyecta/domain/registro_code.py`; `registro_rules.py` | Código `OPD-####`, obligatorios, fechas, catálogos y coherencia del registro. |
| `src/proyecta/domain/states.py`; `rules.py` | Transiciones, requisitos, pausa/reapertura y probabilidad/confiabilidad con vigencia mensual. |
| `src/proyecta/application/use_cases/estados.py`; `bitacora.py` | Transiciones con motivo/auditoría; nuevas entradas y correcciones de bitácora por referencia. |
| `src/proyecta/interfaces/api/v1/estados.py`; `bitacora.py` | Validación HTTP, autorización y llamada a casos de uso según OpenAPI. |
| `src/proyecta/application/use_cases/backlog.py`; `metas.py` | Contratos, renovación/cierre, vencimientos y metas por sector/mes; orquestación del cálculo de gap/cobertura. |
| `src/proyecta/interfaces/api/v1/contratos.py`; `metas.py` | Endpoints protegidos de contratos y metas. |
| `src/proyecta/interfaces/web/templates/contratos/form.html`; `src/proyecta/interfaces/web/templates/metas/index.html` | Formularios/vistas de US5; coordinar estilos con Bryam. |
| `src/proyecta/infrastructure/datastore/corte_repository.py` | Continuación T108 del repositorio iniciado por Matías en T023. |
| `src/proyecta/application/use_cases/cierre.py` | Cierre por lotes, estados `CREANDO`/`CERRADO`/`ERROR`, reintento idempotente e inmutabilidad. |
| `src/proyecta/domain/engine/puente.py` | Descomposición de variación y línea de redondeo; Nicolás revisa el contrato con el motor. |
| `src/proyecta/interfaces/api/v1/cortes.py`; `src/proyecta/interfaces/web/templates/cortes/index.html` | API y vista de cortes/comparación. |
| `tests/unit/domain/test_states.py`; `test_gap.py`; `test_puente.py` | Transiciones, gap/cobertura y determinismo del puente. |
| `tests/contract/test_estados.py`; `test_backlog_metas.py`; `test_cortes.py` | Contratos de US2, US5 y US6. |
| `tests/integration/test_lifecycle.py`; `test_backlog.py`; `test_cierre.py` | Ciclo completo, vencimientos/metas y cierre/idempotencia. |

## Orden de ejecución

1. Entrega T028 durante Fundación y acuerda con Matías cómo aplicar permisos.
2. Implementa T040–T041 para que Bryam integre altas y validadores.
3. Completa US2 empezando por pruebas. Entrega a Bryam los casos de uso y errores que necesita T060.
4. Después de US1 y US3, implementa US5. Usa los cálculos de Nicolás para evitar fórmulas divergentes.
5. Después de US3 y US5, implementa US6. Coordina T108 con Matías y T110 con Nicolás antes de editar sus archivos.

## Validación y entrega

Prueba adjudicación con P=100 %, motivos obligatorios, StandBy, cancelación según motivo y vigencias históricas. La bitácora debe rechazar edición/borrado. La falta de meta produce DQ-12; el cierre repetido no duplica datos y la suma del puente coincide con la variación.

Ejecuta estas suites cuando los archivos y dependencias estén implementados:

```powershell
uv run pytest tests/unit/domain/test_states.py tests/contract/test_estados.py tests/integration/test_lifecycle.py -q
uv run pytest tests/unit/domain/test_gap.py tests/contract/test_backlog_metas.py tests/integration/test_backlog.py -q
uv run pytest tests/unit/domain/test_puente.py tests/contract/test_cortes.py tests/integration/test_cierre.py -q
```

Entrega a Bryam contratos de acciones/errores; a Nicolás, vigencias y datos de corte; a Roberto, casos de permisos e inmutabilidad. Registra las verificaciones que el entorno no permita ejecutar.

## Prompt personal para una IA

Añade al prompt común:

```text
Soy Felipe Astete, responsable de Backend / Estados.
Lee docs/guias-equipo/felipe-astete.md.
Primer lote: T028, comprobando los contratos de dominio de Fundación.
Implementa políticas por rol y propiedad con casos permitidos y denegados de spec.md.
Mantén el dominio libre de HTTP y Datastore y documenta su interfaz para Matías.
No implementes aún las historias que dependen de Fundación incompleta.
```

## Catálogo de tareas del frente

Detalle tomado de `specs/001-proyecta-mvp/tasks.md` al preparar esta guía. Ese archivo conserva el estado oficial y las dependencias; si cambia, actualiza este catálogo. Las rutas abreviadas se interpretan con el directorio de la primera ruta y la tabla de archivos anterior. Las etiquetas [P] no permiten omitir dependencias ni editar un archivo compartido al mismo tiempo.

- **T028**: Implementar políticas de rol y propiedad en `src/proyecta/domain/permissions.py`.
- **T040**: [P] [US1] Generador de código `OPD-####` en `src/proyecta/domain/registro_code.py`.
- **T041**: [P] [US1] Validadores de registro, fechas y catálogos en `src/proyecta/domain/registro_rules.py`.
- **T052**: [P] [US2] Contrato de `/estado`, `/flujo` y `/bitacora` en `tests/contract/test_estados.py`.
- **T053**: [P] [US2] Unitarias de la máquina de estados en `tests/unit/domain/test_states.py`.
- **T054**: [P] [US2] Integración del ciclo de vida en `tests/integration/test_lifecycle.py`.
- **T055**: [P] [US2] Máquina de estados y transiciones en `src/proyecta/domain/states.py`.
- **T056**: [P] [US2] Reglas de probabilidad y confiabilidad con vigencia mensual en `src/proyecta/domain/rules.py`.
- **T057**: [US2] Caso de uso de transición de estado y flujo en `src/proyecta/application/use_cases/estados.py`.
- **T058**: [US2] Caso de uso de bitácora y correcciones por referencia en `src/proyecta/application/use_cases/bitacora.py`.
- **T059**: [US2] Rutas API de estado, flujo y bitácora en `src/proyecta/interfaces/api/v1/estados.py` y `bitacora.py`.
- **T061**: [US2] Integrar auditoría de estado, tipo, flujo, P y C en `src/proyecta/application/use_cases/estados.py`.
- **T062**: [US2] Pruebas de adjudicación al 100 %, StandBy, cancelación por motivo (AC-16) y transiciones inválidas en `tests/integration/test_lifecycle.py`.
- **T063**: [US2] Ejecutar la suite de US2 y corregir fallos en `tests/contract/test_estados.py` y `tests/integration/test_lifecycle.py`.
- **T092**: [P] [US5] Contrato de `/contratos` y `/metas` en `tests/contract/test_backlog_metas.py`.
- **T093**: [P] [US5] Unitarias de gap y cobertura en `tests/unit/domain/test_gap.py`.
- **T094**: [P] [US5] Integración de continuidad y Backlog en `tests/integration/test_backlog.py`.
- **T095**: [US5] Caso de uso de contrato, renovación y cierre en `src/proyecta/application/use_cases/backlog.py`.
- **T096**: [US5] Caso de uso de metas por sector/mes en `src/proyecta/application/use_cases/metas.py`.
- **T097**: [US5] Cálculo de Backlog contractual y vencimientos en `src/proyecta/application/use_cases/backlog.py`.
- **T098**: [US5] Cálculo de gap y cobertura en `src/proyecta/application/use_cases/metas.py`.
- **T099**: [US5] Rutas API de contratos y metas en `src/proyecta/interfaces/api/v1/contratos.py` y `metas.py`.
- **T100**: [P] [US5] Plantilla de contrato en `src/proyecta/interfaces/web/templates/contratos/form.html`.
- **T101**: [P] [US5] Plantilla de metas y gap en `src/proyecta/interfaces/web/templates/metas/index.html`.
- **T102**: [US5] Alertas de vencimiento y `DQ-12` en `src/proyecta/application/use_cases/backlog.py`.
- **T103**: [US5] Pruebas de alertas, meta faltante y contrato vencido en `tests/integration/test_backlog.py`.
- **T104**: [US5] Ejecutar la suite de US5 y corregir fallos en `tests/contract/test_backlog_metas.py` y `tests/integration/test_backlog.py`.
- **T105**: [P] [US6] Contrato de `/cortes` y `/puente` en `tests/contract/test_cortes.py`.
- **T106**: [P] [US6] Unitarias del puente por categoría en `tests/unit/domain/test_puente.py`.
- **T107**: [P] [US6] Integración de cierre e idempotencia en `tests/integration/test_cierre.py`.
- **T108**: [US6] Repositorio de corte y detalle en `src/proyecta/infrastructure/datastore/corte_repository.py`.
- **T109**: [US6] Servicio de cierre por lotes con estados `CREANDO`/`CERRADO`/`ERROR` en `src/proyecta/application/use_cases/cierre.py`.
- **T110**: [US6] Cálculo del puente en `src/proyecta/domain/engine/puente.py`.
- **T111**: [US6] Rutas API de cortes y puente en `src/proyecta/interfaces/api/v1/cortes.py`.
- **T112**: [US6] Plantilla de cortes y comparación en `src/proyecta/interfaces/web/templates/cortes/index.html`.
- **T113**: [US6] Inmutabilidad del corte cerrado y reintento idempotente en `src/proyecta/application/use_cases/cierre.py`.
- **T114**: [US6] Pruebas de AC-08 y línea de redondeo en `tests/integration/test_cierre.py`.
- **T115**: [US6] Ejecutar la suite de US6 y corregir fallos en `tests/contract/test_cortes.py` y `tests/integration/test_cierre.py`.
