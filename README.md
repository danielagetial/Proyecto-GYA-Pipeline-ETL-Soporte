# Proyecto Final GYA: Pipeline ETL Aplicado a Base de Casos de Soporte de Jira

## 1. Contexto

La necesidad identificada surge dentro de una empresa dedicada a la implementación de soluciones inteligentes para el control de acceso, control logístico y trazabilidad de la producción. Sus clientes suelen ser empresas pequeñas, medianas y grandes de sectores como la industria manufacturera, logística, consumo masivo y servicios, que necesitan automatizar la gestión y control de accesos o la trazabilidad y gestión de procesos de producción.

Actualmente cuentan con aproximadamente más de 330 clientes que tienen un contrato de soporte activo. Para la atención de requerimientos, fallas, solicitudes de asistencia o incidencias operativas, se utiliza la plataforma **Jira** como canal centralizado de mesa de ayuda.

A través de esta herramienta se registra un alto volumen diario de solicitudes de diversa índole (soporte técnico, fallas en dispositivos de acceso, integración con ERPs y nóminas, configuraciones y capacitaciones). Sin embargo, la información se encuentra almacenada en reportes planos de Jira, lo cual dificulta:
* La consolidación de métricas clave.
* El análisis del desempeño de los agentes de soporte.
* El seguimiento al cumplimiento de los acuerdos de nivel de servicio (SLA).
* La identificación de patrones en las causas de las novedades reportadas por los clientes.

---

## 2. Caracterización del usuario final

El proyecto está orientado a satisfacer las necesidades de toma de decisiones de la **Coordinación del área de soporte**.

* **Descripción del perfil:** Líder encargado de la gestión y supervisión diaria del equipo de agentes de soporte. Sus funciones principales incluyen:
  * Asignación eficiente de tickets.
  * Gestión y ajuste de prioridades (especialmente ante quejas de clientes por casos críticos).
  * Seguimiento riguroso a casos abiertos con fechas de atención prolongadas o vencidas.
  * Seguimiento a casos cerrados de los cuales haya surgido queja en el área de servicio al cliente, debido a su cierre y no solución efectiva o definitiva.

* **Necesidad de información:** La coordinación requiere una visibilidad integral para poder responder ante la Dirección acerca de consultas relacionadas sobre los clientes con mayor volumen de casos reportados y sus motivos principales. Necesita monitorear la operación del área (tickets recibidos y pendientes), el desempeño del equipo (tiempos de resolución y distribución de carga de trabajo por agente), el cumplimiento de los Acuerdos de Nivel de Servicio (SLA) y la identificación de las incidencias, esto con el fin de poder proponer y efectuar acciones de solución.

---

## 3. Objetivo

Implementar un proceso ETL (Extracción, Transformación y Carga) enfocado en integrar los datos transaccionales de Jira y las encuestas de SharePoint hacia una solución analítica en Power BI, que permita la toma de decisiones estratégicas y tácticas de la Coordinación del Área de Soporte.

---

## 4. Preguntas estratégicas o de negocio a responder

### Operación
* ¿Cuántos tickets se reciben diariamente, semanalmente y mensualmente?
* ¿Cuántos tickets están actualmente pendientes?

### Desempeño
* ¿Cuál es el tiempo promedio de resolución?
* ¿Qué personas tienen mayor carga de tickets?
* ¿Qué personas tienen mayor tiempo promedio de resolución?

### SLA
* ¿Qué porcentaje de tickets se atiende dentro del plazo?

### Calidad
* ¿Cuáles son las razones más frecuentes de las incidencias?

### Satisfacción del Cliente
* ¿Cómo perciben los usuarios la velocidad de atención de sus solicitudes?
* ¿Se están resolviendo efectivamente las solicitudes reportadas por los usuarios?

---

## 5. Conclusiones y recomendaciones

* **Dificultades en la integración:** Al realizar el pipeline ETL se presentaron dificultades para establecer la llave entre los datos de Jira y las encuestas de SharePoint. Esto debido a que, en el formulario de encuestas, el número de ticket y el nombre de la compañía son digitados manualmente por el usuario. Dicha práctica generó inconsistencias como variaciones en la escritura de una misma empresa, ausencia de siglas en los tickets o identificadores numéricos con longitudes incorrectas.
* **Recomendaciones de mejora:** Se recomienda a la empresa reemplazar el campo de texto libre *Nombre de la Compañía* por el número de identificación NIT o una lista desplegable estandarizada. Asimismo, se sugiere implementar validaciones en el campo *Número de Ticket* para que se restrinja solamente a recibir números.
* **Limitación de datos históricos:** Debido a que algunos campos del archivo CSV exportado de Jira fueron implementados recientemente, no se dispone de información histórica correspondiente a años anteriores a 2026.