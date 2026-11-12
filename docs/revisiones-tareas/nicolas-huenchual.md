# Revisión de tareas — Nicolás Huenchual

Fecha de revisión: 12 de noviembre de 2026.

**Nicolás implementó gran parte de los entregables de su guía, pero todavía hay correcciones e integraciones pendientes para considerar su frente terminado.** El motor tiene pruebas que pasan; la aplicación completa y las pantallas aún no están validadas de extremo a extremo.

Comparé [su guía de trabajo](../guias-equipo/nicolas-huenchual.md) con el código y el historial. Su implementación principal está en el commit `8227340`, firmado por `NICOXDE123`, con su correo institucional.

## Qué hizo

| Tareas de la guía | Trabajo encontrado |
|---|---|
| **T012–T017: fundación** | Creó enums, objetos de valor, entidades, errores y puertos para repositorios, reloj, exportación e IA. |
| **T035: datos mínimos** | Implementó generación reproducible de datos sintéticos. |
| **T064–T073: motor** | Implementó fracción activa por días, Base mensual, MAB, Backlog, Forecast, HC, gap/cobertura y resolución mensual de vigencias. Agregó los casos C-01 a C-08 y pruebas de redondeo. |
| **T074–T078: uso e integración** | Agregó cálculo y previsualización sin persistencia, API de serie/detalle, plantilla de cálculo y servicio para registrar impacto MAB/Forecast en auditoría. |
| **T142–T148: IA y simulación** | Implementó sugerencias con evidencia, aceptación/descarte, proveedor Vertex opcional, simulación en memoria, API y plantilla de sugerencias. |
| **T150–T155 y T165: complementarias** | Agregó generador de 1.000 registros, fixture de cuatro registros inconsistentes, cargador, CLI que produce JSON e instrucciones de demo. |

Esto representa una implementación sustancial, incluidos los frentes opcionales de IA y carga ampliada.

## Qué falta o necesita corrección

1. **T145: las horas de la simulación pueden ignorarse.**
   El simulador incorpora las horas elegidas con vigencia desde **1900**, mientras el motor selecciona el parámetro con fecha de vigencia más reciente. Con el parámetro normal de 2026, prevalecen las horas originales. Falta corregir esa prioridad y probar una simulación que cambie horas. Evidencia: [simulacion.py](../../src/proyecta/application/use_cases/simulacion.py), línea 81.

2. **T146–T147: la pantalla de sugerencias no coincide con la API.**
   Los botones envían formularios con `csrf_token`, pero la API espera un cuerpo JSON con `revisor_id`. Tal como están escritos, esos botones no satisfacen el contrato de aceptación/descarte. Además, falta integrar el contenido de la cita que la pantalla espera mostrar. Evidencia: [plantilla](../../src/proyecta/interfaces/web/templates/sugerencias/index.html), línea 65, y [API](../../src/proyecta/interfaces/api/v1/ia.py), línea 54.

3. **T143–T144: la protección de datos y las citas de IA están incompletas.**
   Se eliminan ciertos campos sensibles, pero el texto libre de bitácora se envía truncado, sin anonimización; podría contener nombres, tarifas o montos. También se asigna automáticamente la primera evidencia cuando el modelo omite la cita, y no se comprueba que una cita devuelta pertenezca a las evidencias proporcionadas. Evidencia: [vertex.py](../../src/proyecta/infrastructure/ai/vertex.py), líneas 97 y 167.

4. **T144: aceptar una sugerencia todavía depende de una integración pendiente.**
   El caso de uso puede marcarla aceptada y auditarla sin modificar el registro, porque el `aplicador` es opcional. Falta conectarlo al cambio de negocio y asegurar consistencia si la aplicación falla. Evidencia: [ia.py](../../src/proyecta/application/use_cases/ia.py), línea 187.

5. **T153: el resultado del cargador informa actualizaciones que no realiza.**
   Si el código ya existe, incrementa `actualizados` y omite la fila. Evita duplicados, pero no actualiza ni vuelve a validar esos datos. Debe aclararse si la repetición debe actualizar o solamente omitir; actualmente el resultado y la documentación inducen a error. Evidencia: [carga.py](../../src/proyecta/application/use_cases/carga.py), línea 180.

## Pendientes compartidos y validación

Las API tienen dependencias que aún lanzan `RuntimeError`; ambas plantillas necesitan un `base.html` inexistente. Falta conectar aplicación, repositorios y rutas web. Estas dependencias involucran a Matías y Bryam: no corresponde atribuirlas exclusivamente a Nicolás. Asimismo, T077 tiene el servicio de auditoría implementado, pero falta demostrar su uso en un flujo real de edición.

No encontré `puente.py` para verificar su apoyo a Felipe en **T110**, ni evidencia suficiente de coordinación o revisión formal. Tampoco está `specs/001-proyecta-mvp/tasks.md`, por lo que no pude contrastar el estado oficial.

Ejecuté las pruebas: **65 pasaron y 1 se omitió por falta de FastAPI**. La cobertura mínima del 90% quedó **sin verificar**, porque falta `pytest-cov`. Por eso, T079, T149 y T156 tienen evidencia favorable de ejecución, pero aún no justifican dar por aceptados todos los flujos. No modifiqué el código.
