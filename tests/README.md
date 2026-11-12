# tests — estrategia y responsables

## Estructura

```text
tests/
├── unit/domain/     # Reglas, motor, estados, calidad y value objects
├── integration/      # Casos de uso con emulador Datastore y fixtures
├── contract/         # Contrato OpenAPI y errores 403/405/409/422
└── e2e/              # Flujos de usuario, accesibilidad y compatibilidad
```

## Reglas

- Las pruebas de una historia se escriben antes de implementarla y deben fallar primero.
- `C-01` a `C-08` son regresión obligatoria del motor.
- Cubrir `403` (permisos), `405` (auditoría/bitácora), `409` (versión) y `422` (validación).
- Usar datos sintéticos; nunca tarifas, clientes ni ingresos reales. 
- El dominio debe mantener ≥ 90 % de cobertura (`RNF-013`).

## Comandos

```bash
pytest tests/unit/domain -q
pytest --cov=proyecta.domain --cov-fail-under=90
pytest tests/integration -q
pytest tests/contract -q
pytest tests/e2e -q
```

## Responsables

- **Roberto Villouta** — estrategia de QA, seguridad, cobertura y evidencias.
- **Cada integrante** — pruebas de las tareas que implementa.
- **Nicolás Huenchual** — casos de referencia del motor y pruebas de cálculo.
- **Leonardo Aguilera** — pruebas de dashboard, accesibilidad y compatibilidad.
- **Bryam Beltrán** — pruebas de formularios, bitácora y flujos de interfaz.

Los IDs de tareas y el detalle están en `specs/001-proyecta-mvp/tasks.md`.
