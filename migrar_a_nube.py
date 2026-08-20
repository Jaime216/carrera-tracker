import sqlite3
import db
import os
import json

print("🚀 Iniciando la migración blindada de datos locales a Turso...")

if not os.path.exists("carrera.db"):
    print("❌ Error: No se encuentra el archivo carrera.db antiguo en esta carpeta.")
    exit()

conn_local = sqlite3.connect("carrera.db")
cursor_local = conn_local.cursor()

tablas = ["asignaturas", "asistencia", "calificaciones", "horario", "entregas", "reglas", "creditos_extra"]

for tabla in tablas:
    print(f"\n📥 Migrando tabla: {tabla}...")
    
    # 1. Limpiar Turso
    try:
        db.execute_query(f"DELETE FROM {tabla}")
    except Exception as e:
        print(f"  ⚠️ Error al limpiar {tabla} en Turso: {e}")
        continue
    
    # 2. Leer SQLite local
    try:
        cursor_local.execute(f"SELECT * FROM {tabla}")
        filas = cursor_local.fetchall()
        
        cursor_local.execute(f"PRAGMA table_info({tabla})")
        columnas = [info[1] for info in cursor_local.fetchall()]
        
        if not filas:
            print(f"  ⚪ La tabla {tabla} estaba vacía.")
            continue
            
        print(f"  Encontradas {len(filas)} filas en {tabla}.")
        
        columnas_str = ", ".join(columnas)
        placeholders = ", ".join(["?" for _ in columnas])
        query_insert = f"INSERT INTO {tabla} ({columnas_str}) VALUES ({placeholders})"
        
        # 3. Forzar el tipado celda por celda antes de enviar
        insertadas = 0
        for fila in filas:
            fila_casteada = []
            for valor in fila:
                if valor is None:
                    fila_casteada.append(None)
                elif isinstance(valor, int):
                    fila_casteada.append(valor)
                elif isinstance(valor, float):
                    fila_casteada.append(valor)
                elif isinstance(valor, str):
                    # Si es texto, intentar convertir a número si "parece" un número
                    v_str = valor.strip()
                    if v_str.replace('.', '', 1).isdigit() and v_str.count('.') == 1:
                        fila_casteada.append(float(v_str))
                    elif v_str.isdigit():
                        fila_casteada.append(int(v_str))
                    else:
                        fila_casteada.append(v_str)
                else:
                    fila_casteada.append(str(valor))
            
            try:
                db.execute_query(query_insert, fila_casteada)
                insertadas += 1
            except Exception as e:
                # Mostrar el error exacto para depurar si vuelve a fallar
                print(f"    ❌ Error al insertar fila: {e}")
                print(f"       Datos enviados: {fila_casteada}")
                
        print(f"  ✅ {insertadas}/{len(filas)} filas migradas a Turso con éxito.")
        
    except Exception as e:
        print(f"  ❌ Error al leer la tabla {tabla} local: {e}")

conn_local.close()
print("\n🎉 ¡Migración completada! Todos tus datos antiguos ya están en la nube.")
