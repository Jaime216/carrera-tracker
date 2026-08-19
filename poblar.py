import db
from datetime import datetime, timedelta
import time
import pandas as pd

print("🚀 Iniciando el proceso de poblado (V5 - Escenario Avanzado)...")

# 0. VACIAR BASE DE DATOS
print("\n🧹 Vaciando la base de datos local (SQLite)...")
db.reset_db()
time.sleep(1)

# 1. CREAR ASIGNATURAS (Añadido Num. Matrícula y Comentarios)
print("\n📚 Creando asignaturas (Incluyendo 2ª Matrícula y Comentarios)...")
id_prog = db.add_asignatura("Fundamentos de Programación", 1, 1, 6.0, 80.0, "Profesor muy estricto corrigiendo.", 1)
id_mat = db.add_asignatura("Álgebra Lineal", 1, 1, 6.0, 75.0, "Hay que llevar calculadora científica no programable.", 1)

# Historial de Física: Suspendida en la Matrícula 1, cursando en la Matrícula 2
id_fis_m1 = db.add_asignatura("Física Básica", 1, 1, 6.0, 70.0, "Suspendí por no hacer las prácticas.", 1)
db.suspender_asignatura(id_fis_m1, 3.5) # La marcamos como Suspensada

id_fis_m2 = db.add_asignatura("Física Básica", 1, 1, 6.0, 70.0, "Ojo, me lo juego todo a esta 2ª Matrícula.", 2)

# Asignatura Aprobada
id_hist = db.add_asignatura("Historia de la Computación", 1, 1, 3.0, 50.0, "Convalidada / Aprobada fácil", 1)
db.aprobar_asignatura(id_hist, 8.5)

# 2. HORARIO
print("🕒 Configurando horario semanal...")
db.add_horario(id_prog, "Lunes", "09:00", "11:00")
db.add_horario(id_prog, "Miércoles", "09:00", "11:00")
db.add_horario(id_mat, "Martes", "11:00", "13:00")
db.add_horario(id_mat, "Jueves", "11:00", "13:00")
db.add_horario(id_fis_m2, "Lunes", "11:00", "13:00") 
db.add_horario(id_fis_m2, "Viernes", "10:00", "12:00")

hoy = datetime.now()
dias_pasados = [hoy - timedelta(days=i) for i in range(30)]
dias_futuros = [hoy + timedelta(days=i) for i in range(1, 20)]

# 3. ASISTENCIA
print("📝 Creando registros de asistencia...")
db.add_asistencia(id_prog, "Presente", "Introducción a Python", str(dias_pasados[14].date()), "Teoría")
db.add_asistencia(id_prog, "Falta", "No sonó el despertador", str(dias_pasados[12].date()), "Teoría")
db.add_asistencia(id_fis_m2, "Presente", "Práctica de Cinemática", str(dias_pasados[10].date()), "Laboratorio")
db.add_asistencia(id_mat, "Justificada", "Médico", str(dias_pasados[2].date()), "Teoría")

# 4. CALIFICACIONES (Mínimos y Planificados)
print("📊 Creando notas (con límites y planificados)...")
# Programación: Forzaremos un bloqueo por nota mínima en el Parcial 2
db.add_calificacion(id_prog, "Parcial 1", 20.0, 7.0, str(dias_pasados[10].date()), "Realizado", "Teoría", 4.0)
db.add_calificacion(id_prog, "Parcial 2", 20.0, 3.5, str(dias_pasados[2].date()), "Realizado", "Teoría", 4.0) # <-- BLOQUEO
db.add_calificacion(id_prog, "Examen Final", 60.0, None, str(dias_futuros[12].date()), "Pendiente", "Teoría", 5.0)

# Mates: Planificamos múltiples exámenes para ver cómo los suma el simulador
db.add_calificacion(id_mat, "Control 1", 30.0, 6.5, str(dias_pasados[5].date()), "Realizado", "Teoría", 0.0)
db.add_calificacion(id_mat, "Práctica Laboratorio", 20.0, None, str(dias_futuros[5].date()), "Pendiente", "Laboratorio", 0.0)
db.add_calificacion(id_mat, "Examen Final", 50.0, None, str(dias_futuros[15].date()), "Pendiente", "Teoría", 5.0)

# Física M2: Para probar la regla conjunta
db.add_calificacion(id_fis_m2, "Bloque A", 25.0, 5.0, str(dias_pasados[8].date()), "Realizado", "Teoría", 0.0)
db.add_calificacion(id_fis_m2, "Bloque B", 25.0, 3.0, str(dias_pasados[3].date()), "Realizado", "Teoría", 0.0)
db.add_calificacion(id_fis_m2, "Laboratorio Final", 50.0, None, str(dias_futuros[10].date()), "Pendiente", "Laboratorio", 5.0)

# 5. ENTREGAS
print("📌 Creando entregas y tareas...")
db.add_entrega(id_prog, "Ejercicios Bucles (Opcional sin nota)", str(dias_pasados[5].date()), None)
db.add_entrega(id_mat, "Hoja de problemas 2", str(dias_futuros[2].date()), 5.0)
db.add_entrega(id_fis_m2, "Informe de Laboratorio 1", str(dias_pasados[1].date()), 10.0)

# Vamos a marcar completada una de las entregas
df_entregas = db.get_table("entregas")
if not df_entregas.empty:
    id_ent_prog = df_entregas[df_entregas["id_asignatura"] == id_prog].iloc[0]["id_entrega"]
    db.toggle_entrega(id_ent_prog, 1)

# 6. REGLAS ESPECIALES
print("⚙️ Configurando reglas de evaluación conjuntas...")
df_notas = db.get_table("calificaciones")
if not df_notas.empty:
    # Regla para Física M2: La media del Bloque A y Bloque B debe ser mínimo 4.5
    notas_fis = df_notas[df_notas["id_asignatura"] == id_fis_m2]
    if len(notas_fis) >= 2:
        id_b1 = notas_fis[notas_fis["concepto"] == "Bloque A"].iloc[0]["id_evaluacion"]
        id_b2 = notas_fis[notas_fis["concepto"] == "Bloque B"].iloc[0]["id_evaluacion"]
        db.add_regla(id_fis_m2, "Media teórica de Bloques A+B", "Media Mínima", f"{id_b1},{id_b2}", 4.5)

print("\n✅ ¡Base de datos poblada con todas las nuevas mecánicas con éxito!")
