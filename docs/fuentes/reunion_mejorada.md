# Proyecta — Minuta de la primera reunión

**Proyecto:** Aplicación de Gestión de Oportunidades y Demanda  
**Reunión:** Primer levantamiento de información y necesidades operacionales  
**Interlocutor:** Jorge Escobar  
**Cargo:** Gerente de Proyectos y responsable de Operaciones

## 1. Contexto del área de Operaciones

El área de Operaciones trabaja con información financiera y comercial para analizar el estado de los negocios, sus costos, ingresos y márgenes. Uno de sus objetivos principales es proyectar los resultados de los próximos meses y anticipar las necesidades para cumplir las metas comerciales.

Los aspectos más relevantes son:

- **Control financiero:** seguimiento de costos, ingresos y márgenes.
- **Proyección:** análisis de escenarios para los próximos 3, 6 y 12 meses, con especial énfasis en los primeros 3 meses.
- **Gestión de oportunidades y demandas:** identificación de negocios potenciales, evaluación de su probabilidad de concretarse y estimación de su impacto.
- **Gestión de personas:** seguimiento de los headcounts (HC), las incorporaciones, las bajas y los cierres mensuales.
- **Indicadores operacionales:** estadísticas por sector, oportunidades comerciales y necesidades de personal.

### 1.1. Conceptos de negocio mencionados

| Concepto | Descripción preliminar |
|---|---|
| **Backlog** | Proyectos que vienen de períodos anteriores. |
| **MAB** | Concepto relacionado con el backlog seguro y las oportunidades ponderadas por su probabilidad. Su fórmula y alcance exactos deben validarse. |
| **Gap comercial** | Diferencia entre la proyección comercial y el objetivo que se busca alcanzar. Por ejemplo, si la proyección es de 1.500 millones y la meta es de 1.700 millones, existe una brecha de 200 millones que se debe cubrir con nuevas oportunidades. |

**Observación:** las definiciones anteriores son una primera interpretación de los apuntes y requieren confirmación con Operaciones, especialmente la relación entre backlog, MAB y oportunidades.

## 2. Objetivo principal de Proyecta

La aplicación debe centralizar la información de las oportunidades y demandas comerciales para facilitar su seguimiento, análisis y proyección.

El objetivo es disponer de un pipeline actualizado que permita responder preguntas como:

- ¿Qué oportunidades nuevas existen en cada sector?
- ¿Cuánto ingreso potencial representan?
- ¿Qué tecnologías, especialidades y perfiles se requieren?
- ¿Qué oportunidades tienen mayor probabilidad de concretarse?
- ¿Cuántas personas se necesitarán durante los próximos meses?
- ¿Cómo se compara la proyección actual con los objetivos comerciales?
- ¿Qué oportunidades están próximas a concretarse y cuáles presentan riesgos?

La información debe permitir generar estadísticas e indicadores sin depender exclusivamente de la revisión manual de planillas.

## 3. Usuarios y permisos

Se plantea que los gerentes y líderes puedan ingresar a la plataforma para revisar el estado de los negocios y consultar los indicadores.

Como primera aproximación, se identificaron dos perfiles:

| Perfil | Función preliminar |
|---|---|
| **Gerente o líder** | Consultar el dashboard, revisar oportunidades y analizar indicadores y proyecciones. |
| **Administrador** | Registrar y mantener la información de las oportunidades y demandas. |

Esta separación de permisos es una propuesta inicial basada en los apuntes. Se debe confirmar quién podrá crear, editar, actualizar estados y cerrar oportunidades.

## 4. Flujo comercial y probabilidades

Las oportunidades deben avanzar según su nivel de madurez comercial. Durante la reunión se mencionaron cinco niveles de probabilidad:

| Probabilidad | Situación comercial |
|---:|---|
| **10 %** | Oportunidad inicial, sin fecha definida, sin perfiles concretos y con información todavía poco precisa. |
| **25 %** | Se está trabajando en la propuesta y se comienzan a considerar perfiles genéricos. |
| **50 %** | La propuesta ya fue presentada y se están buscando perfiles para responder a la necesidad. |
| **75 %** | La propuesta fue ganada y existen candidatos en proceso de entrevistas. |
| **100 %** | La propuesta fue ganada y los perfiles han sido seleccionados. |

Estas probabilidades deben asociarse a reglas de negocio claras para que el sistema pueda calcular las proyecciones de manera consistente.

### 4.1. Consideraciones para el estado del 100 %

Se mencionaron dos procesos que deben distinguirse:

- **Staffing / Recruiting:** proceso mediante el cual se solicita personal para cubrir una demanda.
- **Invoicing:** aplicación utilizada para registrar lo que se prevé facturar durante el mes.

Una oportunidad ganada no implica necesariamente que la facturación ya esté registrada ni que todos los perfiles estén incorporados. Por ello, se debe confirmar cómo se relacionan el estado comercial, la solicitud de personal y la previsión de ingresos.

## 5. Relación entre oportunidades, Staffing e Invoicing

Durante la reunión se planteó que las oportunidades y demandas forman parte del pipeline que Operaciones necesita controlar. Sin embargo, existen sistemas o procesos distintos para gestionar la demanda de personas y la facturación.

### 5.1. Staffing

Permite gestionar la solicitud de personas para cubrir una oportunidad o demanda.

Se necesita identificar si la oportunidad ya fue levantada a Staffing, es decir, si la solicitud de personal ya fue realizada.

### 5.2. Invoicing

Permite registrar la previsión de facturación mensual.

Se debe identificar si la oportunidad ya está registrada en esta aplicación.

### 5.3. Hipótesis pendiente de validación

Se planteó el siguiente ejemplo:

- **T0:** existe una previsión inicial de facturación de $1 millón.
- **T1:** la oportunidad avanza y se actualiza la previsión con los montos en curso.

También se observó que, al marcar una oportunidad como adjudicada, una planilla podría dejar de contabilizarla en el MAB. Se debe confirmar si esto ocurre realmente y si la previsión considera únicamente oportunidades adjudicadas, o si contempla otros estados.

**Implicación para Proyecta:** no se debe asumir que adjudicación, registro en Invoicing y levantamiento a Staffing son equivalentes. Es necesario definir cómo se contabiliza cada oportunidad en los indicadores y las proyecciones.

## 6. Información que debe registrar una oportunidad o demanda

Los siguientes campos se recopilaron durante la reunión. La obligatoriedad, el formato y las relaciones entre ellos están pendientes de especificación.

| Campo | Descripción o propósito |
|---|---|
| Manager | Gerente asociado al negocio. |
| Sector | Área o sector al que pertenece la oportunidad. |
| Cliente | Cliente asociado al negocio. |
| Servicio / proyecto | Nombre o descripción del servicio o proyecto. |
| Tecnología backend | Tecnologías de backend requeridas. |
| Tecnología frontend | Tecnologías de frontend requeridas. |
| Studio | Clasificación adicional propuesta para organizar las oportunidades. |
| Cuenta | Identificador que permite determinar a qué negocio se deben imputar las horas. |
| ID MANA | Identificador de la aplicación actual de generación de demanda, que según lo comentado se utiliza poco. |
| Tipo | Clasificación entre oportunidad y demanda. |
| Probabilidad | Probabilidad de concreción comercial, según las etapas definidas. |
| Estado | Estado operativo o comercial, por ejemplo: adjudicada, en curso, cancelada o stand by. |
| Fecha de adjudicación | Fecha en que se adjudica el negocio. |
| Fecha de cancelación | Fecha en que se cancela. |
| Flujo | Campo mencionado durante la reunión; falta precisar su significado y los valores permitidos. |
| Owner | Persona responsable del seguimiento de la oportunidad. |
| Modalidad | Tipo de ejecución: NTT o subcontratación. |
| Bitácora | Historial de avances, comentarios y antecedentes de la oportunidad. |
| Levantado a Staffing | Indicador que informa si la solicitud de personal ya fue realizada. |
| Registrado en Invoicing | Indicador que informa si el negocio ya fue registrado en la aplicación de facturación. |
| Tarifa media | Tarifa promedio por hora, según lo señalado en relación con los procesos de recruiting. Debe precisarse su fórmula y alcance. |

### Observaciones sobre los datos

- Conviene distinguir el **estado de la oportunidad** de los indicadores de Staffing e Invoicing.
- Las tecnologías y especialidades deben permitir clasificar y agrupar las necesidades de personal.
- El campo Studio fue planteado como una sugerencia, no como un requisito confirmado.
- Se debe aclarar si oportunidad y demanda son tipos distintos de registro o etapas relacionadas de un mismo negocio.
- El significado de Flujo, Cuenta e ID MANA debe documentarse antes de definir el modelo de datos.

## 7. Gestión de headcount y necesidades de personal

La plataforma debe permitir analizar la cantidad de personas asociadas a los negocios y su evolución durante los períodos de proyección.

Los aspectos identificados son:

- Headcount por sector.
- Altas e incorporaciones de personas.
- Bajas de personas.
- Cierres mensuales.
- Necesidades de personal derivadas de oportunidades y demandas.
- Tecnologías y especialidades requeridas.
- Distribución temporal de las necesidades.

El análisis debe ayudar a comprender no solo el valor comercial de una oportunidad, sino también las personas necesarias para ejecutarla.

## 8. Dashboard e indicadores

Se requiere un dashboard actualizable que los gerentes y líderes puedan consultar para revisar el estado de los negocios.

### Indicadores y reportes mencionados

1. **Oportunidades por sector:** cantidad y distribución de oportunidades entre los distintos sectores.
2. **Personas por sector:** cantidad de personas asociadas a cada sector.
3. **Proyección comercial:** evolución esperada del negocio durante los próximos 3, 6 y 12 meses.
4. **Headcount:** necesidades, altas, bajas y cierres mensuales.
5. **Probabilidades comerciales:** distribución de las oportunidades según su nivel de madurez.
6. **Tecnologías y especialidades:** perfiles técnicos requeridos por las oportunidades y demandas.

Estos reportes constituyen una base inicial. Queda pendiente definir las métricas exactas, sus fórmulas, los filtros disponibles y la periodicidad de actualización.


---

## Conclusión

La necesidad central identificada es contar con una visión consolidada y actualizada de las oportunidades y demandas, que permita a Operaciones anticipar ingresos, necesidades de personal y brechas respecto de los objetivos comerciales.

El principal trabajo previo al desarrollo consiste en **formalizar las reglas de negocio del MAB, las probabilidades comerciales y la relación entre el pipeline, Staffing e Invoicing**. Estas definiciones determinarán el modelo de datos, los cálculos y los indicadores de Proyecta.