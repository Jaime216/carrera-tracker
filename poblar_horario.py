import db
import pandas as pd

print("🚀 Poblando el horario del 1º Cuatrimestre...")

# 1. Obtener la tabla de asignaturas
df_asig = db.get_table("asignaturas")

if df_asig.empty:
    print("❌ Error: No hay asignaturas en la base de datos.")
    exit()

# 2. Mapeo de siglas a nombres exactos (como los añadimos antes)
nombres = {
    "PSM": "PROCESAMIENTO DE SEÑALES MULTIMEDIA",
    "MSN": "MODELADO Y SIMULACIÓN NUMÉRICA",
    "DP1": "DISEÑO Y PRUEBAS I",
    "PSG1": "PROCESO SOFTWARE Y GESTIÓN I",
    "IR": "INGENIERÍA DE REQUISITOS"
}

# 3. Buscar los IDs de estas asignaturas en la base de datos
ids = {}
for sigla, nombre in nombres.items():
    match = df_asig[df_asig['nombre'] == nombre]
    if not match.empty:
        ids[sigla] = str(match.iloc[0]['id_asignatura'])
    else:
        print(f"⚠️ Advertencia: No se encontró la asignatura '{nombre}' en la BBDD.")

# 4. Limpiar el horario existente (para que no se dupliquen si lo ejecutas 2 veces)
df_horario = db.get_table("horario")
if not df_horario.empty:
    print("🧹 Limpiando el horario anterior...")
    for _, row in df_horario.iterrows():
        db.delete_horario(str(row["id_horario"]))

# 5. Lista de clases a insertar (Día, Hora Inicio, Hora Fin, Sigla)
clases = [
    # Lunes
    ("Lunes", "08:30", "10:20", "PSM"),
    ("Lunes", "10:40", "12:30", "MSN"),
    ("Lunes", "12:40", "14:30", "PSM"),
    # Martes
    ("Martes", "08:30", "10:20", "PSM"),
    ("Martes", "10:40", "12:30", "DP1"),
    ("Martes", "12:40", "14:30", "PSG1"),
    # Miércoles
    ("Miércoles", "10:40", "12:30", "PSM"),
    ("Miércoles", "12:40", "14:30", "IR"),
    # Jueves
    ("Jueves", "10:40", "12:30", "PSG1"),
    ("Jueves", "12:40", "14:30", "MSN"),
    # Viernes
    ("Viernes", "08:30", "10:20", "DP1"),
    ("Viernes", "10:40", "12:30", "IR")
]

# 6. Insertar en la base de datos
print("\n📅 Insertando clases:")
for dia, inicio, fin, sigla in clases:
    if sigla in ids:
        db.add_horario(ids[sigla], dia, inicio, fin)
        print(f"  ✅ {sigla} - {dia} ({inicio} a {fin})")

print("\n🎉 ¡Horario configurado con éxito! Recarga tu aplicación para verlo.")
