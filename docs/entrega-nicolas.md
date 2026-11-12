# Entrega de Nicolás Huenchual — Dominio, motor e IA

**Rol:** Líder Backend / Motor / IA
**Proyecto:** Proyecta — MVP de gestión de demanda
**Rama:** `feature/nicolas-motor`

## Resumen

Implementé la fundación del dominio, el motor de cálculo mensual, el módulo
opcional de IA y simulación, y la carga inicial con datos sintéticos. El
trabajo se apoya en tres reglas: `Decimal` para cálculo, enteros
CLP/centavos/puntos base para almacenamiento, y vigencias mensuales que nunca
reescriben meses anteriores.

**Resultado:** 66 pruebas en verde y 92,5 % de cobertura del dominio, con el
gate de 90 % pasando.

## Tareas entregadas

### Fundación (T012–T017, T035)

| Tarea | Entregable |
|---|---|
| T012 | `domain/enums.py` — `Tipo`, `Estado`, `Flujo` (con `.orden` 1–6), `Rol`, `Modalidad`, `Origen`, `Bucket`, `MotivoCierre` |
| T013 | `domain/value_objects.py` — `Money`, `Percentage`, `Period`, `DateRange` |
| T014 | `domain/entities.py` — `Usuario`, `Registro`, `Perfil`, `TarifaPerfil`, `AjusteHC`, `Contrato` |
| T015 | `domain/entities.py` — `VigenciaEstadoCalculo`, `Bitacora`, `EventoAuditoria`, `Parametro`, `Catalogo`, `MetaComercial`, `Corte`, `CorteDetalle`, `SugerenciaIA`, `Sesion` |
| T016 | `domain/errors.py` — `ErrorDominio` con `code`/`message`/`details`, jerarquía y códigos estables |
| T017 | `application/ports.py` — repositorios, `Reloj`, `ProveedorIA`, `CambioAuditado` |
| T035 | `seed/synthetic.py` — generador determinista de datos sintéticos |

### Motor de cálculo (T064–T079)

- Fracción activa por días y prorrateo (`engine/active_fraction.py`).
- Base mensual con HC, dedicación y tarifas en centavos (`engine/base.py`).
- MAB, Backlog contractual, Backlog confirmado como vista de MAB y Forecast,
  sin doble conteo (`engine/bags.py`).
- HC proyectado y grilla de altas, bajas y cierre (`engine/headcount.py`).
- Gap y cobertura (`engine/gap.py`).
- Resolución mensual de P, C y horas (`engine/vigencias.py`).
- Fachada con contrato de resultados y detalle explicable (`engine/service.py`).
- Caso de uso de cálculo y previsualización sin persistencia
  (`use_cases/calculo.py`).
- Rutas API de forecast y detalle (`interfaces/api/v1/forecast.py`).
- Plantilla de serie y detalle (`templates/registros/calculo.html`).
- Impacto MAB/Forecast en auditoría (`application/services/audit.py`).

Los ocho escenarios C-01 a C-08 quedan verificados exactos, más las pruebas de
redondeo half-up.

### IA y simulación (T142–T149)

- Adaptador Vertex AI (`infrastructure/ai/vertex.py`).
- Sugerencias con cita obligatoria de bitácora, aprobación humana y etiqueta de
  origen (`use_cases/ia.py`).
- Simulación aislada que nunca escribe datos reales (`use_cases/simulacion.py`).
- Rutas API (`interfaces/api/v1/ia.py`) y pantalla opcional de sugerencias.
- Comportamiento correcto cuando la IA no está disponible.

### Carga inicial (T150–T156, T165)

- Generador de 1.000 registros determinista (`seed/synthetic.py`).
- Fixture de cuatro registros, cada uno con una inconsistencia deliberada
  (`seed/fixtures.py`).
- Cargador idempotente con errores por fila que no aborta el resto
  (`use_cases/carga.py`).
- CLI con `--cantidad 1000` y `--fixture four-records`
  (`scripts/seed_synthetic.py`).
- Pruebas de integración, idempotencia y ausencia de datos reales
  (`tests/integration/test_seed.py`).
- Guion de demo (`docs/demo.md`).

## Decisiones técnicas

1. **`Flujo` es `str, Enum`, no `IntEnum`.** El OpenAPI y el modelo de datos lo
   definen como texto; el orden 1–6 vive en la propiedad `flujo.orden`.
2. **Fechas de negocio con semántica explícita.** En el contrato, `fecha_fin` es
   el último día cubierto (incluso); en el perfil, es el primer día inactivo.
3. **Tarifas por solapamiento de mes**, para admitir ingresos a mitad de mes sin
   perder el valor vigente.
4. **El motor usa P y C resueltos**, no fuerza 100 %, de modo que los escenarios
   C-02 y C-03 se reproduzcan ambos.
5. **Idempotencia por `codigo`**, no por identificador autogenerado: recargar no
   duplica registros.
6. **Porcentajes en puntos base.** `Percentage` valida 0–10.000 y convierte
   desde fracción o desde porcentaje, sin `float` en el cálculo.

## Evidencia de calidad

```powershell
python -m pytest tests -q
# 66 passed

python -m pytest tests -q --cov=proyecta.domain --cov-fail-under=90
# Required test coverage of 90% reached. Total coverage: 92.52%

python -m pytest tests/integration/test_ia_sim.py tests/integration/test_seed.py -q
# 16 passed

python -m pytest tests/unit/domain/test_engine_cases.py tests/unit/domain/test_engine_rounding.py tests/integration/test_forecast.py -q
# 27 passed
```

Cobertura por módulo del dominio:

| Archivo | Cobertura |
|---|---|
| `entities.py` | 99 % |
| `value_objects.py` | 99 % |
| `errors.py` | 99 % |
| `enums.py` | 100 % |
| `engine/service.py` | 91 % |
| Total dominio | 92,5 % |

## Reglas de arquitectura respetadas

- El dominio no importa FastAPI, Datastore ni Jinja2.
- Dinero en enteros CLP; tarifas en centavos; porcentajes en puntos base.
- Cálculos con `Decimal` y redondeo half-up al final del registro-mes.
- Vigencias mensuales: un cambio no reescribe meses anteriores.
- Backlog confirmado es una vista de MAB; la continuidad alimenta el Backlog
  contractual.

## Fuera de mi alcance

No forman parte de esta entrega y corresponden a otros frentes:

- `main.py`, `config.py`, wiring de `/api/v1`, repositorios Datastore,
  autenticación, sesión y CSRF, `base.html`, `pyproject.toml`.
- `permissions.py` (Felipe).
- Guion final de la demo (Alfredo).

## Pendientes

- **T077:** revisión de la interfaz de `application/services/audit.py` por
  Roberto.
- Marcar las tareas en `specs/001-proyecta-mvp/tasks.md` después de esa
  revisión.
- Verificar el import de `permissions.py` cuando esté disponible. 