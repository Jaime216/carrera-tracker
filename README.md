# 🎓 Control de Carrera Universitaria

Una aplicación web interactiva desarrollada con **Streamlit** para gestionar de forma integral tu expediente académico. Centraliza horarios, asistencia, calificaciones y entregas en un entorno rápido y seguro.

---

## ✨ Características Principales

* **📈 Dashboard Dinámico:** Visualización de ECTS superados, nota media y rendimiento por asignatura mediante gráficos interactivos.
* **🗓️ Horario Inteligente:** Cuadrícula de clases adaptable (mañana/tarde) con sistema automático de rotación para semanas pares e impares.
* **🧮 Simulador de Notas:** Proyección de calificaciones finales y cálculo matemático de la nota exacta necesaria en futuros exámenes para aprobar.
* **📝 Asistencia y Entregas:** Registro de faltas con alertas visuales de mínimos exigidos y gestor de tareas pendientes por fecha límite.
* **🔒 Autenticación Segura:** Sistema de acceso protegido persistente basado en tokens de URL nativos de Streamlit.
* **⚡ Rendimiento Optimizado:** Navegación instantánea entre pestañas gracias a la gestión avanzada de memoria con `@st.cache_data`.
* **💾 Copias de Seguridad:** Integración en la nube con Turso (SQLite) y herramientas de exportación/importación de backups locales.

---

## 🛠️ Tecnologías Utilizadas

* **Frontend y Lógica:** Python, Streamlit
* **Manipulación de Datos:** Pandas
* **Visualización:** Plotly
* **Base de Datos:** Turso / SQLite (vía API REST con `requests`)

---

## 🚀 Instalación y Despliegue Local

### 1. Clonar el repositorio y preparar el entorno
Abre tu terminal y ejecuta los siguientes comandos:

```bash
git clone [https://github.com/TU_USUARIO/TU_REPOSITORIO.git](https://github.com/TU_USUARIO/TU_REPOSITORIO.git)
cd TU_REPOSITORIO
python -m venv .venv
