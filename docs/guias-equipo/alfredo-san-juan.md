# Alfredo San Juan — Product Owner

## Resultado esperado

Mantener el alcance trazable, resolver las decisiones con el sponsor y aceptar entregas con evidencia. Tu trabajo con una IA consiste en preparar documentación, revisar coherencia y organizar validaciones; la aprobación del sponsor necesita su respuesta real.

**Tareas base:** T164, T166 y T167. **Complementaria propuesta:** coordinación de T162. Consulta primero [el flujo común](README.md), `AGENTS.md` y `docs/equipo.md`. Las rutas parten de la raíz del repositorio.

## Archivos y contenidos

| Archivo | Contenido que debes mantener o preparar |
|---|---|
| `docs/fuentes/requerimientos.md` | Requisitos normativos, discrepancias del Anexo A, decisiones abiertas e historial. Incorporar H-01, H-04 y H-05 antes de la firma sin borrar antecedentes. |
| `specs/001-proyecta-mvp/spec.md` | Historias, reglas y criterios AC coherentes con las decisiones aprobadas. Conservar identificadores. |
| `specs/001-proyecta-mvp/tasks.md` | Prioridades, dependencias y estado oficial de las tareas. Marcar completadas después de revisión. |
| `docs/equipo.md` | Responsables acordados, traspasos y ajustes a las asignaciones propuestas en estas guías. |
| `specs/001-proyecta-mvp/quickstart.md` | Escenarios V-01 a V-14, instrucciones reproducibles y resultados esperados. |
| `specs/001-proyecta-mvp/checklists/requirements-quality.md` | Revisión final de requisitos con referencias a evidencia. |
| `.specify/memory/constitution.md` | Fuente de principios para T166; evaluar cumplimiento sin relajar las reglas para aprobar una entrega. |
| `docs/manual.md` | Entregable previsto: acciones por rol, permisos, formularios, errores y recorridos de operación. Cada integrante aporta su sección. |
| `docs/demo.md` | Entregable previsto: guion, datos sintéticos, pasos, resultados esperados y limitaciones. Nicolás prepara la semilla. |
| `docs/adr/001-stack.md` | ADR previsto de T162; Matías redacta la decisión técnica y tú coordinas su consistencia documental. |
| `docs/evidencias/aceptacion.md` | Archivo propuesto: versión evaluada, escenario, resultado, evidencia, defecto y responsable de aceptación. |

## Orden de ejecución

1. Compara requisitos, especificación y plan. Separa las decisiones H-xx documentadas de las S-xx pendientes de validación; prepara preguntas concretas al sponsor.
2. Prioriza Setup, Fundación y US1–US4. Coordina las dependencias y confirma cualquier ajuste de responsable en `docs/equipo.md`.
3. Ejecuta T167: actualiza las enmiendas necesarias y su historial. Si encuentras una contradicción, registra sus referencias y la decisión requerida.
4. Coordina T162 con el equipo: Matías aporta README/ADR; los autores documentan sus funcionalidades; integra manual y demo.
5. Con la aplicación disponible, ejecuta T164 junto a Roberto. Registra los escenarios bloqueados y los opcionales deshabilitados sin presentarlos como aprobados.
6. Completa T166 y solicita las revisiones pendientes antes de aceptar el alcance.

## Validación y entrega

Comprueba la cadena requisito → criterio AC → tarea → prueba o escenario. Clasifica cada resultado como aprobado, rechazado, bloqueado o fuera del alcance. Guarda evidencia real, no una descripción de lo que debería ocurrir.

La entrega al equipo debe indicar la siguiente prioridad, los criterios de aceptación, decisiones registradas y pendientes con responsable. Roberto aporta evidencia técnica; el sponsor valida decisiones de negocio. Para cambios exclusivamente documentales, revisa coherencia, enlaces e identificadores.

## Prompt personal para una IA

Copia primero el prompt común del [índice](README.md) y agrega:

```text
Soy Alfredo San Juan, Product Owner de Proyecta.
Lee docs/guias-equipo/alfredo-san-juan.md.
Primer lote: T167.
Compara H-01, H-04 y H-05 entre requerimientos.md, spec.md y plan.md.
Prepara las enmiendas documentales con historial y referencias.
Conserva las decisiones abiertas como pendientes y prepara las preguntas al sponsor.
No inventes aprobaciones ni ejecutes cambios de funcionalidad.
Entrega archivos modificados, coherencia comprobada y decisiones que aún requieren respuesta.
```

Para los siguientes lotes, sustituye T167 por la tarea concreta. No delegues toda la aceptación como un único encargo a la IA.

## Catálogo de tareas del frente

Detalle tomado de `specs/001-proyecta-mvp/tasks.md` al preparar esta guía. Ese archivo conserva el estado oficial y las dependencias; si cambia, actualiza este catálogo. Las rutas abreviadas se interpretan con el directorio de la primera ruta y la tabla de archivos anterior. Las etiquetas [P] no permiten omitir dependencias ni editar un archivo compartido al mismo tiempo.

- **T162** **(asignación complementaria propuesta)**: [P] Completar README, manual de usuario, ADR y guion de demo en `docs/manual.md`, `docs/adr/001-stack.md` y `docs/demo.md`.
- **T164**: Ejecutar los escenarios V-01 a V-14 de `specs/001-proyecta-mvp/quickstart.md` y registrar evidencia.
- **T166**: Revisar la Constitution Check final y el checklist de requisitos en `.specify/memory/constitution.md` y `specs/001-proyecta-mvp/checklists/requirements-quality.md`.
- **T167**: Actualizar `docs/fuentes/requerimientos.md` con H-01, H-04 y H-05 antes de la firma del sponsor.
