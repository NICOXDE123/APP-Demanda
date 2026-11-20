# Auditoría de Interfaz y Plan de Rediseño Visual · Proyecta MVP

## 1. Contexto y Diagnóstico Inicial
El MVP actual de **Proyecta** (respaldado por el equipo *Heavy-Duty* en el desafío *APP Gestión de la Demanda*) cumple rigurosamente con la densidad técnica, la lógica de negocio y la trazabilidad del backend (FastAPI y Firestore). Sin embargo, tal como se aprecia en las capturas del dashboard y las tablas (`dashboard-1.PNG`, `registros.PNG`, `Auditoria.PNG`), la interfaz peca de ser **visualmente plana, monocromática y de alto desgaste cognitivo**. 

Al utilizar tonos de fondo oscuros casi idénticos (`#0F172A`) sin una jerarquía clara de superficies (Card Elevation) ni acentos cromáticos funcionales, la información financiera densa se funde, generando fatiga visual en la Capa Ejecutiva y Operaciones.

---

## 2. Diagnóstico por Criterios de Evaluación (Rubric-based Audit)
*   **Claridad Visual y Jerarquía (Desarrollo actual: 2/4 - *Developing*):** Las cifras monetarias principales (ej. `$1.788.046.023`) compiten en peso visual con las etiquetas secundarias. Falta separación de capas entre el fondo base y los contenedores de KPIs.
*   **Impacto Gráfico y Storytelling de Datos (Desarrollo actual: 1.5/4 - *Needs Improvement*):** El gráfico de barras/líneas del Forecast es plano; las barras inferiores y la línea de meta carecen de gradientes, profundidad y micro-interacciones (tooltips modernos).
*   **Densidad Operativa y Lectura de Tablas (Desarrollo actual: 2.5/4 - *Good*):** Las tablas muestran demasiada información horizontal sin *zebra striping* sutil ni un efecto *hover* enriquecido que guíe el barrido visual del usuario.

---

## 3. Plan de Mejora Esencial (Acciones Críticas de Rediseño)

### A. Sistema de Superficies y Elevación (Surface Design)
*   **Problema:** Las tarjetas de indicadores y bloques funcionales están delimitadas únicamente por bordes de 1px muy débiles sobre un fondo oscuro uniforme.
*   **Acción:** Implementar un esquema de capas escalonado. Usa el fondo base (`#0F172A`) para el canvas general, eleva las tarjetas con un tono ligeramente más claro (`#1E293B` o `#222E35`), y añade un **borde superior de acento (border-top de 2px a 3px)** con el color corporativo o estado (ej. esmeralda para Forecast, azul para MAB).

### B. Jerarquía Tipográfica y Cifras Protagonistas
*   **Problema:** Los montos y las métricas clave tienen el mismo tratamiento de tipografía que los textos descriptivos.
*   **Acción:** Aplica una jerarquía estricta: etiqueta superior en tipografía pequeña, color gris suave (`#94A3B8`) y mayúsculas espaciadas (`11px, tracking-wider`); **la cifra principal en gran tamaño, peso bold y color blanco puro** (`28px, font-bold`). Añade micro-indicadores de variación porcentual (ej. `+4.2% vs mes anterior` con una micro-flecha verde).

### C. Gráficos de Alto Impacto (Chart.js Avanzado)
*   **Problema:** El gráfico actual de Forecast e ingresos se percibe estático y poco dinámico.
*   **Acción:** Configura **gradientes de color verticales** bajo el área de las barras (de turquesa brillante transparente a sólido) y añade puntos con bordes blancos brillantes en la línea de meta para que resalten de inmediato sobre el fondo oscuro.

### D. Badges y Semáforos Interactivos en Tablas
*   **Problema:** Los estados en las tablas de registros y auditoría son texto plano dentro de celdas oscuras.
*   **Acción:** Convierte los estados (*En Curso, Adjudicada, Oportunidad*) en **badges tipo píldora** con fondo translúcido y texto de color sólido (ej. verde suave para Adjudicada, ámbar para Seguimiento). Incorpora un efecto *hover* marcado en las filas (`bg-slate-800/50`) para facilitar la lectura horizontal en tablas con múltiples columnas.

