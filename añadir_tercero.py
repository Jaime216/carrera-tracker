import db

print("🚀 Añadiendo las asignaturas del nuevo curso al expediente...")

# Asignaturas del 1º Cuatrimestre (Nombre, Siglas)
asignaturas_c1 = [
    ("DISEÑO Y PRUEBAS I", "DP1"),
    ("INGENIERÍA DE REQUISITOS", "IR"),
    ("MODELADO Y SIMULACIÓN NUMÉRICA", "MSN"),
    ("PROCESO SOFTWARE Y GESTIÓN I", "PSG1"),
    ("PROCESAMIENTO DE SEÑALES MULTIMEDIA", "PSM")
]

# Asignaturas del 2º Cuatrimestre (Nombre, Siglas)
asignaturas_c2 = [
    ("ARQUITECTURA Y SERVICIOS DE REDES", "ASR"),
    ("DISEÑO Y PRUEBAS II", "DP2"),
    ("INTELIGENCIA ARTIFICIAL", "IA"),
    ("MODELADO Y VISUALIZACIÓN GRÁFICA", "MVG"),
    ("PROCESO SOFTWARE Y GESTIÓN II", "PSG2")
]

# Añadir Cuatrimestre 1
print("\n🍂 Añadiendo asignaturas del 1º Cuatrimestre:")
for nombre, siglas in asignaturas_c1:
    db.add_asignatura(
        nombre=nombre, 
        curso=3, 
        cuatrimestre=1, 
        creditos=6.0, 
        min_asistencia_pct=80.0, 
        comentarios=f"Siglas: {siglas}", 
        num_matricula=1
    )
    print(f"  ✅ {nombre} ({siglas})")

# Añadir Cuatrimestre 2
print("\n🌸 Añadiendo asignaturas del 2º Cuatrimestre:")
for nombre, siglas in asignaturas_c2:
    db.add_asignatura(
        nombre=nombre, 
        curso=3, 
        cuatrimestre=2, 
        creditos=6.0, 
        min_asistencia_pct=80.0, 
        comentarios=f"Siglas: {siglas}", 
        num_matricula=1
    )
    print(f"  ✅ {nombre} ({siglas})")

print("\n🎉 ¡Nuevas asignaturas añadidas con éxito! (Tu historial anterior sigue intacto).")
