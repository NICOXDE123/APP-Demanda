Usa la skill UI UX Pro Max para auditar el frontend de la aplicación web de este repositorio. Quiero saber qué aspectos de la interfaz dificultan orientarse, leer la información o completar tareas, y qué cambios concretos conviene implementar primero.

En esta etapa genera únicamente AUDITORIA_FRONTEND.md. Espera mi aprobación para modificar la aplicación.

## 1. Recorre la aplicación

Revisa el README, los scripts y la estructura del proyecto. Si la web ya está corriendo, usa la URL local disponible. Si necesitas levantarla, utiliza el procedimiento que indica el repositorio.

Identifica el propósito de la web, sus usuarios y sus flujos principales. Abre la aplicación en un navegador y recorre esos flujos en escritorio y móvil. Prueba también la navegación con teclado. Revisa el código de los componentes y estilos cuando necesites explicar la causa de un problema. Si alguna pantalla requiere credenciales o algún aspecto solo se pudo revisar en código, déjalo indicado.

## 2. Valida mis observaciones iniciales

Trata cada observación como una hipótesis. Para cada una, indica si se confirma, en qué pantalla se aprecia, cómo afecta al usuario y qué cambio propones.

- Modo oscuro. Comprueba si la web respeta la preferencia del sistema, si ofrece un selector y si recuerda la elección. Si recomiendas añadirlo, identifica qué colores o componentes habría que adaptar, incluidos gráficos, formularios y estados de interacción.
- Breadcrumbs o migas de pan. Revisa la profundidad real de la navegación. Señala en qué rutas ayudarían a entender la jerarquía o volver a una vista superior. Muestra un ejemplo con nombres reales de la aplicación.
- Identificación de la sección activa. Al entrar directamente a una URL o cambiar de pestaña, ¿se entiende dónde estoy? Revisa el menú, las pestañas y el encabezado. Considera mi idea de oscurecer el hero, pero evalúa si esa señal identifica la sección por sí sola. Propón el indicador más claro para esta interfaz y comprueba si también funciona en móvil, con teclado y sin depender exclusivamente del color.
- Contraste y jerarquía visual. Revisa textos secundarios, botones, enlaces, bordes, campos y estados de foco, selección y error. Para los problemas de contraste, identifica el elemento y su fondo, mide la relación cuando sea posible e indica el criterio WCAG 2.2 AA aplicable. Distingue una falla de legibilidad de una preferencia estética.
- Gráficos. Para cada gráfico relevante, identifica qué pregunta debería responder. Evalúa si se entienden las unidades, el período, las escalas, las leyendas y las diferencias entre series. Comprueba qué ocurre en móvil, con datos vacíos y cuando el usuario no puede usar el hover. Sugiere otro tipo de gráfico solo si mejora la interpretación de esos datos.
- Favicon. Comprueba si aparece en la pestaña del navegador, si el recurso carga correctamente y si el símbolo se reconoce a tamaño pequeño.

Amplía la auditoría si encuentras otros problemas durante el recorrido. Presta especial atención a inconsistencias entre pantallas, desbordes en móvil, acciones difíciles de encontrar y estados de carga, vacío o error que dejen al usuario sin saber qué hacer.

## 3. Entrega un informe que sirva para implementar

Escribe AUDITORIA_FRONTEND.md en español e incluye:

1. Un resumen con las tres mejoras que harías primero y qué problema resuelve cada una.
2. Las rutas, flujos y tamaños de pantalla revisados, junto con las limitaciones de la revisión.
3. Una tabla breve con el veredicto de cada una de mis seis observaciones.
4. Los hallazgos priorizados. Para cada uno incluye la ruta o componente, la evidencia observable, el impacto, la solución concreta, el archivo relevante cuando puedas identificarlo y un criterio de aceptación verificable.
5. Un plan de trabajo ordenado por impacto, esfuerzo aproximado y dependencias. Si varios hallazgos comparten una causa, como un token de color o un componente de navegación, agrúpalos en una sola intervención.

Usa capturas cuando ayuden a demostrar un problema visual. Diferencia lo observado en el navegador de lo inferido al leer el código. Conserva la identidad visual y aprovecha los componentes existentes. Evita recomendaciones genéricas como “mejorar el contraste” o “modernizar el dashboard”: especifica qué elemento cambiarías, por qué y cómo comprobaríamos que quedó resuelto.