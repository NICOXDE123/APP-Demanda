# Proyecta — APP Gestión de la Demanda y Oportunidades

Plataforma de gestión de oportunidades y demandas, seguimiento operacional y proyecciones de negocio para Operaciones de NTT DATA GDN-e.

**Iniciativa:** Build & Impact 2026 · Fundación NTT DATA Chile  
**Equipo:** Heavy-Duty · TEC-UCT  
**Product Owner:** Alfredo San Juan

> **Entrega 2 (producto mínimo viable):** [`ENTREGA_2.md`](ENTREGA_2.md) responde los 10 puntos de las Bases (§16.2): URL, cuentas de demostración, instrucciones, pruebas, limitaciones, backlog y plan de mejoras.
> **Entrega 1 (definición y diseño de la solución):** [`ENTREGA_1.md`](ENTREGA_1.md) responde los 11 puntos de las Bases (§16.1).

## Estado

MVP de la Entrega 2: las 9 funcionalidades del OnePage, con sesión y tres roles (Operaciones, Líder y Ejecutivo), estados y flujo, auditoría por campo con impacto en la MAB y el Forecast, y dashboard con filtros y detalle de cada cifra. Tiene 88 pruebas y 93 % de cobertura del dominio. Los datos van en memoria, sobre una semilla sintética, hasta tener el proyecto de GCP (S-12). Las limitaciones están en [`ENTREGA_2.md`](ENTREGA_2.md) §7.

## Cómo correrlo

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e '.[dev]'
pytest                                       # motor (C-01 a C-08), dominio, casos de uso y la app por HTTP
uvicorn proyecta.main:app --reload           # http://127.0.0.1:8000 · cuentas en ENTREGA_2.md §2

docker build -f deploy/Dockerfile -t proyecta .
docker run -p 8080:8080 -e PROYECTA_DEMO_PASSWORD=<clave> proyecta   # misma imagen que Cloud Run
```

| Variable | Uso | Por defecto |
|---|---|---|
| `PROYECTA_ENV` | `dev` habilita `/api/docs` y permite la cookie sin `Secure` en HTTP local | `prod` en la imagen; `dev` fuera de ella |
| `PROYECTA_DEMO_PASSWORD` | Contraseña de las cuentas sintéticas | `proyecta-demo`: cambiarla al desplegar |
| `PORT` | Puerto del servicio | `8080` |

## Documentación

| Documento | Contenido |
|---|---|
| [`ENTREGA_2.md`](ENTREGA_2.md) | Entrega 2: MVP, URL, instrucciones, pruebas, limitaciones, backlog y plan de mejoras |
| [`ENTREGA_1.md`](ENTREGA_1.md) | Entrega 1: los 11 puntos de las Bases y el primer incremento |
| [`docs/entrega-1/REGISTRO_USO_IA.md`](docs/entrega-1/REGISTRO_USO_IA.md) | Registro de uso de IA (Bases §14) |
| [`.specify/memory/constitution.md`](.specify/memory/constitution.md) | Principios no negociables del proyecto |
| [`docs/fuentes/requerimientos.md`](docs/fuentes/requerimientos.md) | Documento oficial de requerimientos (fuente normativa) |
| [`specs/001-proyecta-mvp/spec.md`](specs/001-proyecta-mvp/spec.md) | Especificación del MVP y criterios de aceptación |
| [`specs/001-proyecta-mvp/plan.md`](specs/001-proyecta-mvp/plan.md) | Plan técnico, arquitectura e hitos |
| [`specs/001-proyecta-mvp/tasks.md`](specs/001-proyecta-mvp/tasks.md) | Tareas y orden de ejecución |
| [`specs/001-proyecta-mvp/data-model.md`](specs/001-proyecta-mvp/data-model.md) | Entidades, invariantes e índices |
| [`specs/001-proyecta-mvp/contracts/openapi.yaml`](specs/001-proyecta-mvp/contracts/openapi.yaml) | Contrato REST `/api/v1` |
| [`docs/equipo.md`](docs/equipo.md) | Responsables por carpeta |
| [`docs/adr/`](docs/adr/README.md) | Registro de decisiones de arquitectura |
| [`docs/guias-equipo/`](docs/guias-equipo/README.md) | Guía de trabajo de cada integrante |

## Stack

Python 3.12 · FastAPI · Jinja2 + HTMX + Bootstrap + Chart.js · Firestore en modo Datastore · Cloud Run (GCP).

## Datos

La demo y las pruebas usan **solo datos sintéticos**. No se versionan datos reales del cliente (plantillas Excel, tarifas, clientes ni ingresos) ni datos personales del equipo; el `.gitignore` excluye `*.xlsx`, `*.xls`, `*.csv` y la propuesta V3, que incluye los CV.

## Flujo de trabajo

Cada cambio entra por merge request a `main`, con revisión de otra persona y pipeline en verde (`RNF-13`).
