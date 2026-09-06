import db
from datetime import date

print("🚀 Insertando datos de prueba para la paridad de semanas...")

# 1. Configurar la paridad de referencia
# Usamos una fecha reciente (por ejemplo, el lunes pasado o de esta semana)
fecha_ref = "2026-09-07" # Lunes de esta semana actual
tipo_ref = "Impares"     # Definimos que esta primera semana es Impar

db.set_paridad_config(fecha_ref, tipo_ref)
print(f"✅ Configuración de paridad guardada: Semana del {fecha_ref} fijada como {tipo_ref}.")

# 2. Buscar o crear una asignatura activa para las pruebas
df_asig = db.get_table("asignaturas")
id_asig_prueba = None

if not df_asig.empty:
    # Cogemos la primera asignatura que esté "Cursando"
    activas = df_asig[df_asig["estado"] == "Cursando"]
    if not activas.empty:
        id_asig_prueba = str(activas.iloc[0]["id_asignatura"])
        print(f"ℹ️ Usando asignatura existente para pruebas: {activas.iloc[0]['nombre']} ({id_asig_prueba})")

# Si no hay ninguna asignatura cursando, creamos una de prueba
if not id_asig_prueba:
    id_asig_prueba = db.add_asignatura(
        nombre="Sistemas Inteligentes (Test)", 
        curso=3, 
        cuatrimestre=1, 
        creditos=6.0, 
        min_asistencia_pct=80.0, 
        comentarios="Asignatura creada automáticamente para probar frecuencias pares e impares"
    )
    print(f"✅ Creada asignatura de prueba con ID: {id_asig_prueba}")

# 3. Añadir clases al horario con diferentes frecuencias
# Borramos horario previo de prueba si lo hubiera para evitar duplicados masivos
print("🕒 Añadiendo clases de prueba al horario...")

# Clase 1: Teoría (Todas las semanas) los Miércoles de 09:00 a 11:00
db.add_horario(id_asig_prueba, "Miércoles", "09:00", "11:00", tipo="Teoría", frecuencia="Todas")

# Clase 2: Laboratorio (Semanas Impares) los Miércoles a la misma hora (09:00 a 11:00)
db.add_horario(id_asig_prueba, "Miércoles", "09:00", "11:00", tipo="Laboratorio", frecuencia="Impares")

# Clase 3: Prácticas (Semanas Pares) los Jueves de 11:00 a 13:00
db.add_horario(id_asig_prueba, "Jueves", "11:00", "13:00", tipo="Laboratorio", frecuencia="Pares")

print("✅ ¡Clases de prueba añadidas con éxito al horario!")
print("\n🎉 Ya puedes arrancar Streamlit (streamlit run app.py) y revisar la pestaña 'Horario'.")

