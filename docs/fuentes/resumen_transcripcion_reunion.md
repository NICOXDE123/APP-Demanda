# RESUMEN ANALÍTICO DE LA PRIMERA REUNIÓN CON EL SPONSOR
**Archivo Fuente:** `[Reserva] Primera reunión con Sponsor y_ Transcripción`  
**Iniciativa:** Proyecta — APP Gestión de la Demanda y Oportunidades (Build & Impact 2026)  
**Fecha de la Sesión:** Jueves, 15 de octubre de 2026  
**Interlocutor Principal (Sponsor):** Jorge Alejandro Escobar Alvarado (Gerente de Proyectos y Responsable de Operaciones en NTT DATA GDN-e)  
**Agile Coach:** Isaac Enrique Vega Muñoz  
**Equipo de Desarrollo (Heavy-Duty / TEC-UCT):** Alfredo San Juan (PO), Matías McIntyre (Arquitectura), Felipe Astete (Backend/Estados), Leonardo Aguilera (UI/Dashboards), Bryam Beltrán (Frontend/Bitácora), Nicolás Huenchual (Líder Backend/Motor/IA) y Roberto Villalta (Seguridad).

---

## 1. CONTEXTO ORGANIZACIONAL Y MISIÓN DE OPERACIONES

### 1.1. Quién es el Sponsor y qué hace Operaciones en NTT DATA
Jorge Escobar se presenta como Gerente de Proyectos en NTT DATA con base en la oficina de **GDN-e Chile** (Temuco / Altomoco), con trayectoria en la empresa desde 2008 (iniciando en Everis). Gestiona múltiples sectores industriales (*Insurance*, Banca, Sector Público y proyectos con la oficina de Washington, EE.UU.) y lidera transversalmente el área de **Operaciones de todo el GDN-e**.

> *"Dentro del área de operaciones tiene mucho que ver con los números... cuánto tenemos de ingresos, cuánto tenemos de costos y cuánto nos está dando de margen. Y muy importante proyectar cómo va a ser los siguientes tres meses, los siguientes seis meses, el siguiente año."* (min 20:30)

Operaciones opera con una visión pragmática de control financiero y capacidad:
- **Visión habitual a 3 meses:** El horizonte operativo por excelencia con mayor certeza.
- **Visión a 6 meses:** Utilizada especialmente en esta época del año (octubre a marzo) para anticipar el cierre del año fiscal y el arranque del siguiente periodo.

---

## 2. LOS TRES PILARES FINANCIEROS Y DE CAPACIDAD

Jorge Escobar define formalmente los tres conceptos sobre los que se estructura toda la proyección de ingresos de la compañía:

```
               ┌─────────────────────────────────────────────────────────────┐
               │              META COMERCIAL DE LA COMPAÑÍA                  │
               │                   (Ejemplo: $1.700 M$)                      │
               └──────────────────────────────┬──────────────────────────────┘
                                              │
                    ┌─────────────────────────┴─────────────────────────┐
                    ▼                                                   ▼
     ┌──────────────────────────────┐                    ┌──────────────────────────────┐
     │    PROYECCIÓN ACUMULADA      │                    │        GAP COMERCIAL         │
     │     (Ejemplo: $1.500 M$)     │                    │  Meta - Proyección = $200 M$ │
     └──────────────┬───────────────┘                    │ (Brecha que hay que salir a  │
                    │                                    │           buscar)            │
          ┌─────────┴─────────┐                          └──────────────────────────────┘
          ▼                   ▼
┌───────────────────┐ ┌───────────────────┐
│      BACKLOG      │ │    MAB (DEMANDA)  │
│(Proyectos activos)│ │(Nuevos negocios   │
│   Ejemplo: $1.000M│ │   ponderados)     │
│                   │ │   Ejemplo: $500M  │
└───────────────────┘ └───────────────────┘
```

1. **Backlog (No es el Backlog de Scrum):**
   - Son todos los proyectos o servicios contratados que vienen desde periodos anteriores y continuarán ejecutándose activamente en los meses venideros (ej. contratos plurianuales de 2 o 3 años).
   - Poseen dotación asignada y facturación segura (ej. 10 consultores fijos en octubre, noviembre y diciembre).
2. **MAB (Oportunidades y Demanda):**
   - Oportunidades y servicios nuevos que aún no han iniciado pero que podrían materializarse con una determinada probabilidad comercial.
   - Ponderan los ingresos futuros según el nivel de certidumbre comercial y los perfiles requeridos.
3. **Gap Comercial ("Lab / Brecha Comercial"):**
   - La diferencia aritmética entre el presupuesto/meta que exige la dirección de la compañía y la proyección financiera respaldada por Backlog y MAB.
   - *Ejemplo numérico textual del Sponsor (min 23:40):*
     - Backlog = $1.000.000.000 CLP (1.000 M$).
     - Oportunidades (MAB) = $500.000.000 CLP (500 M$).
     - Proyección total esperada = $1.500.000.000 CLP (1.500 M$).
     - Meta comercial exigida = $1.700.000.000 CLP (1.700 M$).
     - **Gap Comercial resultante = $200.000.000 CLP (200 M$)**: *"Significa que no tengo idea de dónde los voy a sacar, pero tengo que ir a buscar ese negocio comercialmente para cumplir la cuota."*

---

## 3. PROPÓSITO ESPECÍFICO DEL SISTEMA "PROYECTA"

Ante la consulta de Alfredo San Juan sobre si el sistema debe gestionar las asignaciones individuales de todos los consultores del GDN, Jorge Escobar delimita taxativamente el alcance:

- **El sistema NO es un ERP global de dotación de personal:** No se busca calzar en el MVP las asignaciones de cada consultor individual contra los proyectos vigentes.
- **El núcleo del sistema es la GESTIÓN DE LA DEMANDA (Oportunidades Comerciales):**
  - Capturar y centralizar los requerimientos de nuevos servicios que los gerentes de cuenta negocian con los clientes.
  - Explotar analíticamente los datos de demanda: perfiles técnicos requeridos, tecnologías, fechas estimadas de inicio, tarifas unitarias, probabilidades y proyecciones de facturación.
  - Proporcionar a Operaciones un dashboard semanal actualizado para la toma de decisiones, sin depender de consolidar planillas Excel manualmente.

---

## 4. DEFINICIONES CONCEPTUALES Y OPERATIVAS CRÍTICAS

### 4.1. Diferencia entre Oportunidad y Demanda (`Tipo`)
Jorge Escobar establece la distinción funcional exacta (min 33:16):
- **Oportunidad:** Proyecto o propuesta en curso que NTT DATA **aún no se ha ganado**. El cliente está evaluando alternativas y podría adjudicársela a NTT DATA o a otro proveedor competidor (*vendor*).
- **Demanda:** Oportunidad que NTT DATA **ya ganó/adjudicó formalmente** y donde el cliente solicita la incorporación inmediata o programada de profesionales técnicos.

### 4.2. Escala de Probabilidades y su Significado Operativo
Jorge Escobar explica qué significa cada porcentaje en la práctica comercial (min 38:59 a 40:40):

| Probabilidad | Situación Comercial Real | Interpretación en la Operativa de NTT DATA |
| :---: | :--- | :--- |
| **10%** | **Prospección en Verde** | No hay fecha, no hay perfiles definidos, se está comenzando a conversar la propuesta; nada concreto. *(Bajo el 10% no existe; si no existe, no se registra).* |
| **25%** | **Involucramiento de GDN-e** | Se está elaborando la propuesta formal y se contempla explícitamente la participación de la oficina de GDN-e y sus perfiles de desarrollo. |
| **50%** | **Propuesta Entregada y Búsqueda Activa** | La propuesta técnica y económica ya fue entregada al cliente y Operaciones comienza a buscar perfiles técnicos para responder a la necesidad. |
| **75%** | **Negociación Avanzada con Candidatos** | Propuesta prácticamente ganada; existen candidatos técnicos en proceso de entrevistas con el cliente (muchas veces con nombre y apellido). |
| **100%** | **Propuesta Ganada con Perfiles Listos** | Venta ganada y perfiles técnicos formalmente seleccionados y reservados, con fecha de ingreso acordada para iniciar el servicio. |

---

## 5. LA PROBLEMÁTICA CRÍTICA DE INVOICING, STAFFING Y EL "ESTADO EN CURSO AL 100%"

En el minuto 40:49 a 46:18, Jorge Escobar revela la problemática de fondo que explica por qué la gestión mediante Excel es propensa a errores y cómo interactúan los sistemas:

### 5.1. Distinción entre los Actores
1. **Equipo de Staffing / Recruiting:** Equipo humano encargado de buscar candidatos internos disponibles (en banca/bench) o activar procesos de reclutamiento externo en el mercado.
2. **Invoicing (Gestión Económica):** Aplicación de software corporativa donde Operaciones registra al inicio de cada mes la **Previsión de facturación**. A fin de mes se emite la factura contable real.

### 5.2. El Riesgo de la "Plata Mágica" y la Regla Tácita del Excel
Jorge Escobar explica qué ocurre si una oportunidad se gana a mitad de mes:
- **Momento $T_0$ (Inicio de Mes):** Operaciones carga en la aplicación Invoicing la previsión del mes (ej. $100 millones).
- **Momento $T_1$ (Mitad de Mes):** Se confirma una oportunidad con consultores listos para ingresar. Esta venta no estaba contemplada en la previsión original de Invoicing.
- **La Trampa del Estado:** Si Jorge Escobar marca la oportunidad como `Estado = Adjudicada` en su Excel, las tablas dinámicas la retiraban del cálculo de MAB mensual. Como tampoco estaba cargada en Invoicing, la oportunidad desaparecía de la proyección financiera. A fin de mes, al facturarse, aparecían ingresos imprevistos (*"plata mágica"* no controlada).
- **La Solución Pragmática Actual:** Para evitar esto, en la planilla se mantiene con **`Probabilidad = 100%` pero con `Estado = En Curso`**, sumando en el MAB hasta que sea formalmente absorbida por el sistema de Invoicing.

> *"Si yo no hago eso y la dejo aquí adjudicada, luego en mi reporte no me va a aparecer en la MAB y tampoco me va a aparecer en Invoicing. Y cuando llegue a facturar, me va a aparecer plata mágicamente... Por eso aquí se deja en curso al 100%."* (min 45:36)

---

## 6. INVENTARIO Y EXPLICACIÓN DE CAMPOS DEL EXCEL (POR EL SPONSOR)

Durante la demostración visual de la planilla (`Octubre26.Semana1.Demanda.GDN-e`), Jorge Escobar repasa campo por campo:

1. **`Creación`:** Fecha de ingreso de la iniciativa al archivo.
2. **`Manager`:** Gerente comercial o de cuenta responsable (Carlos Molitor, Jesús Díaz, Jorge Escobar, etc.).
3. **`Tecnología Backend` y `Tecnología Frontend`:** Explica que frecuentemente no coinciden (ej. Oracle en backend y Angular en frontend). Si no hay frontend, se debe consignar *"No Aplica"* en lugar de celdas vacías para evitar dudas de completitud.
4. **`Studio`:** Centros de práctica tecnológica transversales de NTT DATA (Data, QA, Cloud, Frontend). El campo indica si participa un Studio especializado (`Sí`/`No`/`No Aplica`), permitiendo medir el involucramiento de estas áreas.
5. **`Cuenta`:** Código alfanumérico o identificador del proyecto al cual se deben imputar las horas del equipo.
6. **`ID MANA`:** Identificador en la aplicación corporativa MANA utilizada por las oficinas centrales de NTT DATA. Aunque en GDN-e se utiliza poco, se mantiene para trazabilidad con "Oficina".
7. **`Tipo`:** Clasificación binaria entre `Oportunidad` (en competencia) y `Demanda` (ganada con requerimiento de personas).
8. **`Probabilidad`:** Porcentaje de certidumbre comercial (10%, 25%, 50%, 75%, 100%).
9. **`Estado`:** Estados operativos: `Adjudicada`, `En Curso`, `Cancelada`, `StandBy`.
10. **`Fecha Adj / Canc.`:** Fecha en que se ganó o se canceló, fundamental para estadísticas de conversión mensual.
11. **`Flujo`:** Etapas operacionales del requerimiento:
    - `Pendiente RFP` (esperando requerimientos del cliente).
    - `Propuesta en curso` (construcción de la oferta técnica/económica).
    - `Propuesta entregada` (presentada al cliente).
    - `Pendiente candidatos` (esperando perfiles de Staffing).
    - `Validando candidatos` (evaluación y entrevistas con el cliente; fase final previa al cierre).
12. **`Owner`:** Responsable del seguimiento operativo por parte de la oficina gestora.
13. **`Modalidad`:**
    - `NTT`: Personal propio contratado internamente o reubicado desde banca (*staff*).
    - `Subcontratación`: Profesionales externos contratados por horas/mes a través de empresas especializadas de subcontratación (similar a consultores externos gestionados).
14. **`Descripción / Bitácora`:** Campo de texto donde se concatenan semanalmente notas fechadas con avances, hitos y conversaciones con el cliente.
15. **`En Staffing`:** Indicador booleano (`Sí`/`No`) que señala si la solicitud de búsqueda de personas ya fue levantada formalmente al equipo de reclutamiento.
16. **`Invoicing / Demanda Forecast`:** Indicador que precisa si el requerimiento ya está incorporado en la previsión contable de facturación.
17. **`Tarifa Media`:** Dato de entrada crítico. Promedio ponderado cobrado por hora al cliente.
    - *Ejemplo explícito de Jorge Escobar (min 55:10):* *"Si tengo un equipo de 5 personas y uno me vale 22 lucas la hora, el otro 10, el otro 15, saco la tarifa media y digo la tarifa media de este equipo son 18 mil ($18.000 CLP/h)."*
18. **`Desglose Mensual (Altas, Bajas, Cierre)`:** Grilla temporal por meses donde se anotan las incorporaciones previstas (Altas), desasignaciones (Bajas) y la dotación total al cierre del mes (Headcount activo).

---

## 7. ROLES Y USUARIOS DE LA PLATAFORMA

Jorge Escobar delimita la separación de perfiles y permisos (min 30:28 a 31:21):
- **Managers / Gerentes y Líderes:** Consultan el dashboard, analizan proyecciones y alimentan la información de sus oportunidades.
- **Operaciones / Administrador (Jorge Escobar y Jorge Colipe):** Tienen la potestad de centralizar, supervisar, validar la calidad del dato y realizar modificaciones globales en el sistema.
- **Acceso Ejecutivo:** Los directores y tomadores de decisiones acceden en modalidad de consulta exclusiva a reportes y dashboards consolidados.

---

## 8. REPORTES Y EXPLOTACIÓN DE DATOS ESPERADOS

Hacia el final de la reunión (min 56:38 a 57:50), Jorge Escobar detalla los reportes que actualmente extrae de su Excel y que Proyecta debe automatizar:
1. **Resúmenes Mensuales de Ingresos:** Facturación esperada desglosada mes a mes.
2. **Ingresos por Modalidad:** Proyección dividida entre personal directo (`NTT`) y servicios tercerizados (`Subcontratación`).
3. **Proyecciones por Sector:** Evolución esperada del MAB por industria (Banca, Telecomunicaciones, Seguros, Minería/RRNN) para los siguientes meses.
4. **Gráficos de Capacidad:** Cantidad de personas demandadas por sector y distribución temporal.
5. **Gestión de Liberaciones y Banca:** Monitoreo de consultores que finalizan proyectos en los próximos meses para coordinar su reubicación en nuevas oportunidades (hoja `Liberaciones` del Excel).

---

## 9. SÍNTESIS DE ASPECTOS DEFINIDOS VS. PROPUESTAS DE MEJORA

| Elemento | Situación en la Planilla Excel | Definición Acordada para Proyecta |
| :--- | :--- | :--- |
| **Moneda** | Tarifas en pesos chilenos ($18.000 CLP/h) y metas en millones de CLP. | Oficializado en **Pesos Chilenos (CLP)** para todo el MVP. |
| **Adjudicadas y Facturación** | Se dejaban artificialmente en "En curso" al 100% para no perderlas del reporte. | Resuelto mediante la probabilidad del **90% para Adjudicadas** (en Staffing) y ascenso al **100% (Backlog)** al confirmar perfiles, coexistiendo con los flags de Invoicing y Staffing. |
| **Bitácora** | Única celda (R120) de texto plano concatenado a mano. | Entidad relacional estructurada con autor, fecha/hora y tipo de evento. |
| **Flujo de Reclutamiento** | Menú desplegable con 6 estados operativos. | Selector libre de estado operativo entre las 6 opciones, editable por Líder y Staffing. |
| **Permisos de Edición** | Planilla compartida sin control de concurrencia. | Política colaborativa por Sector con auditoría inmutable (`AuditEvent`). |
| **Factor de Confiabilidad** | No existía en la planilla; Jorge ajustaba mentalmente al revisar. | Incorporado formalmente como parámetro exclusivo de Operaciones ($C(r)$) con motivo obligatorio. |
| **Metas y Gap Comercial** | Cálculo manual fuera de la grilla. | Parametrizado por Sector y Mes, con persistencia continua y cálculo automatizado del Gap en el Dashboard. |
