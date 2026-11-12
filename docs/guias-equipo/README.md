# Guías de ejecución del equipo

Estas guías convierten los roles de [equipo.md](../equipo.md) en lotes de trabajo para una persona apoyada por una IA. Las rutas dentro de las guías parten de la raíz del repositorio. La asignación original es una propuesta del PO; estas guías no reemplazan los requisitos ni cambian el estado de las tareas.

## Guía por integrante

| Integrante | Frente | Guía |
|---|---|---|
| Alfredo San Juan | Producto, decisiones y aceptación | [Abrir guía](alfredo-san-juan.md) |
| Matías Mcintire | Arquitectura, infraestructura y seguridad | [Abrir guía](matias-mcintire.md) |
| Felipe Astete | Estados, reglas y procesos operativos | [Abrir guía](felipe-astete.md) |
| Leonardo Aguilera | Dashboard, reportes y exportación | [Abrir guía](leonardo-aguilera.md) |
| Bryam Beltrán | Registros, formularios, bitácora y calidad | [Abrir guía](bryam-beltran.md) |
| Nicolás Huenchual | Dominio, motor, IA y datos sintéticos | [Abrir guía](nicolas-huenchual.md) |
| Roberto Villouta | Auditoría, acceso, pruebas y operación | [Abrir guía](roberto-villouta.md) |

## Estado y documentos que debe leer la IA

Al preparar estas guías hay carpetas y archivos `__init__.py`, pero faltan `pyproject.toml`, la aplicación ejecutable y las implementaciones. Los comandos de desarrollo son previstos y requieren completar Setup. Este directorio tampoco contiene historial Git verificable: las instrucciones de ramas y PR aplican cuando trabajen en un clon con Git.

Antes de implementar, leer en este orden:

1. `AGENTS.md` y `docs/equipo.md`: convenciones y responsables.
2. `docs/fuentes/requerimientos.md` y `.specify/memory/constitution.md`: requisitos normativos y principios.
3. `specs/001-proyecta-mvp/spec.md` y `plan.md`: comportamiento y arquitectura.
4. `specs/001-proyecta-mvp/tasks.md`: IDs, dependencias y estado oficial.
5. `data-model.md`, `contracts/openapi.yaml` y `quickstart.md`, dentro de esa especificación: entidades, contratos y aceptación.
6. La guía personal, el código existente y los ADR del frente.

Si hay una contradicción, registrarla con sus referencias y solicitar resolución al PO. Por ejemplo, `plan.md` menciona `domain/engine.py`, mientras que las tareas y el esqueleto usan `domain/engine/`: seguir las rutas detalladas de las tareas para los módulos, sin crear dos motores. Las decisiones S-xx abiertas deben conservarse como pendientes; no inventar una respuesta del sponsor.

## Orden de ejecución

1. **Setup, T001–T011:** Matías coordina instalación, configuración y app base.
2. **Fundación, T012–T036:** Nicolás entrega dominio/puertos/seed; Matías repositorios/auth/config; Felipe permisos; Roberto auditoría/pruebas; Bryam layout. Ninguna historia empieza antes de completar esta fase.
3. **MVP:** US1 registros → US2 estados → US3 motor → US4 dashboard, respetando las dependencias detalladas de `tasks.md`.
4. **Operación ampliada:** US5–US9 según sus dependencias; US10 y US11 son opcionales. T035 proporciona el esqueleto de datos sintéticos sin exigir toda US11 para iniciar.
5. **Endurecimiento y aceptación:** seguridad, accesibilidad, rendimiento, operación y escenarios del quickstart.

Trabajar con una tarea o un lote pequeño de tareas dependientes. `[P]` solo permite trabajo simultáneo cuando no se comparte archivo ni se depende de una tarea incompleta. Cada integrante escribe las pruebas de su implementación; Roberto mantiene la estrategia transversal.

## Cruces de responsabilidad

| Archivo o tarea | Implementación y coordinación |
|---|---|
| T060, acciones web/bitácora | Bryam implementa; Felipe entrega casos de uso y revisa la integración. Se excluye T060 del catálogo principal de Felipe. |
| T159, seguridad | Matías implementa; Roberto revisa. El catálogo principal aparece solo en la guía de Matías. |
| `application/services/audit.py` | Roberto crea T029; Nicolás integra el impacto del motor en T077. |
| `domain/permissions.py` | Felipe crea T028; Roberto amplía T131. |
| `interfaces/api/errors.py` | Matías crea T031; Roberto amplía T132. |
| `infrastructure/datastore/corte_repository.py` | Matías crea T023; Felipe continúa T108. |
| T008 y T033, CSS/JS/layout | Matías prepara recursos comunes; Bryam integra layout y navegación. |
| T110, `domain/engine/puente.py` | Felipe implementa y Nicolás revisa su integración con el motor. |
| T139, `registros/list.html` | Leonardo agrega exportación coordinándose con Bryam. |
| T158, plantillas compartidas | Roberto coordina la evaluación; Bryam y Leonardo acompañan las correcciones. |

## Asignaciones complementarias propuestas

Estos responsables cubren tareas sin dueño explícito en la tabla original. Son una propuesta operativa visible; Alfredo puede ajustarla en `docs/equipo.md`. No representan aprobación de un cambio de alcance.

| Tareas | Responsable propuesto | Apoyo |
|---|---|---|
| T150–T156, carga sintética; T165, preparación de demo | Nicolás | Alfredo integra el guion; Roberto valida la carga. |
| T160, observabilidad; T173, presupuesto | Matías | Roberto revisa operación; Alfredo acuerda presupuesto. |
| T161, operación; T172, zonas horarias | Roberto | Matías aporta infraestructura; autores corrigen sus módulos. |
| T162, manual/README/ADR/demo | Alfredo coordina | Matías redacta ADR/README; cada integrante aporta su sección del manual. |
| T170–T171, compatibilidad/localización | Bryam | Leonardo revisa dashboard; Roberto verifica evidencia. |

Los catálogos personales distribuyen T001–T173 entre responsables principales sin duplicarlos. Compartir un archivo no autoriza editarlo al mismo tiempo: acordar primero el contrato y el orden de integración.

## Prompt común para una IA

Copiar este bloque y añadir el prompt de la guía personal. Dar acceso a los archivos del repositorio; si la herramienta no puede leerlos, proporcionar sus contenidos antes de pedir implementación.

```text
Trabaja en Proyecta como asistente del integrante indicado en mi guía.
Lee AGENTS.md, docs/equipo.md, docs/guias-equipo/README.md y mi guía personal.
Después consulta requisitos, constitución, spec, plan, tasks, modelo, OpenAPI y ADR del frente.

Ejecuta únicamente la tarea o lote indicado, previa inspección del código y sus dependencias.
Identifica los requisitos y criterios AC que cubre. Si una dependencia no existe, informa
el bloqueo y avanza solo con trabajo independiente permitido; no declares el flujo terminado.
Conserva el stack Python/FastAPI/Jinja2/HTMX/Datastore y las capas existentes.
Mantén el dominio sin HTTP/BD, las fórmulas en el motor y los datos de prueba sintéticos.
No inventes contratos, decisiones de negocio, aprobaciones ni resultados de pruebas.
Coordina archivos compartidos con el responsable antes de cambiar sus interfaces.
Para implementación, escribe pruebas de comportamiento, verifica su fallo inicial y luego
implementa. Ejecuta las comprobaciones del lote que permita el entorno y registra sus salidas.
Documenta cualquier comando que no pudiste ejecutar y el motivo.
No marques tareas completadas hasta que el revisor las confirme.
Entrega: tareas/requisitos cubiertos, archivos y su propósito, verificaciones ejecutadas,
resultados, bloqueos, decisiones pendientes y contrato que recibe el siguiente integrante.
```

## Preparación y validación local

Después de Setup, consultar `quickstart.md` y el README que entregue Matías. Ejemplos previstos desde la raíz:

```powershell
uv sync --extra dev
gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081
```

En otra terminal PowerShell, con el emulador activo:

```powershell
$env:DATASTORE_EMULATOR_HOST = 'localhost:8081'
$env:GOOGLE_CLOUD_PROJECT = 'proyecta-local'
$env:PROYECTA_ENV = 'dev'
$env:PROYECTA_SECRET_KEY = 'dev-only-change-me'
$env:PROYECTA_AI_ENABLED = 'false'
uv run uvicorn proyecta.main:app --reload --port 8000
```

Los valores anteriores son de desarrollo local. La semilla requiere T035 y, para la CLI ampliada, T150–T156. Playwright y axe-core requieren su instalación e integración antes de ejecutar E2E. Comprobar instalación y configuración de Ruff/mypy en T003 antes de usarlos.

## Lista de entrega de cada lote

- Indicar tarea, requisitos y archivos modificados, con propósito y decisiones tomadas.
- Registrar comandos ejecutados y resultados reales; separar fallos, bloqueos y verificaciones pendientes.
- Probar permisos, auditoría, validación y concurrencia donde corresponda; mantener cobertura del dominio ≥90 %.
- Adjuntar capturas para cambios visuales y evidencia reproducible para cálculos o rendimiento.
- Mantener datos sintéticos, secretos fuera del repositorio y documentación en español de Chile.
- Entregar contratos y dependencias al siguiente integrante; solicitar revisión de otra persona antes de integrar.
- En un clon Git, usar una rama como `feat/T055-estados` y un commit como `Implementa transiciones de estado (T055)`; el PR incluye alcance, pruebas y pendientes. Son convenciones propuestas, no inferidas del historial.

Los archivos `docs/evidencias/aceptacion.md` y `docs/evidencias/qa.md` mencionados en las guías son entregables propuestos: deben contener evidencia real cuando se ejecuten las validaciones.
