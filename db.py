import pandas as pd
import uuid
from datetime import datetime
import streamlit as st
import sqlite3
import requests

# ------------------------------------------------------------------------------
# CONEXIÓN A TURSO (Vía API HTTP)
# ------------------------------------------------------------------------------
TURSO_URL = st.secrets["TURSO_URL"].replace("libsql://", "https://")
TURSO_AUTH_TOKEN = st.secrets["TURSO_AUTH_TOKEN"]

DB_FILE = "carrera.db" # Lo mantenemos por compatibilidad con app.py

def execute_query(query, params=None):
    """Ejecuta una consulta SQL en Turso a través de su API HTTP."""
    headers = {
        "Authorization": f"Bearer {TURSO_AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Formatear parámetros para la API de Turso
    args = []
    if params:
        for p in params:
            if isinstance(p, (int, float)):
                args.append({"type": "float" if isinstance(p, float) else "integer", "value": str(p)})
            elif p is None:
                args.append({"type": "null"})
            else:
                args.append({"type": "text", "value": str(p)})
    
    payload = {
        "requests": [
            {
                "type": "execute",
                "stmt": {
                    "sql": query,
                    "args": args
                }
            },
            {"type": "close"}
        ]
    }
    
    response = requests.post(f"{TURSO_URL}/v2/pipeline", headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Error de base de datos: {response.text}")
    
    return response.json()

def get_table(table_name: str) -> pd.DataFrame:
    try:
        res = execute_query(f"SELECT * FROM {table_name.lower()}")
        results = res["results"][0]
        if "response" in results and "result" in results["response"]:
            data = results["response"]["result"]
            cols = [col["name"] for col in data["cols"]]
            rows = []
            for r in data["rows"]:
                row_data = []
                for val in r:
                    if val["type"] == "null":
                        row_data.append(None)
                    elif val["type"] in ["integer", "float"]:
                        row_data.append(float(val["value"]))
                    else:
                        row_data.append(val["value"])
                rows.append(row_data)
            return pd.DataFrame(rows, columns=cols)
        return pd.DataFrame()
    except Exception as e:
        print(f"Error al leer la tabla {table_name}: {e}")
        return pd.DataFrame()

def init_db():
    queries = [
        '''CREATE TABLE IF NOT EXISTS asignaturas (
            id_asignatura TEXT PRIMARY KEY, nombre TEXT, curso INTEGER, 
            cuatrimestre INTEGER, creditos REAL, min_asistencia_pct REAL, 
            estado TEXT, nota_final REAL, comentarios TEXT, num_matricula INTEGER,
            link_guia TEXT, link_campus TEXT, link_apuntes TEXT)''',
        '''CREATE TABLE IF NOT EXISTS asistencia (
            id_registro TEXT PRIMARY KEY, fecha TEXT, id_asignatura TEXT, 
            estado TEXT, observaciones TEXT, tipo TEXT)''',
        '''CREATE TABLE IF NOT EXISTS calificaciones (
            id_evaluacion TEXT PRIMARY KEY, id_asignatura TEXT, concepto TEXT, 
            ponderacion_pct REAL, nota REAL, fecha TEXT, estado TEXT, tipo TEXT, nota_minima REAL)''',
        '''CREATE TABLE IF NOT EXISTS horario (
            id_horario TEXT PRIMARY KEY, id_asignatura TEXT, dia_semana TEXT, 
            hora_inicio TEXT, hora_fin TEXT, tipo TEXT, frecuencia TEXT)''',
        '''CREATE TABLE IF NOT EXISTS entregas (
            id_entrega TEXT PRIMARY KEY, id_asignatura TEXT, descripcion TEXT, 
            fecha_limite TEXT, ponderacion REAL, completada INTEGER)''',
        '''CREATE TABLE IF NOT EXISTS reglas (
            id_regla TEXT PRIMARY KEY, id_asignatura TEXT, descripcion TEXT, 
            tipo TEXT, ids_evaluaciones TEXT, valor_exigido REAL)''',
        '''CREATE TABLE IF NOT EXISTS creditos_extra (
            id_credito TEXT PRIMARY KEY, descripcion TEXT, creditos REAL, fecha TEXT)'''
    ]
    
    for q in queries:
        try:
            execute_query(q)
        except:
            pass

init_db()

# ------------------------------------------------------------------------------
# ASISTENCIA
# ------------------------------------------------------------------------------
def add_asistencia(id_asignatura: str, estado: str, observaciones: str = "", fecha: str = None, tipo: str = "Teoría"):
    fecha_str = fecha if fecha else datetime.now().strftime("%Y-%m-%d")
    id_registro = str(uuid.uuid4())[:8]
    execute_query("INSERT INTO asistencia VALUES (?, ?, ?, ?, ?, ?)", 
                  (id_registro, fecha_str, id_asignatura, estado, observaciones, tipo))
    return True

def edit_asistencia(id_registro: str, estado: str, observaciones: str, fecha: str, tipo: str):
    execute_query("UPDATE asistencia SET estado=?, observaciones=?, fecha=?, tipo=? WHERE id_registro=?", 
                  (estado, observaciones, fecha, tipo, id_registro))
    return True

def delete_asistencia(id_registro: str):
    execute_query("DELETE FROM asistencia WHERE id_registro = ?", (id_registro,))
    return True

# ------------------------------------------------------------------------------
# CALIFICACIONES
# ------------------------------------------------------------------------------
def add_calificacion(id_asignatura: str, concepto: str, ponderacion: float, nota: float = None, fecha: str = None, estado: str = "Realizado", tipo: str = "Teoría", nota_minima: float = 0.0):
    fecha_str = fecha if fecha else datetime.now().strftime("%Y-%m-%d")
    id_eval = str(uuid.uuid4())[:8]
    execute_query("INSERT INTO calificaciones VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                  (id_eval, id_asignatura, concepto, ponderacion, nota, fecha_str, estado, tipo, nota_minima))
    return True

def update_calificacion(id_evaluacion: str, nueva_nota: float):
    execute_query("UPDATE calificaciones SET nota = ?, estado = 'Realizado' WHERE id_evaluacion = ?", 
                  (nueva_nota, id_evaluacion))
    return True

def edit_calificacion(id_evaluacion: str, concepto: str, ponderacion: float, nota: float, fecha: str, tipo: str, nota_minima: float):
    execute_query("UPDATE calificaciones SET concepto=?, ponderacion_pct=?, nota=?, fecha=?, tipo=?, nota_minima=? WHERE id_evaluacion=?", 
                  (concepto, ponderacion, nota, fecha, tipo, nota_minima, id_evaluacion))
    return True

def delete_calificacion(id_evaluacion: str):
    execute_query("DELETE FROM calificaciones WHERE id_evaluacion = ?", (id_evaluacion,))
    return True

# ------------------------------------------------------------------------------
# ASIGNATURAS Y EXPEDIENTE
# ------------------------------------------------------------------------------
def add_asignatura(nombre: str, curso: int, cuatrimestre: int, creditos: float, min_asistencia_pct: float, comentarios: str = "", num_matricula: int = 1, link_guia: str = "", link_campus: str = "", link_apuntes: str = ""):
    df_existentes = get_table("asignaturas")
    siguiente = 1
    nuevo_id = f"ASIG-{siguiente:02d}"
    if not df_existentes.empty:
        existentes = df_existentes["id_asignatura"].tolist()
        while nuevo_id in existentes:
            siguiente += 1
            nuevo_id = f"ASIG-{siguiente:02d}"
    
    execute_query("""
        INSERT INTO asignaturas 
        (id_asignatura, nombre, curso, cuatrimestre, creditos, min_asistencia_pct, estado, nota_final, comentarios, num_matricula, link_guia, link_campus, link_apuntes) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
        (nuevo_id, nombre.strip(), int(curso), int(cuatrimestre), float(creditos), float(min_asistencia_pct), "Cursando", 0.0, comentarios, int(num_matricula), link_guia, link_campus, link_apuntes))
    return nuevo_id

def edit_asignatura(id_asignatura: str, nombre: str, curso: int, cuatrimestre: int, creditos: float, min_asistencia_pct: float, comentarios: str, num_matricula: int, link_guia: str, link_campus: str, link_apuntes: str):
    execute_query("""
        UPDATE asignaturas 
        SET nombre=?, curso=?, cuatrimestre=?, creditos=?, min_asistencia_pct=?, 
            comentarios=?, num_matricula=?, link_guia=?, link_campus=?, link_apuntes=? 
        WHERE id_asignatura=?""", 
        (nombre.strip(), int(curso), int(cuatrimestre), float(creditos), float(min_asistencia_pct), comentarios, int(num_matricula), link_guia, link_campus, link_apuntes, id_asignatura))
    return True

def delete_asignatura(id_asignatura: str):
    execute_query("DELETE FROM asignaturas WHERE id_asignatura = ?", (id_asignatura,))
    return True

def aprobar_asignatura(id_asignatura: str, nota_final: float):
    execute_query("UPDATE asignaturas SET estado = 'Aprobada', nota_final = ? WHERE id_asignatura = ?", 
                  (nota_final, id_asignatura))
    return True

def suspender_asignatura(id_asignatura: str, nota_final: float):
    execute_query("UPDATE asignaturas SET estado = 'Suspensada', nota_final = ? WHERE id_asignatura = ?", 
                  (nota_final, id_asignatura))
    return True

# ------------------------------------------------------------------------------
# HORARIO
# ------------------------------------------------------------------------------
def add_horario(id_asignatura: str, dia: str, inicio: str, fin: str, tipo: str = "Teoría", frecuencia: str = "Todas"):
    id_hor = str(uuid.uuid4())[:8]
    execute_query("INSERT INTO horario (id_horario, id_asignatura, dia_semana, hora_inicio, hora_fin, tipo, frecuencia) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                  (id_hor, id_asignatura, dia, inicio, fin, tipo, frecuencia))
    return True

def edit_horario(id_horario: str, dia: str, inicio: str, fin: str, tipo: str, frecuencia: str):
    execute_query("UPDATE horario SET dia_semana=?, hora_inicio=?, hora_fin=?, tipo=?, frecuencia=? WHERE id_horario=?", 
                  (dia, inicio, fin, tipo, frecuencia, id_horario))
    return True

def delete_horario(id_horario: str):
    execute_query("DELETE FROM horario WHERE id_horario = ?", (id_horario,))
    return True

# ------------------------------------------------------------------------------
# ENTREGAS
# ------------------------------------------------------------------------------
def add_entrega(id_asignatura: str, descripcion: str, fecha_limite: str, ponderacion: float = None):
    id_ent = str(uuid.uuid4())[:8]
    execute_query("INSERT INTO entregas VALUES (?, ?, ?, ?, ?, ?)", 
                  (id_ent, id_asignatura, descripcion, fecha_limite, ponderacion, 0))
    return True

def toggle_entrega(id_entrega: str, estado_completada: int):
    execute_query("UPDATE entregas SET completada = ? WHERE id_entrega = ?", 
                  (estado_completada, id_entrega))
    return True

def edit_entrega(id_entrega: str, descripcion: str, fecha_limite: str, ponderacion: float):
    execute_query("UPDATE entregas SET descripcion=?, fecha_limite=?, ponderacion=? WHERE id_entrega=?", 
                  (descripcion, fecha_limite, ponderacion, id_entrega))
    return True

def delete_entrega(id_entrega: str):
    execute_query("DELETE FROM entregas WHERE id_entrega = ?", (id_entrega,))
    return True

# ------------------------------------------------------------------------------
# REGLAS Y CRÉDITOS EXTRA
# ------------------------------------------------------------------------------
def add_regla(id_asignatura: str, descripcion: str, tipo: str, ids_evaluaciones: str, valor_exigido: float):
    id_regla = str(uuid.uuid4())[:8]
    execute_query("INSERT INTO reglas VALUES (?, ?, ?, ?, ?, ?)", 
                  (id_regla, id_asignatura, descripcion, tipo, ids_evaluaciones, float(valor_exigido)))
    return True

def delete_regla(id_regla: str):
    execute_query("DELETE FROM reglas WHERE id_regla = ?", (id_regla,))
    return True

def add_credito_extra(descripcion: str, creditos: float, fecha: str):
    id_credito = str(uuid.uuid4())[:8]
    execute_query("INSERT INTO creditos_extra VALUES (?, ?, ?, ?)", 
                  (id_credito, descripcion, float(creditos), fecha))
    return True

def delete_credito_extra(id_credito: str):
    execute_query("DELETE FROM creditos_extra WHERE id_credito = ?", (id_credito,))
    return True

def reset_db():
    for tabla in ["asignaturas", "asistencia", "calificaciones", "horario", "entregas", "reglas", "creditos_extra"]:
        try: execute_query(f"DELETE FROM {tabla}")
        except: pass
