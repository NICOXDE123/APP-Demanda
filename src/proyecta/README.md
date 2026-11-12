# src/proyecta — mapa de capas

Este árbol es la base de implementación de Proyecta. Antes de escribir código, leer:

- `specs/001-proyecta-mvp/spec.md` — requisitos y criterios de aceptación.
- `specs/001-proyecta-mvp/plan.md` — stack, módulos y hitos.
- `specs/001-proyecta-mvp/tasks.md` — tareas y orden de ejecución.
- `specs/001-proyecta-mvp/data-model.md` — entidades, campos, invariantes e índices.
- `specs/001-proyecta-mvp/contracts/openapi.yaml` — contrato de la API.
- `docs/equipo.md` — responsables por carpeta.

## Regla de dependencias

```text
interfaces  →  application  →  domain
                     ↑
              infrastructure
```

- `domain/`: entidades, value objects, reglas, estados, motor y calidad. No importa FastAPI, Jinja2, Datastore ni clientes de nube.
- `application/`: casos de uso, puertos y servicios de aplicación. Orquesta el dominio; no contiene SQL/HTTP.
- `infrastructure/`: adaptadores de Datastore, autenticación, exportación y IA. Implementa los puertos.
- `interfaces/`: rutas web y API, plantillas y estáticos. No contiene fórmulas ni reglas de negocio.
- `seed/`: generador sintético y fixtures de demo; no es fuente de verdad.

## Convenciones

- Nombres de módulos en `snake_case`; una responsabilidad por archivo.
- Dinero en CLP entero; tarifas en centavos; porcentajes en puntos base; fechas de negocio sin hora; eventos en UTC.
- Toda escritura relevante genera auditoría; no hay borrado físico.
- No se usan datos reales en demo, pruebas ni carga inicial.
- Cada cambio debe dejar pruebas en `tests/` y mantener el dominio por encima del 90 % de cobertura.

## Estado

Las carpetas y los `__init__.py` están creados. Los archivos de implementación se agregan por tarea según `tasks.md`; no se debe adelantar código de una tarea posterior sin coordinación.
