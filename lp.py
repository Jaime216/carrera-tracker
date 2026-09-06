import db
import pandas as pd

def limpiar_horarios_antiguos():
    print("🧹 Iniciando limpieza de horarios antiguos...")
    
    # 1. Definir las franjas válidas exactas que hemos establecido en la app
    franjas_validas = [
        ("08:30", "10:20"),
        ("10:40", "12:30"),
        ("12:40", "14:30"),
        ("15:30", "17:20"),
        ("17:40", "19:30"),
        ("19:40", "21:30")
    ]
    
    # 2. Obtener todos los datos de la tabla horario
    try:
        df_horario = db.get_table("horario")
    except Exception as e:
        print(f"❌ Error al conectar con la base de datos: {e}")
        return

    if df_horario.empty:
        print("El horario está vacío. No hay nada que limpiar.")
        return

    eliminados = 0
    
    # 3. Revisar cada registro uno por uno
    for _, row in df_horario.iterrows():
        h_ini = str(row['hora_inicio']).strip()
        h_fin = str(row['hora_fin']).strip()
        id_h = str(row['id_horario'])
        
        # Comprobar si la pareja de horas no está en nuestra lista de permitidas
        if (h_ini, h_fin) not in franjas_validas:
            print(f"🗑️ Eliminando clase desfasada: ({h_ini} - {h_fin}) | ID: {id_h}")
            db.delete_horario(id_h)
            eliminados += 1
            
    print("-" * 40)
    print(f"✨ ¡Limpieza completada! Se han eliminado {eliminados} registros huérfanos.")

if __name__ == "__main__":
    limpiar_horarios_antiguos()
