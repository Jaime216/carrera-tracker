# 🎓 Carrera Tracker

Una aplicación de alto rendimiento desarrollada con **Streamlit** y **SQLite** para la gestión integral del expediente académico universitario. Adiós a las hojas de cálculo lentas y a las dependencias en la nube.

---

## 🚀 Características principales

| Función | Descripción |
|---|---|
| ⚡ **Velocidad instantánea** | Motor de base de datos local (SQLite) |
| 📚 **Control de expediente** | Gestión de cursos, cuatrimestres y segundas matrículas |
| 📅 **Calendario dinámico** | Visualización clara de clases, exámenes (reales/planificados) y entregas |
| 🧮 **Simulador de notas** | Calcula tu nota final proyectada y detecta incumplimientos de notas mínimas o reglas de evaluación conjuntas |
| ✅ **Gestor de tareas** | Lista de tareas pendiente/completada con impacto en nota |
| 🔒 **Seguridad** | Sistema de importación/exportación de copias de seguridad (.db) |

---

## 🛠️ Requisitos

- Python 3.x
- Librerías: `streamlit`, `pandas`, `plotly`

---

## ⚙️ Instalación y configuración

**1. Clonar el repositorio**

```bash
git clone https://github.com/Jaime216/carrera-tracker.git
cd carrera-tracker
```

**2. Instalar dependencias**

```bash
pip install -r requirements.txt
```

---

## ▶️ Ejecución

**Lanzar la aplicación:**

```bash
streamlit run app.py
```

**Poblar datos iniciales (opcional):**

Si es la primera vez que ejecutas la app y está vacía, puedes cargar un escenario de prueba profesional con:

```bash
python poblar.py
```

---

## ⚙️ Funcionalidades avanzadas

### 🧮 Simulador de notas

El simulador analiza:

- **Ponderaciones** — calcula el peso real evaluado vs. el restante.
- **Notas mínimas** — bloquea la proyección si alguna evaluación obligatoria no alcanza el mínimo de la guía docente.
- **Reglas conjuntas** — evalúa medias grupales (ej. "Media de parciales ≥ 4.0").
- **Simulación multi-input** — permite proyectar resultados en múltiples exámenes pendientes simultáneamente.

### 💾 Backup y restauración

En la pestaña **⚙️ Ajustes**, puedes descargar el archivo `carrera.db` para tener una copia de seguridad, o subir una versión antigua para restaurar tu estado académico.

---

## 📝 Changelog (v1.0.0)

- Lanzamiento inicial con SQLite.
- Sistema de gestión de evaluaciones con nota mínima individual.
- Gestor de tareas con impacto en nota.
- Simulador de notas con soporte para reglas de evaluación complejas.
- Sistema de importación/exportación de base de datos.

---

<p align="center">Desarrollado con ❤️ para organizar la carrera universitaria.</p>
