# Quickstart Validation: Proyecta — MVP

**Feature**: `001-proyecta-mvp`

**Date**: 2026-10-27

**Spec**: [spec.md](spec.md)

**Plan**: [plan.md](plan.md)

Esta guía valida el MVP de punta a punta con datos sintéticos. No reemplaza la suite de pruebas: describe escenarios ejecutables y resultados esperados para la demo y la revisión con el sponsor.

## Prerequisites

- Python 3.12 y `uv` (o `pip` + `venv`).
- `gcloud` CLI con el emulador de Datastore, o Docker para el emulador.
- Navegador Chrome o Edge de las últimas dos versiones.
- Playwright y axe-core para las pruebas E2E y de accesibilidad.
- No se requieren datos reales. Todo el entorno usa la semilla sintética.

## Setup

```bash
# 1. Dependencias
uv sync --extra dev
# alternativa: python -m venv .venv && source .venv/bin/activate
#              pip install -e ".[dev]"

# 2. Emulador de Datastore (terminal aparte)
gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081

# 3. Variables de entorno
export DATASTORE_EMULATOR_HOST=localhost:8081
export GOOGLE_CLOUD_PROJECT=proyecta-local
export PROYECTA_ENV=dev
export PROYECTA_SECRET_KEY=dev-only-change-me
export PROYECTA_SEED_PASSWORD=cambiar-solo-local   # contraseña de los usuarios de la semilla

# 4. Semilla sintética
python scripts/seed_synthetic.py --records 1000 --sectors 12

# 5. Aplicación
uvicorn proyecta.main:app --reload --port 8000
```

Abrir `http://localhost:8000`. Usuarios de la semilla:

| Rol | Correo |
|---|---|
| Operaciones | `operaciones@proyecta.local` |
| Líder | `lider@proyecta.local` |
| Ejecutivo | `ejecutivo@proyecta.local` |

La contraseña de los tres usuarios es el valor de `PROYECTA_SEED_PASSWORD`. Es solo para el entorno local: no se versiona ni se usa en la demo pública (Principio IX).

## Test commands

```bash
# Dominio y reglas
pytest tests/unit/domain -q
pytest --cov=proyecta.domain --cov-fail-under=90

# Integración, contrato y E2E
pytest tests/integration -q
pytest tests/contract -q
playwright install
pytest tests/e2e -q

# Accesibilidad y calidad de interfaz
pytest tests/e2e -k accessibility -q
```

Resultado esperado: todo en verde; cobertura de dominio ≥ 90 %; cero violaciones `axe` críticas.

## Validation Scenarios

### V-01 · Alta de oportunidad con dos perfiles

1. Iniciar sesión como Líder.
2. Crear una oportunidad con manager, sector, cliente, servicio, modalidad, tecnologías y dos perfiles con HC, dedicación, tarifa y fechas.
3. Verificar la previsualización de Base, MAB y Forecast antes de guardar.

**Esperado**: código `OPD-####`, estado `Pendiente`, flujo 1, P 10 %, C 90 %, evento de creación en auditoría y previsualización sin persistencia.

### V-02 · Adjudicación al 100 %

1. Abrir la oportunidad y pasarla a `Adjudicada` con fecha y al menos un perfil.
2. Verificar el tipo, la probabilidad y la auditoría.

**Esperado**: tipo `Demanda`, P 100 %, rango 80–95 % retirado para `Adjudicada`, evento con estado, tipo y probabilidad anteriores y nuevos.

### V-03 · Perfiles seleccionados y Backlog confirmado

1. Confirmar un perfil con fecha de ingreso y pasar al flujo 6.
2. Abrir el dashboard y la vista de Backlog confirmado.

**Esperado**: P 100 %, MAB recalculada con confiabilidad, el registro aparece una sola vez y no se suma al Backlog contractual.

### V-04 · Cálculo de referencia

1. Crear un registro con 3 HC y tarifa de $2.600/h.
2. Consultar la Base, la MAB con P 50 % y C 90 %, y el detalle.

**Esperado**: Base $1.404.000; MAB $631.800; el detalle muestra HC, dedicación, tarifa, horas, días activos, P y C.

### V-05 · Continuidad y Backlog contractual

1. Crear una continuidad con contrato de $45.000.000 mensuales, inicio y fin.
2. Consultar el Forecast y el reporte de vencimientos.

**Esperado**: Backlog contractual $45.000.000 en el mes; MAB 0; el registro no se suma dos veces; alerta de vencimiento según `aviso_termino_dias`.

### V-06 · Horas con vigencia mensual

1. Como Operaciones, cambiar las horas de 180 a 176 con motivo y fecha efectiva en un mes futuro.
2. Comparar el mes anterior, el mes efectivo y el puente.

**Esperado**: los meses anteriores conservan su cálculo; el mes efectivo y siguientes usan 176 h; el puente muestra el efecto parámetros; el cambio queda auditado con motivo.

### V-07 · Gap por sector

1. Cargar una meta de $1.700.000.000 para un sector y mes.
2. Crear o ajustar registros hasta un Forecast de $1.500.000.000.
3. Consultar el dashboard.

**Esperado**: gap $200.000.000; cobertura 88,2 %; semáforo rojo; si falta la meta, no se calcula el gap y aparece `DQ-12`.

### V-08 · Cierre y puente

1. Ejecutar el cierre mensual como Operaciones.
2. Verificar el corte `CERRADO`, la inmutabilidad y la comparación con el corte anterior.

**Esperado**: `CorteDetalle` con base, P, C, MAB, Backlog y HC por registro-mes; el puente descompone la variación por causa y la suma coincide con la diferencia total, con línea de redondeo.

### V-09 · Calidad del dato

1. Crear un registro `En Curso` sin `Invoicing`.
2. Abrir el panel de calidad.

**Esperado**: rojo por `DQ-07` con alerta de facturación no planificada; un `Adjudicada` sin `En Staffing` aparece amarillo por `DQ-06`.

### V-10 · Permisos y concurrencia

1. Como Líder A, intentar editar un registro del Líder B.
2. Abrir el mismo registro en dos sesiones y guardar desde la segunda.

**Esperado**: la edición ajena se rechaza sin modificar datos; la segunda escritura informa conflicto de versión, conserva lo escrito y muestra la versión vigente.

### V-11 · Auditoría inmutable

1. Consultar la auditoría de un registro.
2. Intentar editar o borrar un evento por la interfaz y por el contrato.

**Esperado**: la interfaz no ofrece la acción; el servidor rechaza la operación con `405`; una corrección es una entrada nueva que referencia la anterior.

### V-12 · Exportación

1. Filtrar el pipeline por sector y exportar a `.xlsx`.
2. Exportar la auditoría y abrir ambas planillas.

**Esperado**: el archivo respeta filtros y permisos; un líder no recibe datos de otros owners; las celdas con `=`, `+`, `-` o `@` están sanitizadas; la auditoría incluye valor anterior, nuevo, usuario, fecha, motivo e impacto.

### V-13 · Carga inicial sintética

1. Ejecutar `python scripts/seed_synthetic.py --fixture four-records`.
2. Verificar los cuatro registros, las inconsistencias por fila y el recálculo a 180 h.

**Esperado**: cuatro registros sintéticos; inconsistencias marcadas; ningún dato real; la importación es idempotente.

### V-14 · IA y simulación (opcional)

1. Si `PROYECTA_AI_ENABLED=true`, generar una sugerencia con una contradicción entre bitácora y campos.
2. Aceptarla y revisar la auditoría.
3. Ejecutar una simulación con otra probabilidad.

**Esperado**: la sugerencia cita la bitácora, requiere aprobación, se audita con origen `IA` y no escribe sola; la simulación se rotula como `simulado`, no persiste y no cambia estados ni cortes. Si la IA está apagada, el MVP sigue funcionando.

## Demo checklist

- [ ] Los tres roles inician sesión y ven solo lo que les corresponde.
- [ ] La oportunidad recorre `Pendiente → Adjudicada → Perfiles seleccionados → En Curso`.
- [ ] La MAB, el Backlog y el Forecast cuadran con los casos C-01 a C-08.
- [ ] El dashboard muestra los 11 datos y abre el detalle de cada cifra.
- [ ] El cierre congela el corte y el puente explica la variación.
- [ ] La auditoría rechaza edición y borrado.
- [ ] La exportación respeta filtros y permisos.
- [ ] No hay datos reales en la demo.
- [ ] La IA y el simulador no bloquean la demo si fallan.

## Troubleshooting

| Síntoma | Causa probable | Acción |
|---|---|---|
| `Could not automatically determine credentials` | Emulador no iniciado o `DATASTORE_EMULATOR_HOST` ausente | Exportar la variable y reiniciar la app |
| `409` al guardar | Otro usuario guardó antes | Recargar, revisar la versión y reintentar |
| `403` al editar | El registro no pertenece al líder | Usar Operaciones o el owner correcto |
| Dashboard lento | Proyección `ResumenMensual` desactualizada | Ejecutar `python scripts/rebuild_resumen.py` |
| IA no disponible | Falta de credenciales o flag apagado | Mantener `PROYECTA_AI_ENABLED=false`; el MVP funciona sin IA |
