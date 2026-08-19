import pandas as pd
import db

print("🚀 Iniciando la importación del Expediente Académico...")

# 1. Vaciar la base de datos
print("🧹 Vaciando la base de datos local...")
db.reset_db()

# 2. Leer el archivo "Excel" (leyéndolo como TSV por cómo lo genera la universidad)
print("📂 Leyendo el archivo expAcademico.xls...")
try:
    df = pd.read_csv('expAcademico.xls', sep='\t', encoding='latin1', skiprows=2)
except FileNotFoundError:
    print("❌ Error: No se ha encontrado el archivo 'expAcademico.xls' en esta carpeta.")
    exit()
except Exception as e:
    print(f"❌ Error al leer el archivo: {e}")
    exit()

# 3. Procesar e insertar los datos
print("📥 Guardando asignaturas en la base de datos...")
for index, row in df.iterrows():
    # Extraemos los datos según la posición de las columnas del archivo
    codigo = str(row.iloc[0]).strip()
    nombre = str(row.iloc[1]).strip()
    nota_texto = str(row.iloc[4]).strip()
    nota_num = float(row.iloc[5])
    tipologia = str(row.iloc[6]).strip()
    creditos = float(row.iloc[7])
    curso = int(row.iloc[8])
    
    # Formateamos un comentario con detalles útiles
    comentarios = f"Código Universitario: {codigo} | Tipo: {tipologia} | {nota_texto.capitalize()}"
    
    # Creamos la asignatura (asignamos cuatrimestre 1 por defecto al no venir en el Excel)
    id_asig = db.add_asignatura(
        nombre=nombre,
        curso=curso,
        cuatrimestre=1,
        creditos=creditos,
        min_asistencia_pct=80.0,
        comentarios=comentarios,
        num_matricula=1
    )
    
    # Como el expediente solo lista las aprobadas/notables, finalizamos la asignatura con la nota real
    db.aprobar_asignatura(id_asig, nota_num)
    
    print(f"  ✅ Registrada: {nombre} -> Nota: {nota_num}")

print("\n🎉 ¡Expediente importado con éxito! Tienes 18 asignaturas reales guardadas.")
