# Nicolás Huenchual — Líder Backend / Motor / IA

## Resultado esperado

Entregar contratos de dominio y un motor único, determinista y explicable. La IA del producto y la carga ampliada son frentes opcionales posteriores al MVP; trabajar con una IA para programar no exige activar la IA del producto.

**Tareas base:** T012–T017, T035, T064–T079 y T142–T149. **Complementarias propuestas:** T150–T156 y T165. Lee [el flujo común](README.md), `AGENTS.md` y los documentos del frente. Las rutas parten de la raíz.

## Archivos y contenidos

Son entregables previstos; inspecciona cuáles existen. Los nombres abreviados de una fila comparten el directorio del primer archivo, salvo ruta explícita.

| Archivo o grupo | Contenido esperado |
|---|---|
| `src/proyecta/domain/enums.py`; `value_objects.py`; `entities.py`; `errors.py` | Enums; Money/Percentage/Period/DateRange; entidades del modelo; excepciones y códigos estables. |
| `src/proyecta/application/ports.py` | Contratos de repositorio, reloj, exportación e IA compartidos por casos de uso y adaptadores. |
| `src/proyecta/domain/engine/active_fraction.py`; `base.py` | Fracción activa por días, prorrateo y Base mensual, con redondeo explícito. |
| `src/proyecta/domain/engine/bags.py`; `headcount.py`; `gap.py` | MAB/Backlog/Forecast sin doble conteo; HC y Altas/Bajas/Cierre; gap/cobertura. |
| `src/proyecta/domain/engine/vigencias.py`; `service.py` | Resolución mensual de P/C/horas y fachada con contrato de resultados y componentes explicables. |
| `src/proyecta/application/use_cases/calculo.py`; `src/proyecta/interfaces/api/v1/forecast.py` | Orquestación del motor, previsualización sin persistencia y API de serie/detalle. |
| `src/proyecta/interfaces/web/templates/registros/calculo.html` | Serie de doce meses y detalle de componentes; coordinar integración visual con Bryam. |
| `src/proyecta/application/services/audit.py` | T077 integra impacto MAB/Forecast sobre el servicio de Roberto. Acordar interfaz antes de editar. |
| `src/proyecta/infrastructure/ai/vertex.py` | Adaptador Vertex AI detrás del puerto y del flag de configuración. |
| `src/proyecta/application/use_cases/ia.py`; `simulacion.py` | Sugerencias con citas/aprobación y simulación aislada en memoria. |
| `src/proyecta/interfaces/api/v1/ia.py`; `src/proyecta/interfaces/web/templates/sugerencias/index.html` | API/vista opcionales con etiquetas de origen y estados claros. |
| `src/proyecta/seed/synthetic.py`; `fixtures.py` | Generador inicial/ampliado y fixture de cuatro registros ficticios con inconsistencias. |
| `src/proyecta/application/use_cases/carga.py`; `scripts/seed_synthetic.py` | Carga idempotente, errores por fila y CLI de datos sintéticos. |
| `docs/demo.md` | Contribución T165: preparación de datos y pasos reproducibles; Alfredo coordina el guion final. |
| `tests/unit/domain/test_engine_cases.py`; `test_engine_rounding.py`; `tests/integration/test_forecast.py` | Los dos primeros en unit/domain/: C-01 a C-08 y redondeo. Integración: serie y vigencias. |
| `tests/integration/test_ia_sim.py`; `test_seed.py` | No escritura autónoma, simulación aislada, operación sin IA e idempotencia de la carga. |

## Orden de ejecución

1. Durante Fundación entrega enums, value objects, entidades, errores y puertos a Matías y Felipe. T014/T015 comparten archivo: ejecutarlas en secuencia.
2. Prepara datos sintéticos mínimos T035. Con Fundación y US1/US2 disponibles, inicia US3 escribiendo C-01 a C-08.
3. Implementa módulos, vigencias, fachada, previsualización y auditoría. Entrega contratos de resultados a Leonardo y Felipe.
4. Apoya a Felipe con T110: puente y reconciliación; evita editar sus archivos simultáneamente.
5. Con US3 validada, implementa IA/simulación solo si se comprometen. Después de US1 puede abordarse la carga ampliada US11. Coordina T165 con Alfredo.

## Validación y entrega

Usa `Decimal` para cálculo y enteros CLP/centavos/puntos base para almacenamiento. Respeta las vigencias de cada mes. Backlog confirmado es vista de MAB; Continuidad aporta al contractual. No uses `float` para dinero ni reescribas meses anteriores con parámetros nuevos.

Cuando las tareas y dependencias estén disponibles:

```powershell
uv run pytest tests/unit/domain/test_engine_cases.py tests/unit/domain/test_engine_rounding.py tests/integration/test_forecast.py -q
uv run pytest --cov=proyecta.domain --cov-fail-under=90
uv run pytest tests/integration/test_ia_sim.py tests/integration/test_seed.py -q
```

La última suite corresponde a los frentes opcionales. Demuestra que la simulación no persiste ni cambia estados y que el MVP funciona con IA apagada. Roberto revisa regresiones; entrega ejemplos sintéticos y resultados explicables a los consumidores.

## Prompt personal para una IA

Añade al prompt común:

```text
Soy Nicolás Huenchual, responsable de dominio, motor e IA.
Lee docs/guias-equipo/nicolas-huenchual.md.
Primer lote: T012, comprobando Setup.
Define enums según data-model.md y OpenAPI, conservando sus valores de contrato.
No agregues roles ni estados nuevos. Expón contradicciones con referencias.
Entrega las pruebas pertinentes y el contrato que utilizarán Matías y Felipe.
```

## Catálogo de tareas del frente

Detalle tomado de `specs/001-proyecta-mvp/tasks.md` al preparar esta guía. Ese archivo conserva el estado oficial y las dependencias; si cambia, actualiza este catálogo. Las rutas abreviadas se interpretan con el directorio de la primera ruta y la tabla de archivos anterior. Las etiquetas [P] no permiten omitir dependencias ni editar un archivo compartido al mismo tiempo.

- **T012**: Crear enums de dominio (`Tipo`, `Estado`, `Flujo`, `Rol`, `Modalidad`, `Origen`, `Bucket`) en `src/proyecta/domain/enums.py`.
- **T013**: Crear value objects `Money`, `Percentage`, `Period` y `DateRange` en `src/proyecta/domain/value_objects.py`.
- **T014**: Crear entidades `Usuario`, `Registro`, `Perfil`, `TarifaPerfil`, `AjusteHC` y `Contrato` en `src/proyecta/domain/entities.py`.
- **T015**: Crear entidades `VigenciaEstadoCalculo`, `Bitacora`, `EventoAuditoria`, `Parametro`, `Catalogo`, `MetaComercial`, `Corte`, `CorteDetalle`, `SugerenciaIA` y `Sesion` en `src/proyecta/domain/entities.py`.
- **T016**: Crear excepciones y códigos de error de dominio en `src/proyecta/domain/errors.py`.
- **T017**: Definir puertos de repositorio, reloj, exportación e IA en `src/proyecta/application/ports.py`.
- **T035**: Crear el esqueleto del generador sintético y los fixtures base en `src/proyecta/seed/synthetic.py`.
- **T064**: [P] [US3] Unitarias de C-01 a C-08 en `tests/unit/domain/test_engine_cases.py`.
- **T065**: [P] [US3] Unitarias de prorrateo y redondeo en `tests/unit/domain/test_engine_rounding.py`.
- **T066**: [P] [US3] Integración de la serie de 12 meses en `tests/integration/test_forecast.py`.
- **T067**: [P] [US3] Fracción activa por días en `src/proyecta/domain/engine/active_fraction.py`.
- **T068**: [P] [US3] Cálculo de Base mensual en `src/proyecta/domain/engine/base.py`.
- **T069**: [P] [US3] MAB, Backlog contractual, Backlog confirmado y Forecast en `src/proyecta/domain/engine/bags.py`.
- **T070**: [P] [US3] HC proyectado y grilla Altas/Bajas/Cierre en `src/proyecta/domain/engine/headcount.py`.
- **T071**: [P] [US3] Gap y cobertura en `src/proyecta/domain/engine/gap.py`.
- **T072**: [US3] Fachada del motor y contrato de resultados en `src/proyecta/domain/engine/service.py`.
- **T073**: [US3] Resolución de vigencias de P, C y horas en `src/proyecta/domain/engine/vigencias.py`.
- **T074**: [US3] Caso de uso de cálculo y previsualización en `src/proyecta/application/use_cases/calculo.py`.
- **T075**: [US3] Rutas API de forecast y detalle en `src/proyecta/interfaces/api/v1/forecast.py`.
- **T076**: [US3] Plantilla de serie y detalle de cálculo en `src/proyecta/interfaces/web/templates/registros/calculo.html`.
- **T077**: [US3] Integrar impacto MAB/Forecast en la auditoría en `src/proyecta/application/services/audit.py`.
- **T078**: [US3] Pruebas de horas con vigencia (AC-17) y P/C con vigencia en `tests/integration/test_forecast.py`.
- **T079**: [US3] Ejecutar la suite de US3 y corregir fallos en `tests/unit/domain/test_engine_cases.py` y `tests/integration/test_forecast.py`.
- **T142**: [P] [US10] Integración de sugerencias y simulación en `tests/integration/test_ia_sim.py`.
- **T143**: [P] [US10] Puerto de IA y adaptador Vertex AI en `src/proyecta/infrastructure/ai/vertex.py`.
- **T144**: [US10] Caso de uso de sugerencias con cita y aprobación en `src/proyecta/application/use_cases/ia.py`.
- **T145**: [US10] Caso de uso de simulación en memoria en `src/proyecta/application/use_cases/simulacion.py`.
- **T146**: [US10] Rutas API de IA y simulación en `src/proyecta/interfaces/api/v1/ia.py`.
- **T147**: [US10] Pantalla opcional de sugerencias en `src/proyecta/interfaces/web/templates/sugerencias/index.html`.
- **T148**: [US10] Pruebas de no escritura, etiquetas y funcionamiento sin IA en `tests/integration/test_ia_sim.py`.
- **T149**: [US10] Ejecutar la suite de US10 y corregir fallos en `tests/integration/test_ia_sim.py`.
- **T150** **(asignación complementaria propuesta)**: [P] [US11] Integración de la carga sintética en `tests/integration/test_seed.py`.
- **T151** **(asignación complementaria propuesta)**: [US11] Generador de 1.000 registros sintéticos en `src/proyecta/seed/synthetic.py`.
- **T152** **(asignación complementaria propuesta)**: [US11] Fixture de cuatro registros con inconsistencias en `src/proyecta/seed/fixtures.py`.
- **T153** **(asignación complementaria propuesta)**: [US11] Cargador idempotente con errores por fila en `src/proyecta/application/use_cases/carga.py`.
- **T154** **(asignación complementaria propuesta)**: [US11] CLI de carga en `scripts/seed_synthetic.py`.
- **T155** **(asignación complementaria propuesta)**: [US11] Pruebas de idempotencia y ausencia de datos reales en `tests/integration/test_seed.py`.
- **T156** **(asignación complementaria propuesta)**: [US11] Ejecutar la suite de US11 y corregir fallos en `tests/integration/test_seed.py`.
- **T165** **(asignación complementaria propuesta)**: Preparar semilla y guion de demo con datos sintéticos en `scripts/seed_synthetic.py` y `docs/demo.md`.
