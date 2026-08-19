import sqlite3
import pandas as pd
import uuid
from datetime import datetime

DB_FILE = "carrera.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS asignaturas (
        id_asignatura TEXT PRIMARY KEY, nombre TEXT, curso INTEGER, 
        cuatrimestre INTEGER, creditos REAL, min_asistencia_pct REAL, 
        estado TEXT, nota_final REAL, comentarios TEXT, num_matricula INTEGER)''')
        
    try: cursor.execute("ALTER TABLE asignaturas ADD COLUMN comentarios TEXT")
    except: pass 
    try: cursor.execute("ALTER TABLE asignaturas ADD COLUMN num_matricula INTEGER DEFAULT 1")
    except: pass
        
    cursor.execute('''CREATE TABLE IF NOT EXISTS asistencia (
        id_registro TEXT PRIMARY KEY, fecha TEXT, id_asignatura TEXT, 
        estado TEXT, observaciones TEXT, tipo TEXT)''')
        
    cursor.execute('''CREATE TABLE IF NOT EXISTS calificaciones (
        id_evaluacion TEXT PRIMARY KEY, id_asignatura TEXT, concepto TEXT, 
        ponderacion_pct REAL, nota REAL, fecha TEXT, estado TEXT, tipo TEXT, nota_minima REAL)''')
        
    try: cursor.execute("ALTER TABLE calificaciones ADD COLUMN nota_minima REAL")
    except: pass
        
    cursor.execute('''CREATE TABLE IF NOT EXISTS horario (
        id_horario TEXT PRIMARY KEY, id_asignatura TEXT, dia_semana TEXT, 
        hora_inicio TEXT, hora_fin TEXT)''')
        
    cursor.execute('''CREATE TABLE IF NOT EXISTS entregas (
        id_entrega TEXT PRIMARY KEY, id_asignatura TEXT, descripcion TEXT, 
        fecha_limite TEXT, ponderacion REAL, completada INTEGER)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS reglas (
        id_regla TEXT PRIMARY KEY, id_asignatura TEXT, descripcion TEXT, 
        tipo TEXT, ids_evaluaciones TEXT, valor_exigido REAL)''')
        
    conn.commit()
    conn.close()

init_db()

def get_table(table_name: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query(f"SELECT * FROM {table_name.lower()}", conn)
    conn.close()
    return df

# ------------------------------------------------------------------------------
# ASISTENCIA
# ------------------------------------------------------------------------------
def add_asistencia(id_asignatura: str, estado: str, observaciones: str = "", fecha: str = None, tipo: str = "Teoría"):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    fecha_str = fecha if fecha else datetime.now().strftime("%Y-%m-%d")
    id_registro = str(uuid.uuid4())[:8]
    cursor.execute("INSERT INTO asistencia VALUES (?, ?, ?, ?, ?, ?)", 
                   (id_registro, fecha_str, id_asignatura, estado, observaciones, tipo))
    conn.commit()
    conn.close()
    return True

def edit_asistencia(id_registro: str, estado: str, observaciones: str, fecha: str, tipo: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE asistencia SET estado=?, observaciones=?, fecha=?, tipo=? WHERE id_registro=?", 
                   (estado, observaciones, fecha, tipo, id_registro))
    conn.commit()
    conn.close()
    return True

def delete_asistencia(id_registro: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM asistencia WHERE id_registro = ?", (id_registro,))
    conn.commit()
    conn.close()
    return True

# ------------------------------------------------------------------------------
# CALIFICACIONES
# ------------------------------------------------------------------------------
def add_calificacion(id_asignatura: str, concepto: str, ponderacion: float, nota: float = None, fecha: str = None, estado: str = "Realizado", tipo: str = "Teoría", nota_minima: float = 0.0):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    fecha_str = fecha if fecha else datetime.now().strftime("%Y-%m-%d")
    id_eval = str(uuid.uuid4())[:8]
    cursor.execute("INSERT INTO calificaciones VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                   (id_eval, id_asignatura, concepto, ponderacion, nota, fecha_str, estado, tipo, nota_minima))
    conn.commit()
    conn.close()
    return True

def update_calificacion(id_evaluacion: str, nueva_nota: float):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE calificaciones SET nota = ?, estado = 'Realizado' WHERE id_evaluacion = ?", 
                   (nueva_nota, id_evaluacion))
    conn.commit()
    conn.close()
    return True

def edit_calificacion(id_evaluacion: str, concepto: str, ponderacion: float, nota: float, fecha: str, tipo: str, nota_minima: float):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE calificaciones SET concepto=?, ponderacion_pct=?, nota=?, fecha=?, tipo=?, nota_minima=? WHERE id_evaluacion=?", 
                   (concepto, ponderacion, nota, fecha, tipo, nota_minima, id_evaluacion))
    conn.commit()
    conn.close()
    return True

def delete_calificacion(id_evaluacion: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM calificaciones WHERE id_evaluacion = ?", (id_evaluacion,))
    conn.commit()
    conn.close()
    return True

# ------------------------------------------------------------------------------
# ASIGNATURAS Y EXPEDIENTE
# ------------------------------------------------------------------------------
def add_asignatura(nombre: str, curso: int, cuatrimestre: int, creditos: float, min_asistencia_pct: float, comentarios: str = "", num_matricula: int = 1):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id_asignatura FROM asignaturas")
    existentes = [row[0] for row in cursor.fetchall()]
    siguiente = 1
    nuevo_id = f"ASIG-{siguiente:02d}"
    while nuevo_id in existentes:
        siguiente += 1
        nuevo_id = f"ASIG-{siguiente:02d}"
    cursor.execute("INSERT INTO asignaturas VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                   (nuevo_id, nombre.strip(), int(curso), int(cuatrimestre), float(creditos), float(min_asistencia_pct), "Cursando", 0.0, comentarios, int(num_matricula)))
    conn.commit()
    conn.close()
    return nuevo_id

def delete_asignatura(id_asignatura: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM asignaturas WHERE id_asignatura = ?", (id_asignatura,))
    conn.commit()
    conn.close()
    return True

def aprobar_asignatura(id_asignatura: str, nota_final: float):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE asignaturas SET estado = 'Aprobada', nota_final = ? WHERE id_asignatura = ?", 
                   (nota_final, id_asignatura))
    conn.commit()
    conn.close()
    return True

def suspender_asignatura(id_asignatura: str, nota_final: float):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE asignaturas SET estado = 'Suspensada', nota_final = ? WHERE id_asignatura = ?", 
                   (nota_final, id_asignatura))
    conn.commit()
    conn.close()
    return True

# ------------------------------------------------------------------------------
# HORARIO
# ------------------------------------------------------------------------------
def add_horario(id_asignatura: str, dia: str, inicio: str, fin: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    id_hor = str(uuid.uuid4())[:8]
    cursor.execute("INSERT INTO horario VALUES (?, ?, ?, ?, ?)", 
                   (id_hor, id_asignatura, dia, inicio, fin))
    conn.commit()
    conn.close()
    return True

def edit_horario(id_horario: str, dia: str, inicio: str, fin: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE horario SET dia_semana=?, hora_inicio=?, hora_fin=? WHERE id_horario=?", 
                   (dia, inicio, fin, id_horario))
    conn.commit()
    conn.close()
    return True

def delete_horario(id_horario: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM horario WHERE id_horario = ?", (id_horario,))
    conn.commit()
    conn.close()
    return True

# ------------------------------------------------------------------------------
# ENTREGAS
# ------------------------------------------------------------------------------
def add_entrega(id_asignatura: str, descripcion: str, fecha_limite: str, ponderacion: float = None):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    id_ent = str(uuid.uuid4())[:8]
    cursor.execute("INSERT INTO entregas VALUES (?, ?, ?, ?, ?, ?)", 
                   (id_ent, id_asignatura, descripcion, fecha_limite, ponderacion, 0))
    conn.commit()
    conn.close()
    return True

def toggle_entrega(id_entrega: str, estado_completada: int):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE entregas SET completada = ? WHERE id_entrega = ?", 
                   (estado_completada, id_entrega))
    conn.commit()
    conn.close()
    return True

def edit_entrega(id_entrega: str, descripcion: str, fecha_limite: str, ponderacion: float):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE entregas SET descripcion=?, fecha_limite=?, ponderacion=? WHERE id_entrega=?", 
                   (descripcion, fecha_limite, ponderacion, id_entrega))
    conn.commit()
    conn.close()
    return True

def delete_entrega(id_entrega: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM entregas WHERE id_entrega = ?", (id_entrega,))
    conn.commit()
    conn.close()
    return True

# ------------------------------------------------------------------------------
# REGLAS
# ------------------------------------------------------------------------------
def add_regla(id_asignatura: str, descripcion: str, tipo: str, ids_evaluaciones: str, valor_exigido: float):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    id_regla = str(uuid.uuid4())[:8]
    cursor.execute("INSERT INTO reglas VALUES (?, ?, ?, ?, ?, ?)", 
                   (id_regla, id_asignatura, descripcion, tipo, ids_evaluaciones, float(valor_exigido)))
    conn.commit()
    conn.close()
    return True

def delete_regla(id_regla: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reglas WHERE id_regla = ?", (id_regla,))
    conn.commit()
    conn.close()
    return True

def reset_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    for tabla in ["asignaturas", "asistencia", "calificaciones", "horario", "entregas", "reglas"]:
        cursor.execute(f"DELETE FROM {tabla}")
    conn.commit()
    conn.close()
