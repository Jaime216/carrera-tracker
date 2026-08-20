import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import calendar
from datetime import datetime, date
import db
import time

st.set_page_config(page_title="Control Académico", page_icon="🎓", layout="wide")


st.set_page_config(page_title="Control Académico", page_icon="🎓", layout="wide")

# ==============================================================================
# SISTEMA DE AUTENTICACIÓN SEGURO
# ==============================================================================
def check_password():
    """Retorna True si el usuario ha introducido la contraseña correcta."""
    
    # Si ya está autenticado en la sesión, no volvemos a pedir el login
    if st.session_state.get("password_correct", False):
        return True

    # Contenedor aislado para centrar el formulario y evitar elementos fantasma
    with st.container():
        st.markdown("<br><br>", unsafe_allow_html=True) # Pequeño espacio superior
        _, col_centro, _ = st.columns([1, 1.2, 1])
        
        with col_centro:
            st.markdown("### 🔒 Acceso Restringido")
            st.caption("Por favor, introduce tu contraseña para acceder al expediente.")
            
            with st.form("form_login"):
                password_input = st.text_input("Contraseña", type="password")
                submit_btn = st.form_submit_button("Entrar", use_container_width=True)
                
                if submit_btn:
                    # Lee del secreto o usa "1234" por defecto
                    password_correcta = st.secrets.get("PASSWORD", "1234")
                    
                    if password_input == password_correcta:
                        st.session_state["password_correct"] = True
                        st.rerun()
                    else:
                        st.error("❌ Contraseña incorrecta")

    return False

# Si no pasa el control de seguridad, detenemos la ejecución de toda la app aquí mismo
if not check_password():
    st.stop()

# ==============================================================================
# A PARTIR DE AQUÍ COMIENZA EL RESTO DE TU APLICACIÓN (app.py)
# ==============================================================================
st.title("🎓 Control de Carrera Universitaria")
# ... (todo tu código de carga de datos, pestañas y tablas va aquí debajo)




# ------------------------------------------------------------------------------
# 1. CARGA Y LIMPIEZA DE DATOS (CON PARCHES PANDAS)
# ------------------------------------------------------------------------------
try:
    df_asignaturas = db.get_table("asignaturas")
    df_asistencia = db.get_table("asistencia")
    df_notas = db.get_table("calificaciones")
    df_horario = db.get_table("horario")
    try: df_entregas = db.get_table("entregas")
    except: df_entregas = pd.DataFrame()
    try: df_reglas = db.get_table("reglas")
    except: df_reglas = pd.DataFrame()
    try: df_creditos_extra = db.get_table("creditos_extra")
    except: df_creditos_extra = pd.DataFrame()
except Exception as e:
    st.error(f"❌ Error al cargar la base de datos: {e}")
    st.stop()

hay_asignaturas = False
mapa_asignaturas = {}
mapa_nombres_rev = {}
mapa_activas = {}

if not df_asignaturas.empty:
    if "estado" not in df_asignaturas.columns: df_asignaturas["estado"] = "Cursando"
    df_asignaturas["estado"] = df_asignaturas["estado"].fillna("Cursando").replace("", "Cursando")
    
    if "nota_final" not in df_asignaturas.columns: df_asignaturas["nota_final"] = 0.0
    df_asignaturas["nota_final"] = pd.to_numeric(df_asignaturas["nota_final"], errors="coerce").fillna(0.0)
    
    if "creditos" not in df_asignaturas.columns: df_asignaturas["creditos"] = 0.0
    df_asignaturas["creditos"] = pd.to_numeric(df_asignaturas["creditos"], errors="coerce").fillna(0.0)
    
    if "num_matricula" not in df_asignaturas.columns: df_asignaturas["num_matricula"] = 1
    df_asignaturas["num_matricula"] = pd.to_numeric(df_asignaturas["num_matricula"], errors="coerce").fillna(1).astype(int)
    
    if "link_guia" not in df_asignaturas.columns: df_asignaturas["link_guia"] = ""
    df_asignaturas["link_guia"] = df_asignaturas["link_guia"].fillna("").astype(str)
    
    if "link_campus" not in df_asignaturas.columns: df_asignaturas["link_campus"] = ""
    df_asignaturas["link_campus"] = df_asignaturas["link_campus"].fillna("").astype(str)
    
    if "link_apuntes" not in df_asignaturas.columns: df_asignaturas["link_apuntes"] = ""
    df_asignaturas["link_apuntes"] = df_asignaturas["link_apuntes"].fillna("").astype(str)
    
    cols_asig = {str(c).strip().lower(): c for c in df_asignaturas.columns}
    col_id = cols_asig.get("id_asignatura") or cols_asig.get("id")
    col_nom = cols_asig.get("nombre") or cols_asig.get("asignatura")
    col_min_asis = cols_asig.get("min_asistencia_pct") or "min_asistencia_pct"

    if col_id and col_nom:
        hay_asignaturas = True
        df_asignaturas[col_min_asis] = pd.to_numeric(df_asignaturas[col_min_asis], errors="coerce").fillna(80.0)
        
        for _, row in df_asignaturas.iterrows():
            matricula_badge = f" (M{row['num_matricula']})" if row['num_matricula'] > 1 else ""
            txt = f"{row[col_id]} - {row[col_nom]}{matricula_badge}"
            mapa_asignaturas[txt] = str(row[col_id])
            mapa_nombres_rev[str(row[col_id])] = f"{row[col_nom]}{matricula_badge}"
            
            if row["estado"] == "Cursando":
                mapa_activas[txt] = str(row[col_id])

if not df_asistencia.empty:
    df_asistencia.columns = df_asistencia.columns.str.strip().str.lower()
    if "fecha" not in df_asistencia.columns: df_asistencia["fecha"] = pd.NA
    df_asistencia["fecha"] = pd.to_datetime(df_asistencia["fecha"], errors="coerce")
    
    if "tipo" not in df_asistencia.columns: df_asistencia["tipo"] = "Teoría"
    df_asistencia["tipo"] = df_asistencia["tipo"].fillna("Teoría").replace("", "Teoría")

if not df_notas.empty:
    df_notas.columns = df_notas.columns.str.strip().str.lower()
    
    if "nota" not in df_notas.columns: df_notas["nota"] = pd.NA
    df_notas["nota"] = pd.to_numeric(df_notas["nota"], errors="coerce")
    
    if "ponderacion_pct" not in df_notas.columns: df_notas["ponderacion_pct"] = pd.NA
    df_notas["ponderacion_pct"] = pd.to_numeric(df_notas["ponderacion_pct"], errors="coerce")
    
    if "nota_minima" not in df_notas.columns: df_notas["nota_minima"] = 0.0
    df_notas["nota_minima"] = pd.to_numeric(df_notas["nota_minima"], errors="coerce").fillna(0.0)
    
    if "fecha" not in df_notas.columns: df_notas["fecha"] = pd.NA
    df_notas["fecha"] = pd.to_datetime(df_notas["fecha"], errors="coerce")
    
    if "estado" not in df_notas.columns: df_notas["estado"] = "Realizado"
    df_notas["estado"] = df_notas["estado"].fillna("Realizado").replace("", "Realizado")
    
    if "tipo" not in df_notas.columns: df_notas["tipo"] = "Teoría"
    df_notas["tipo"] = df_notas["tipo"].fillna("Teoría").replace("", "Teoría")

if not df_entregas.empty:
    if "fecha_limite" not in df_entregas.columns: df_entregas["fecha_limite"] = pd.NA
    df_entregas["fecha_limite"] = pd.to_datetime(df_entregas["fecha_limite"], errors="coerce")
    
    if "completada" not in df_entregas.columns: df_entregas["completada"] = 0
    df_entregas["completada"] = pd.to_numeric(df_entregas["completada"], errors="coerce").fillna(0).astype(int)

# ------------------------------------------------------------------------------
# 2. PESTAÑAS DE LA APLICACIÓN
# ------------------------------------------------------------------------------
tab_dash, tab_horario, tab_asis, tab_eval, tab_entregas, tab_asig, tab_ajustes = st.tabs([
    "📈 Dashboard", "🕒 Horario", "📝 Asistencia", "📊 Calificaciones", "📌 Entregas", "📚 Asignaturas", "⚙️ Ajustes"
])

# ==============================================================================
# TAB 1: DASHBOARD
# ==============================================================================
with tab_dash:
    if not hay_asignaturas:
        st.info("Crea primero tus asignaturas en la pestaña **📚 Asignaturas**.")
    else:
        sub_graficos, sub_calendario = st.tabs(["📊 Gráficos y Métricas", "📅 Vista Calendario"])

        with sub_graficos:
            df_aprobadas = df_asignaturas[df_asignaturas["estado"] == "Aprobada"].copy()
            df_cursando = df_asignaturas[df_asignaturas["estado"] == "Cursando"].copy()
            
            creditos_asig = df_aprobadas["creditos"].sum() if not df_aprobadas.empty else 0.0
            creditos_ext = df_creditos_extra["creditos"].sum() if not df_creditos_extra.empty else 0.0
            creditos_totales = creditos_asig + creditos_ext
            
            media_expediente = 0.0
            if creditos_asig > 0:
                suma_ponderada = (df_aprobadas["nota_final"] * df_aprobadas["creditos"]).sum()
                media_expediente = round(suma_ponderada / creditos_asig, 2)

            st.subheader("Expediente Académico")
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            kpi1.metric("📚 Asig. Cursando", len(df_cursando))
            kpi2.metric("✅ Asig. Aprobadas", len(df_aprobadas))
            kpi3.metric("🏆 Créditos Superados", f"{creditos_totales} ECTS")
            kpi4.metric("⭐ Media Expediente", media_expediente)

            st.divider()
            
            if not df_notas.empty and "estado" in df_notas.columns:
                df_notas_realizadas = df_notas[df_notas["estado"] == "Realizado"]
            else:
                df_notas_realizadas = pd.DataFrame(columns=["id_asignatura", "nota", "ponderacion_pct", "estado"])

            col_g1, col_g2 = st.columns(2)

            with col_g1:
                st.markdown("#### 🎯 Rendimiento por Asignatura (En Curso)")
                notas_resumen = []
                for id_asig, nom_asig in mapa_nombres_rev.items():
                    if id_asig in mapa_activas.values():
                        if not df_notas_realizadas.empty and "id_asignatura" in df_notas_realizadas.columns:
                            sub_n = df_notas_realizadas[df_notas_realizadas["id_asignatura"] == id_asig]
                            if not sub_n.empty:
                                peso_total = sub_n["ponderacion_pct"].sum()
                                nota_acumulada = (sub_n["nota"] * (sub_n["ponderacion_pct"] / 100.0)).sum()
                                nota_sobre_10 = (nota_acumulada / (peso_total / 100.0)) if peso_total > 0 else 0
                                notas_resumen.append({"Asignatura": nom_asig, "Media Evaluada (0-10)": round(nota_sobre_10, 2)})
                            else:
                                notas_resumen.append({"Asignatura": nom_asig, "Media Evaluada (0-10)": 0.0})
                        else:
                            notas_resumen.append({"Asignatura": nom_asig, "Media Evaluada (0-10)": 0.0})

                df_plot_notas = pd.DataFrame(notas_resumen)
                if not df_plot_notas.empty:
                    fig_notas = go.Figure()
                    fig_notas.add_trace(go.Bar(
                        x=df_plot_notas["Asignatura"], y=df_plot_notas["Media Evaluada (0-10)"],
                        text=df_plot_notas["Media Evaluada (0-10)"], textposition="auto", marker_color="#4F46E5"
                    ))
                    fig_notas.add_hline(y=5.0, line_dash="dash", line_color="#EF4444", annotation_text="Aprobado")
                    fig_notas.update_layout(yaxis_range=[0, 10], template="plotly_white", height=350, margin=dict(l=20, r=20, t=30, b=20))
                    st.plotly_chart(fig_notas, width="stretch")
                else:
                    st.info("Sin datos de calificaciones.")

            with col_g2:
                st.markdown("#### 🛡️ Asistencia vs. Mínimo Exigido (%)")
                if df_asistencia.empty:
                    st.info("Aún no has registrado asistencias.")
                else:
                    asig_list = []
                    for _, row in df_asignaturas.iterrows():
                        aid = str(row[col_id])
                        if aid in mapa_activas.values():
                            anom = str(row[col_nom])
                            amin = float(row[col_min_asis]) if pd.notnull(row[col_min_asis]) else 80.0
                            sub_a = df_asistencia[df_asistencia["id_asignatura"] == aid]
                            tot = len(sub_a)
                            pct_real = round((len(sub_a[sub_a["estado"].isin(["Presente", "Justificada"])]) / tot) * 100, 1) if tot > 0 else 100.0
                            color = "#10B981" if pct_real >= amin else "#EF4444"
                            asig_list.append({"Asignatura": anom, "% Real": pct_real, "% Mínimo": amin, "Color": color})

                    df_plot_asis = pd.DataFrame(asig_list)
                    if not df_plot_asis.empty:
                        fig_asis = go.Figure()
                        fig_asis.add_trace(go.Bar(
                            x=df_plot_asis["Asignatura"], y=df_plot_asis["% Real"], marker_color=df_plot_asis["Color"],
                            text=[f"{v}%" for v in df_plot_asis["% Real"]], textposition="auto", name="% Real"
                        ))
                        fig_asis.add_trace(go.Scatter(
                            x=df_plot_asis["Asignatura"], y=df_plot_asis["% Mínimo"], mode="markers",
                            marker=dict(symbol="line-ew", size=30, line=dict(width=3, color="#1F2937")), name="Mínimo"
                        ))
                        fig_asis.update_layout(yaxis_range=[0, 105], template="plotly_white", height=350, margin=dict(l=20, r=20, t=30, b=20))
                        st.plotly_chart(fig_asis, width="stretch")

        with sub_calendario:
            st.subheader("📅 Calendario Académico")
            c_mes1, c_mes2, c_asig_filtro = st.columns([1, 1, 2])
            hoy = date.today()
            with c_mes1:
                mes_sel = st.selectbox("Mes", list(range(1, 13)), index=hoy.month - 1, format_func=lambda x: calendar.month_name[x].capitalize())
            with c_mes2:
                ano_sel = st.number_input("Año", min_value=2020, max_value=2035, value=hoy.year)
            with c_asig_filtro:
                filtro_asig_cal = st.selectbox("Filtrar", ["Todas las asignaturas"] + list(mapa_asignaturas.keys()))

            cal = calendar.monthcalendar(ano_sel, mes_sel)
            dias_semana = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
            id_filtro = mapa_asignaturas.get(filtro_asig_cal) if filtro_asig_cal != "Todas las asignaturas" else None

            eventos_por_dia = {d: {"asistencias": 0, "examenes": [], "entregas": []} for d in range(1, 32)}

            if not df_asistencia.empty:
                sub_asis = df_asistencia[df_asistencia["id_asignatura"] == id_filtro] if id_filtro else df_asistencia
                for _, row in sub_asis.iterrows():
                    if pd.notnull(row["fecha"]) and row["fecha"].year == ano_sel and row["fecha"].month == mes_sel:
                        eventos_por_dia[row["fecha"].day]["asistencias"] += 1

            if not df_notas.empty:
                sub_not = df_notas[df_notas["id_asignatura"] == id_filtro] if id_filtro else df_notas
                for _, row in sub_not.iterrows():
                    if pd.notnull(row["fecha"]) and row["fecha"].year == ano_sel and row["fecha"].month == mes_sel:
                        d = row["fecha"].day
                        eventos_por_dia[d]["examenes"].append({
                            "asig": mapa_nombres_rev.get(str(row["id_asignatura"]), "Asig"),
                            "tipo_estado": "Planificado" if row.get("estado") == "Pendiente" else "Evaluado",
                            "tipo_clase": row.get("tipo", "Teoría")
                        })
                        
            if not df_entregas.empty:
                sub_ent = df_entregas[df_entregas["id_asignatura"] == id_filtro] if id_filtro else df_entregas
                for _, row in sub_ent.iterrows():
                    if pd.notnull(row["fecha_limite"]) and row["fecha_limite"].year == ano_sel and row["fecha_limite"].month == mes_sel:
                        d = row["fecha_limite"].day
                        eventos_por_dia[d]["entregas"].append({
                            "asig": mapa_nombres_rev.get(str(row["id_asignatura"]), "Asig"),
                            "completada": row["completada"]
                        })

            st.markdown("---")
            cols_dias = st.columns(7)
            for i, nom_dia in enumerate(dias_semana):
                cols_dias[i].markdown(f"<p style='text-align:center; font-size:13px; color:#6B7280; border-bottom: 1px solid #E5E7EB; padding-bottom:5px;'>{nom_dia}</p>", unsafe_allow_html=True)

            for semana in cal:
                cols_sem = st.columns(7)
                for i, dia in enumerate(semana):
                    with cols_sem[i]:
                        if dia == 0:
                            st.markdown("<div style='height:80px; margin:2px;'></div>", unsafe_allow_html=True)
                        else:
                            es_hoy = (dia == hoy.day and mes_sel == hoy.month and ano_sel == hoy.year)
                            borde = "border: 1px solid #374151;" if es_hoy else "border: 1px solid transparent; border-top: 1px solid #F3F4F6;"
                            fuente_dia = "font-weight:bold; color:#111827;" if es_hoy else "color:#4B5563;"
                            html_eventos = ""
                            
                            for ex in eventos_por_dia[dia]["examenes"]:
                                txt_ex = f"{ex['asig'][:12]}.." if len(ex['asig']) > 12 else ex['asig']
                                icono_lab = "🧪" if ex.get("tipo_clase") == "Laboratorio" else ""
                                if ex['tipo_estado'] == "Planificado":
                                    html_eventos += f"<div style='font-size:10px; color: var(--text-color); opacity: 0.7; margin-top:2px;'>◦ {txt_ex} (P) {icono_lab}</div>"
                                else:
                                    html_eventos += f"<div style='font-size:10px; color: var(--text-color); margin-top:2px; font-weight:600;'>• {txt_ex} {icono_lab}</div>"
                            
                            for ent in eventos_por_dia[dia]["entregas"]:
                                txt_ent = f"{ent['asig'][:12]}.." if len(ent['asig']) > 12 else ent['asig']
                                if ent['completada'] == 1:
                                    html_eventos += f"<div style='font-size:10px; color: var(--text-color); opacity: 0.4; margin-top:2px; text-decoration: line-through;'>✅ {txt_ent}</div>"
                                else:
                                    html_eventos += f"<div style='font-size:10px; color: var(--text-color); font-weight:600; margin-top:2px;'>📌 {txt_ent}</div>"
                            
                            num_asis = eventos_por_dia[dia]["asistencias"]
                            if num_asis > 0:
                                html_eventos += f"<div style='font-size:10px; color:#9CA3AF; margin-top:6px;'>{num_asis} clase(s)</div>"
                            
                            st.markdown(f"<div style='{borde} min-height:80px; padding:4px 6px; margin:2px;'><div style='font-size:13px; {fuente_dia}'>{dia}</div>{html_eventos}</div>", unsafe_allow_html=True)

            st.markdown("<br><b>Detalle de días con actividad</b>", unsafe_allow_html=True)
            hay_eventos = False
            for d in range(1, 32):
                if eventos_por_dia[d]["asistencias"] > 0 or eventos_por_dia[d]["examenes"] or eventos_por_dia[d]["entregas"]:
                    hay_eventos = True
                    detalle = []
                    
                    if not df_entregas.empty:
                        sub = df_entregas[(df_entregas["fecha_limite"].dt.day == d) & (df_entregas["fecha_limite"].dt.month == mes_sel) & (df_entregas["fecha_limite"].dt.year == ano_sel)]
                        if id_filtro: sub = sub[sub["id_asignatura"] == id_filtro]
                        for _, r in sub.iterrows():
                            est = "Completada" if r["completada"] == 1 else "Pendiente"
                            detalle.append(f"📌 Entrega: {mapa_nombres_rev.get(str(r['id_asignatura']))} - {r['descripcion']} ({est})")
                            
                    if not df_notas.empty:
                        sub = df_notas[(df_notas["fecha"].dt.day == d) & (df_notas["fecha"].dt.month == mes_sel) & (df_notas["fecha"].dt.year == ano_sel)]
                        if id_filtro: sub = sub[sub["id_asignatura"] == id_filtro]
                        for _, r in sub.iterrows():
                            est = "Planificado" if r.get("estado") == "Pendiente" else f"Nota: {r.get('nota')} (Mín: {r.get('nota_minima', 0)})"
                            icono = "🧪" if r.get("tipo") == "Laboratorio" else ""
                            detalle.append(f"📝 Examen: {mapa_nombres_rev.get(str(r['id_asignatura']))} {icono} - {r['concepto']} ({est})")
                            
                    if not df_asistencia.empty:
                        sub = df_asistencia[(df_asistencia["fecha"].dt.day == d) & (df_asistencia["fecha"].dt.month == mes_sel) & (df_asistencia["fecha"].dt.year == ano_sel)]
                        if id_filtro: sub = sub[sub["id_asignatura"] == id_filtro]
                        for _, r in sub.iterrows():
                            icono = "🧪" if r.get("tipo") == "Laboratorio" else ""
                            detalle.append(f"🏫 Clase: {mapa_nombres_rev.get(str(r['id_asignatura']))} {icono} ({r['estado']})")

                    with st.expander(f"Día {d}"):
                        for item in detalle:
                            st.write(item)
                            
            if not hay_eventos:
                st.caption("No hay actividad en el mes seleccionado.")

# ==============================================================================
# TAB 2: HORARIO
# ==============================================================================
with tab_horario:
    st.subheader("🗓️ Horario de Clases (Asignaturas Activas)")
    
    if not df_horario.empty:
        if 'tipo' not in df_horario.columns:
            df_horario['tipo'] = 'Teoría'
        df_horario['tipo'] = df_horario['tipo'].fillna('Teoría')
        
        if 'frecuencia' not in df_horario.columns:
            df_horario['frecuencia'] = 'Todas'
        df_horario['frecuencia'] = df_horario['frecuencia'].fillna('Todas')
        
    if not mapa_activas:
        st.info("No tienes asignaturas 'En curso'.")
    else:
        with st.expander("➕ Añadir clase al horario"):
            with st.form("form_horario", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1: 
                    h_asig = st.selectbox("Asignatura", list(mapa_activas.keys()))
                    h_dia = st.selectbox("Día", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"])
                    h_tipo = st.radio("Tipo de clase", ["Teoría", "Laboratorio"], horizontal=True)
                with c2: 
                    c_h1, c_h2 = st.columns(2)
                    with c_h1: h_ini = st.time_input("Hora Inicio", value=pd.to_datetime("09:00").time())
                    with c_h2: h_fin = st.time_input("Hora Fin", value=pd.to_datetime("11:00").time())
                    h_frec = st.selectbox("Frecuencia", ["Todas las semanas", "Semanas pares", "Semanas impares"])
                
                if st.form_submit_button("Añadir al horario", width="stretch"):
                    frec_db = "Todas" if h_frec == "Todas las semanas" else ("Pares" if h_frec == "Semanas pares" else "Impares")
                    db.add_horario(mapa_activas[h_asig], h_dia, h_ini.strftime("%H:%M"), h_fin.strftime("%H:%M"), h_tipo, frec_db)
                    st.rerun()
                    
        with st.expander("✏️ Editar o Eliminar clase existente"):
            if df_horario.empty:
                st.info("El horario está vacío.")
            else:
                df_h_act = df_horario[df_horario['id_asignatura'].isin(list(mapa_activas.values()))]
                if df_h_act.empty:
                    st.info("No hay clases editables en asignaturas actualmente activas.")
                else:
                    opciones_h = {}
                    for _, r in df_h_act.iterrows():
                        n_asig = mapa_nombres_rev.get(str(r['id_asignatura']), "Asig")
                        frec_txt = "" if r['frecuencia'] == "Todas" else f" ({r['frecuencia']})"
                        etiq = f"{n_asig} | {r['dia_semana']} ({r['hora_inicio']} - {r['hora_fin']}){frec_txt}"
                        opciones_h[etiq] = str(r['id_horario'])
                    
                    sel_h = st.selectbox("Clase a modificar", list(opciones_h.keys()))
                    if sel_h:
                        id_h = opciones_h[sel_h]
                        r_h = df_h_act[df_h_act['id_horario'] == id_h].iloc[0]
                        
                        idx_tipo_h = 1 if r_h.get('tipo') == "Laboratorio" else 0
                        frec_val = r_h.get('frecuencia', 'Todas')
                        idx_frec_h = 0
                        if frec_val == "Pares": idx_frec_h = 1
                        elif frec_val == "Impares": idx_frec_h = 2
                        
                        with st.form("form_edit_horario"):
                            c1, c2 = st.columns(2)
                            dias_validos = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
                            idx_dia = dias_validos.index(r_h['dia_semana']) if r_h['dia_semana'] in dias_validos else 0
                            
                            with c1: 
                                e_dia = st.selectbox("Día", dias_validos, index=idx_dia)
                                e_tipo = st.radio("Tipo de clase", ["Teoría", "Laboratorio"], index=idx_tipo_h, horizontal=True)
                            with c2: 
                                c_e1, c_e2 = st.columns(2)
                                with c_e1: e_ini = st.time_input("Hora Inicio", value=pd.to_datetime(r_h['hora_inicio']).time())
                                with c_e2: e_fin = st.time_input("Hora Fin", value=pd.to_datetime(r_h['hora_fin']).time())
                                e_frec = st.selectbox("Frecuencia", ["Todas las semanas", "Semanas pares", "Semanas impares"], index=idx_frec_h)
                            
                            c_btn1, c_btn2 = st.columns(2)
                            with c_btn1:
                                if st.form_submit_button("💾 Guardar Cambios", type="primary", use_container_width=True):
                                    frec_db = "Todas" if e_frec == "Todas las semanas" else ("Pares" if e_frec == "Semanas pares" else "Impares")
                                    db.edit_horario(id_h, e_dia, e_ini.strftime("%H:%M"), e_fin.strftime("%H:%M"), e_tipo, frec_db)
                                    st.rerun()
                            with c_btn2:
                                if st.form_submit_button("🗑️ Eliminar Clase", use_container_width=True):
                                    db.delete_horario(id_h)
                                    st.rerun()

        st.divider()
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        cols = st.columns(5)
        for i, dia in enumerate(dias_semana):
            with cols[i]:
                st.markdown(f"<p style='text-align:center; font-size:13px; color:#6B7280; border-bottom: 1px solid #E5E7EB; padding-bottom:5px;'>{dia}</p>", unsafe_allow_html=True)
                if not df_horario.empty and "dia_semana" in df_horario.columns:
                    for _, clase in df_horario[df_horario["dia_semana"] == dia].sort_values("hora_inicio").iterrows():
                        id_asig = str(clase["id_asignatura"])
                        nom = mapa_nombres_rev.get(id_asig, id_asig)
                        
                        tipo_str = "🧪" if clase.get('tipo') == "Laboratorio" else "📖"
                        frec_val = clase.get('frecuencia', 'Todas')
                        frec_str = ""
                        if frec_val == "Pares": frec_str = " *(Pares)*"
                        elif frec_val == "Impares": frec_str = " *(Impares)*"
                        
                        st.markdown(f"<div style='border-left: 2px solid #9CA3AF; padding-left: 8px; margin-bottom: 14px;'><div style='font-size:10px; color:var(--text-color); opacity:0.6;'>{clase['hora_inicio']} - {clase['hora_fin']}{frec_str}</div><div style='font-size:11px; font-weight:600; color:var(--text-color); margin-top:2px;'>{tipo_str} {nom}</div></div>", unsafe_allow_html=True)

# ==============================================================================
# TAB 3: ASISTENCIA
# ==============================================================================
with tab_asis:
    st.subheader("Marcar Asistencia")
    if mapa_activas:
        with st.form("form_asis", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                asig_sel = st.selectbox("Asignatura", list(mapa_activas.keys()))
                estado = st.radio("Estado", ["Presente", "Falta", "Justificada", "Retraso"], horizontal=True)
                tipo_clase = st.radio("Tipo", ["Teoría", "Laboratorio"], horizontal=True)
            with c2:
                fecha = st.date_input("Fecha", value=datetime.now())
                obs = st.text_input("Observaciones")
            if st.form_submit_button("Guardar", width="stretch"):
                db.add_asistencia(mapa_activas[asig_sel], estado, obs, str(fecha), tipo_clase)
                st.rerun()

        with st.expander("✏️ Editar o Eliminar registro existente"):
            if df_asistencia.empty:
                st.info("No hay asistencias registradas.")
            else:
                df_a_act = df_asistencia[df_asistencia['id_asignatura'].isin(list(mapa_activas.values()))]
                if df_a_act.empty:
                    st.info("No hay registros editables en asignaturas actualmente activas.")
                else:
                    opciones_a = {}
                    for _, r in df_a_act.iterrows():
                        n_asig = mapa_nombres_rev.get(str(r['id_asignatura']), "Asig")
                        fecha_str = r['fecha'].strftime("%Y-%m-%d") if pd.notnull(r['fecha']) else ""
                        etiq = f"{fecha_str} | {n_asig} | {r['estado']} ({r['tipo']})"
                        opciones_a[etiq] = str(r['id_registro'])
                    
                    sel_a = st.selectbox("Registro a modificar", list(opciones_a.keys()))
                    if sel_a:
                        id_a = opciones_a[sel_a]
                        r_a = df_a_act[df_a_act['id_registro'] == id_a].iloc[0]
                        with st.form("form_edit_asis"):
                            c1, c2 = st.columns(2)
                            estados_validos = ["Presente", "Falta", "Justificada", "Retraso"]
                            idx_est = estados_validos.index(r_a['estado']) if r_a['estado'] in estados_validos else 0
                            idx_tipo = 1 if r_a['tipo'] == "Laboratorio" else 0
                            try: def_date = pd.to_datetime(r_a['fecha']).date()
                            except: def_date = datetime.now().date()
                            
                            with c1:
                                e_est = st.radio("Estado", estados_validos, index=idx_est, horizontal=True)
                                e_tipo = st.radio("Tipo", ["Teoría", "Laboratorio"], index=idx_tipo, horizontal=True)
                            with c2:
                                e_fec = st.date_input("Fecha", value=def_date)
                                e_obs = st.text_input("Observaciones", value=str(r_a.get('observaciones', '')))
                                
                            c_btn1, c_btn2 = st.columns(2)
                            with c_btn1:
                                if st.form_submit_button("💾 Guardar Cambios", type="primary", use_container_width=True):
                                    db.edit_asistencia(id_a, e_est, e_obs, str(e_fec), e_tipo)
                                    st.rerun()
                            with c_btn2:
                                if st.form_submit_button("🗑️ Eliminar Registro", use_container_width=True):
                                    db.delete_asistencia(id_a)
                                    st.rerun()

# ==============================================================================
# TAB 4: CALIFICACIONES Y SIMULADOR
# ==============================================================================
with tab_eval:
    st.subheader("Gestión de Evaluaciones y Exámenes")
    if not mapa_activas:
        st.warning("⚠️ No tienes asignaturas activas.")
    else:
        modo_eval = st.radio(
            "¿Qué deseas hacer?", 
            ["📝 Registrar examen", "📅 Planificar futuro", "✅ Poner nota a pendiente", "⚙️ Reglas Especiales"], 
            horizontal=True
        )
        st.divider()

        if modo_eval == "📝 Registrar examen":
            with st.form("form_nota", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    asig_nota = st.selectbox("Asignatura", list(mapa_activas.keys()))
                    concepto = st.text_input("Concepto (ej. Parcial 1)")
                    tipo_eval = st.radio("Tipo", ["Teoría", "Laboratorio"], horizontal=True, key="t1")
                with col2:
                    c_n1, c_n2, c_n3 = st.columns(3)
                    with c_n1:
                        ponderacion = st.number_input("Peso (%)", min_value=1.0, max_value=100.0, step=5.0, value=30.0)
                    with c_n2:
                        nota = st.number_input("Nota", min_value=0.0, max_value=10.0, step=0.1, value=7.0)
                    with c_n3:
                        nota_minima = st.number_input("Mínima", min_value=0.0, max_value=10.0, step=0.1, value=0.0)
                    fecha_eval = st.date_input("Fecha", value=datetime.now())
                if st.form_submit_button("Guardar Calificación", width="stretch"):
                    if not concepto.strip():
                        st.error("Introduce un concepto.")
                    else:
                        db.add_calificacion(mapa_activas[asig_nota], concepto, ponderacion, nota, str(fecha_eval), "Realizado", tipo_eval, nota_minima)
                        st.rerun()

        elif modo_eval == "📅 Planificar futuro":
            with st.form("form_plan", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    asig_plan = st.selectbox("Asignatura", list(mapa_activas.keys()))
                    concepto = st.text_input("Concepto (ej. Examen Final)")
                    tipo_eval = st.radio("Tipo", ["Teoría", "Laboratorio"], horizontal=True, key="t2")
                with col2:
                    c_p1, c_p2 = st.columns(2)
                    with c_p1:
                        ponderacion = st.number_input("Peso (%)", min_value=1.0, max_value=100.0, step=5.0, value=40.0)
                    with c_p2:
                        nota_minima = st.number_input("Nota Mínima", min_value=0.0, max_value=10.0, step=0.1, value=5.0)
                    fecha_plan = st.date_input("Fecha del examen", value=datetime.now())
                if st.form_submit_button("Planificar en el Calendario", width="stretch"):
                    if not concepto.strip():
                        st.error("Introduce un concepto.")
                    else:
                        db.add_calificacion(mapa_activas[asig_plan], concepto, ponderacion, None, str(fecha_plan), "Pendiente", tipo_eval, nota_minima)
                        st.rerun()

        elif modo_eval == "✅ Poner nota a pendiente":
            df_pendientes = df_notas[df_notas["estado"] == "Pendiente"] if not df_notas.empty else pd.DataFrame()
            if df_pendientes.empty:
                st.info("🎉 No tienes exámenes pendientes de calificar.")
            else:
                opciones_pendientes = {}
                for _, row in df_pendientes.iterrows():
                    asig_nom = mapa_nombres_rev.get(str(row["id_asignatura"]))
                    fecha_str = row["fecha"].strftime("%Y-%m-%d") if pd.notnull(row["fecha"]) else ""
                    etiq = f"⏳ {fecha_str} | {asig_nom} - {row['concepto']}"
                    opciones_pendientes[etiq] = str(row["id_evaluacion"])
                
                with st.form("form_update", clear_on_submit=True):
                    eval_sel = st.selectbox("Selecciona el examen realizado", list(opciones_pendientes.keys()))
                    nueva_nota = st.number_input("Nota obtenida (0 - 10)", min_value=0.0, max_value=10.0, step=0.1, value=5.0)
                    if st.form_submit_button("Guardar Nota Definitiva", width="stretch"):
                        db.update_calificacion(opciones_pendientes[eval_sel], nueva_nota)
                        st.rerun()

        elif modo_eval == "⚙️ Reglas Especiales":
            c_form, c_lista = st.columns([1.2, 1])
            with c_form:
                with st.form("form_regla", clear_on_submit=True):
                    asig_regla = st.selectbox("1. Asignatura", list(mapa_activas.keys()))
                    id_asig_reg = mapa_activas[asig_regla]
                    evals = df_notas[df_notas["id_asignatura"] == id_asig_reg] if not df_notas.empty else pd.DataFrame()
                    if evals.empty:
                        st.warning("No hay exámenes creados.")
                        ids_seleccionados = ""
                    else:
                        opciones_ev = {f"{r['concepto']}": str(r['id_evaluacion']) for _, r in evals.iterrows()}
                        seleccion = st.multiselect("2. Exámenes que forman esta regla", list(opciones_ev.keys()))
                        ids_seleccionados = ",".join([opciones_ev[k] for k in seleccion])
                    
                    c_r1, c_r2 = st.columns(2)
                    with c_r1: desc_regla = st.text_input("3. Nombre de la regla", value="Media de parciales")
                    with c_r2: val_regla = st.number_input("4. Media mínima exigida", min_value=0.0, max_value=10.0, step=0.1, value=4.0)
                        
                    if st.form_submit_button("Guardar Regla", width="stretch"):
                        if not ids_seleccionados:
                            st.error("Debes seleccionar al menos un examen.")
                        else:
                            db.add_regla(id_asig_reg, desc_regla, "Media Mínima", ids_seleccionados, val_regla)
                            st.rerun()
            with c_lista:
                if not df_reglas.empty:
                    for _, regla in df_reglas.iterrows():
                        asig_n = mapa_nombres_rev.get(str(regla["id_asignatura"]), "Asig")
                        with st.expander(f"⚖️ {asig_n} - {regla['descripcion']} (Mín: {regla['valor_exigido']})"):
                            ids_impl = str(regla["ids_evaluaciones"]).split(",")
                            nombres_impl = []
                            for i in ids_impl:
                                sub = df_notas[df_notas["id_evaluacion"] == i] if not df_notas.empty else pd.DataFrame()
                                if not sub.empty: nombres_impl.append(str(sub.iloc[0]["concepto"]))
                            st.write("Aplica a:", ", ".join(nombres_impl))
                            if st.button("🗑️ Eliminar", key=f"del_r_{regla['id_regla']}"):
                                db.delete_regla(regla["id_regla"])
                                st.rerun()

        st.divider()
        with st.expander("✏️ Editar o Eliminar evaluación individual"):
            if df_notas.empty:
                st.info("No hay calificaciones registradas.")
            else:
                df_c_act = df_notas[df_notas['id_asignatura'].isin(list(mapa_activas.values()))]
                if df_c_act.empty:
                    st.info("No hay evaluaciones editables en asignaturas activas.")
                else:
                    opciones_c = {}
                    for _, r in df_c_act.iterrows():
                        n_asig = mapa_nombres_rev.get(str(r['id_asignatura']), "Asig")
                        est = f"Nota: {r['nota']}" if r['estado'] == "Realizado" else "Pendiente"
                        etiq = f"{n_asig} | {r['concepto']} | {est}"
                        opciones_c[etiq] = str(r['id_evaluacion'])
                    
                    sel_c = st.selectbox("Evaluación a modificar", list(opciones_c.keys()))
                    if sel_c:
                        id_c = opciones_c[sel_c]
                        r_c = df_c_act[df_c_act['id_evaluacion'] == id_c].iloc[0]
                        with st.form("form_edit_calif"):
                            e_con = st.text_input("Concepto", value=str(r_c['concepto']))
                            c1, c2, c3, c4 = st.columns(4)
                            idx_tipo_c = 1 if r_c['tipo'] == "Laboratorio" else 0
                            try: def_date_c = pd.to_datetime(r_c['fecha']).date()
                            except: def_date_c = datetime.now().date()
                            
                            with c1: e_tipo = st.radio("Tipo", ["Teoría", "Laboratorio"], index=idx_tipo_c, horizontal=True)
                            with c2: e_pond = st.number_input("Peso (%)", min_value=1.0, max_value=100.0, value=float(r_c['ponderacion_pct']))
                            with c3: e_min = st.number_input("Nota Mínima", min_value=0.0, max_value=10.0, value=float(r_c['nota_minima']))
                            with c4: e_fec = st.date_input("Fecha", value=def_date_c)
                            
                            if r_c['estado'] == "Realizado":
                                e_nota = st.number_input("Nota Obtenida", min_value=0.0, max_value=10.0, value=float(r_c['nota']) if pd.notnull(r_c['nota']) else 0.0)
                            else:
                                e_nota = None
                                st.caption("*(Nota pendiente)*")
                                
                            c_btn1, c_btn2 = st.columns(2)
                            with c_btn1:
                                if st.form_submit_button("💾 Guardar Cambios", type="primary", use_container_width=True):
                                    db.edit_calificacion(id_c, e_con, e_pond, e_nota, str(e_fec), e_tipo, e_min)
                                    st.rerun()
                            with c_btn2:
                                if st.form_submit_button("🗑️ Eliminar Evaluación", use_container_width=True):
                                    db.delete_calificacion(id_c)
                                    st.rerun()

        st.divider()
        st.subheader("🧮 Simulador de Notas (Previsión Múltiple)")
        st.write("Juega con las notas de tus próximos exámenes para ver tu calificación proyectada, o calcula cuánto necesitas en uno en concreto.")
        
        asig_sim = st.selectbox("Selecciona la asignatura a simular", list(mapa_activas.keys()), key="sim_asig")
        id_sim = mapa_activas[asig_sim]
        
        df_sim_realizados = df_notas[(df_notas["id_asignatura"] == id_sim) & (df_notas["estado"] == "Realizado")] if not df_notas.empty else pd.DataFrame()
        df_sim_pendientes = df_notas[(df_notas["id_asignatura"] == id_sim) & (df_notas["estado"] == "Pendiente")] if not df_notas.empty else pd.DataFrame()
        
        bloqueo_minimo_historial = False
        lista_bloqueos = []
        peso_evaluado = 0.0
        nota_acumulada = 0.0
        peso_planificado = 0.0
        
        if not df_sim_realizados.empty:
            peso_evaluado = df_sim_realizados["ponderacion_pct"].sum()
            nota_acumulada = (df_sim_realizados["nota"] * (df_sim_realizados["ponderacion_pct"] / 100.0)).sum()
            
            for _, eval_row in df_sim_realizados.iterrows():
                n_min = float(eval_row.get("nota_minima", 0.0))
                n_obtenida = float(eval_row.get("nota", 0.0))
                if n_min > 0 and n_obtenida < n_min:
                    bloqueo_minimo_historial = True
                    lista_bloqueos.append(f"**{eval_row['concepto']}** (Nota: {n_obtenida} | Mín: {n_min})")
                    
        if not df_sim_pendientes.empty:
            peso_planificado = df_sim_pendientes["ponderacion_pct"].sum()
        
        if not df_reglas.empty:
            reglas_asig = df_reglas[df_reglas["id_asignatura"] == id_sim]
            for _, regla in reglas_asig.iterrows():
                ids_regla = str(regla["ids_evaluaciones"]).split(",")
                notas_implicadas = df_sim_realizados[df_sim_realizados["id_evaluacion"].isin(ids_regla)]
                if len(notas_implicadas) == len(ids_regla) and len(ids_regla) > 0:
                    media_regla = notas_implicadas["nota"].mean()
                    if media_regla < float(regla["valor_exigido"]):
                        bloqueo_minimo_historial = True
                        lista_bloqueos.append(f"Regla **{regla['descripcion']}** incumplida (Media: {round(media_regla,2)} | Mín: {regla['valor_exigido']})")
        
        peso_no_planificado = max(0.0, 100.0 - peso_evaluado - peso_planificado)
        
        col_s1, col_s2, col_s3 = st.columns(3)
        col_s1.metric("✅ Peso Evaluado", f"{peso_evaluado}%")
        col_s2.metric("⭐ Nota Acumulada", f"{round(nota_acumulada, 2)} ptos / 10")
        col_s3.metric("⏳ Falta por evaluar", f"{round(100.0 - peso_evaluado, 2)}%")
        
        if bloqueo_minimo_historial:
            st.error("🛑 **ASIGNATURA BLOQUEADA POR GUÍA DOCENTE**\n\nTienes evaluaciones ya realizadas que no superan los mínimos exigidos:\n\n" + 
                     "\n".join([f"- {ex}" for ex in lista_bloqueos]) + 
                     "\n\n*Matemáticamente podrías sumar puntos, pero suspenderás si no recuperas antes estas partes.*")
                     
        st.markdown("#### 1. Rellena tus previsiones")
        st.caption("Introduce las notas que esperas sacar en lo que te queda por evaluar para ver tu nota final proyectada.")
        
        notas_hipoteticas = {}
        cols_inputs = st.columns(3)
        idx_col = 0
        
        for _, row_pend in df_sim_pendientes.iterrows():
            with cols_inputs[idx_col % 3]:
                concepto = row_pend['concepto']
                peso = float(row_pend['ponderacion_pct'])
                n_min = float(row_pend.get('nota_minima', 0.0))
                lbl = f"📝 {concepto} ({peso}%)" + (f" [Mín: {n_min}]" if n_min > 0 else "")
                val = st.number_input(lbl, min_value=0.0, max_value=10.0, value=5.0, step=0.1, key=f"sim_{row_pend['id_evaluacion']}")
                notas_hipoteticas[row_pend['id_evaluacion']] = {'peso': peso, 'nota': val, 'min': n_min, 'concepto': concepto}
            idx_col += 1
            
        if peso_no_planificado > 0:
            with cols_inputs[idx_col % 3]:
                val = st.number_input(f"❓ Resto sin planificar ({round(peso_no_planificado, 2)}%)", min_value=0.0, max_value=10.0, value=5.0, step=0.1, key="sim_resto")
                notas_hipoteticas['resto'] = {'peso': peso_no_planificado, 'nota': val, 'min': 0.0, 'concepto': "Resto sin planificar"}
                
        if len(notas_hipoteticas) == 0:
            st.info("No te falta ningún porcentaje por evaluar en esta asignatura. Ya has completado el 100%.")
        else:
            puntos_hipoteticos = sum(item['nota'] * (item['peso'] / 100.0) for item in notas_hipoteticas.values())
            nota_final_proyectada = nota_acumulada + puntos_hipoteticos
            
            bloqueo_hipotetico = False
            mensajes_bloqueo = []
            for item in notas_hipoteticas.values():
                if item['min'] > 0 and item['nota'] < item['min']:
                    bloqueo_hipotetico = True
                    mensajes_bloqueo.append(f"{item['concepto']} (Simulado: {item['nota']} < Mín: {item['min']})")
            
            st.markdown(f"### 🎯 Nota Final Proyectada: **{round(nota_final_proyectada, 2)}**")
            
            if bloqueo_minimo_historial:
                pass 
            elif bloqueo_hipotetico:
                st.warning("⚠️ **Cuidado:** Aunque la suma de puntos dé tu objetivo, con estas previsiones suspenderías por no llegar a los mínimos en:\n\n" + "\n".join(f"- {m}" for m in mensajes_bloqueo))
            elif nota_final_proyectada >= 5.0:
                st.success("🎉 ¡Con estas notas aprobarías la asignatura!")
            else:
                st.error("❌ Con estas notas no te da para aprobar la asignatura (necesitas un 5.0 final).")
                
            st.markdown("---")
            st.markdown("#### 2. Calculadora: ¿Cuánto necesito exactamente?")
            st.write("Elige una de las evaluaciones de arriba. Te diremos qué nota necesitas *exactamente* en ella para aprobar, asumiendo que sacas las notas indicadas en el resto.")
            
            c_rev1, c_rev2 = st.columns(2)
            with c_rev1:
                opciones_rev = {item['concepto']: k for k, item in notas_hipoteticas.items()}
                target_key = st.selectbox("Quiero saber qué nota necesito en...", list(opciones_rev.keys()))
            with c_rev2:
                nota_obj = st.number_input("Para conseguir una nota final de:", min_value=5.0, max_value=10.0, value=5.0, step=0.1)
                
            if target_key:
                id_target = opciones_rev[target_key]
                peso_target = notas_hipoteticas[id_target]['peso']
                n_min_target = notas_hipoteticas[id_target]['min']
                
                puntos_otros_hip = sum(item['nota'] * (item['peso']/100.0) for k, item in notas_hipoteticas.items() if k != id_target)
                puntos_base = nota_acumulada + puntos_otros_hip
                
                nota_necesaria = (nota_obj - puntos_base) / (peso_target / 100.0)
                
                if nota_necesaria > 10:
                    st.error(f"❌ **Matemáticamente imposible.** Necesitarías sacar un **{round(nota_necesaria, 2)}** en '{target_key}' para llegar a un {nota_obj} final.")
                elif nota_necesaria <= 0:
                    st.success(f"🎉 **¡Ya lo tienes asegurado!** Incluso sacando un **0** en '{target_key}' alcanzas tu objetivo.")
                    if n_min_target > 0:
                        st.warning(f"⚠️ ¡Ojo! Como ese examen exige un mínimo de **{n_min_target}**, tendrás que sacar al menos esa nota para no suspender directamente.")
                else:
                    if nota_necesaria < n_min_target:
                        st.warning(f"⚠️ Por puntos solo necesitarías un **{round(nota_necesaria, 2)}** en '{target_key}', pero **exige una nota mínima de {n_min_target}** para hacer media. Debes sacar el mínimo.")
                    else:
                        st.info(f"🎯 Necesitas sacar al menos un **{round(nota_necesaria, 2)}** en '{target_key}' para llegar a tu objetivo de {nota_obj} final.")

# ==============================================================================
# TAB 5: ENTREGAS
# ==============================================================================
with tab_entregas:
    st.subheader("📌 Gestor de Entregas y Tareas")
    if not mapa_activas:
        st.warning("⚠️ No tienes asignaturas activas.")
    else:
        col_form, col_lista = st.columns([1, 1.5])
        with col_form:
            st.markdown("#### Nueva Entrega")
            with st.form("form_entrega", clear_on_submit=True):
                asig_ent = st.selectbox("Asignatura", list(mapa_activas.keys()))
                desc_ent = st.text_input("Descripción (ej. Ejercicios Tema 4)")
                fecha_ent = st.date_input("Fecha Límite")
                cuenta_nota = st.checkbox("¿Cuenta para la nota final?")
                peso_ent = st.number_input("Ponderación (%)", min_value=1.0, max_value=100.0, value=10.0, disabled=not cuenta_nota)

                if st.form_submit_button("Guardar Tarea", width="stretch"):
                    if not desc_ent.strip():
                        st.error("Añade una descripción.")
                    else:
                        pond_final = float(peso_ent) if cuenta_nota else None
                        db.add_entrega(mapa_activas[asig_ent], desc_ent, str(fecha_ent), pond_final)
                        st.rerun()

        with col_lista:
            st.markdown("#### Tareas Pendientes")
            if df_entregas.empty:
                st.info("No hay tareas registradas. ¡Todo al día! 🎉")
            else:
                pendientes = df_entregas[df_entregas["completada"] == 0].sort_values("fecha_limite")
                completadas = df_entregas[df_entregas["completada"] == 1].sort_values("fecha_limite", ascending=False)

                if pendientes.empty:
                    st.success("¡No tienes tareas pendientes!")
                else:
                    for _, row in pendientes.iterrows():
                        asig_nom = mapa_nombres_rev.get(str(row["id_asignatura"]), "Asig")
                        peso_txt = f"*(Cuenta: {row['ponderacion']}%)*" if pd.notnull(row["ponderacion"]) else "*(Sin evaluar)*"
                        fecha_txt = row["fecha_limite"].strftime("%d %b") if pd.notnull(row["fecha_limite"]) else ""
                        c1, c2 = st.columns([1, 10])
                        with c1:
                            if st.button("⬜", key=f"btn_p_{row['id_entrega']}", help="Marcar como completada"):
                                db.toggle_entrega(row['id_entrega'], 1)
                                st.rerun()
                        with c2:
                            st.markdown(f"**{asig_nom}**: {row['descripcion']} - 📅 {fecha_txt}  {peso_txt}")
                
                if not completadas.empty:
                    with st.expander(f"✅ Tareas Completadas ({len(completadas)})"):
                        for _, row in completadas.iterrows():
                            asig_nom = mapa_nombres_rev.get(str(row["id_asignatura"]), "Asig")
                            c1, c2 = st.columns([1, 10])
                            with c1:
                                if st.button("✅", key=f"btn_c_{row['id_entrega']}", help="Marcar como pendiente"):
                                    db.toggle_entrega(row['id_entrega'], 0)
                                    st.rerun()
                            with c2:
                                st.markdown(f"~~{asig_nom}: {row['descripcion']}~~")
                        
        st.divider()
        with st.expander("✏️ Editar o Eliminar entrega existente"):
            if df_entregas.empty:
                st.info("No hay entregas registradas.")
            else:
                df_e_act = df_entregas[df_entregas['id_asignatura'].isin(list(mapa_activas.values()))]
                if df_e_act.empty:
                    st.info("No hay entregas editables en asignaturas actualmente activas.")
                else:
                    opciones_e = {}
                    for _, r in df_e_act.iterrows():
                        n_asig = mapa_nombres_rev.get(str(r['id_asignatura']), "Asig")
                        est_txt = "✅" if r['completada'] == 1 else "⬜"
                        etiq = f"{est_txt} {n_asig} | {r['descripcion']}"
                        opciones_e[etiq] = str(r['id_entrega'])
                    
                    sel_e = st.selectbox("Entrega a modificar", list(opciones_e.keys()))
                    if sel_e:
                        id_e = opciones_e[sel_e]
                        r_e = df_e_act[df_e_act['id_entrega'] == id_e].iloc[0]
                        with st.form("form_edit_ent"):
                            e_desc = st.text_input("Descripción", value=str(r_e['descripcion']))
                            c1, c2 = st.columns(2)
                            try: def_date_e = pd.to_datetime(r_e['fecha_limite']).date()
                            except: def_date_e = datetime.now().date()
                            
                            with c1: e_fec = st.date_input("Fecha Límite", value=def_date_e)
                            with c2:
                                tenia_pond = pd.notnull(r_e['ponderacion'])
                                e_cuenta = st.checkbox("¿Cuenta para nota?", value=tenia_pond)
                                e_pond = st.number_input("Ponderación (%)", min_value=1.0, max_value=100.0, value=float(r_e['ponderacion']) if tenia_pond else 10.0, disabled=not e_cuenta)
                                
                            c_btn1, c_btn2 = st.columns(2)
                            with c_btn1:
                                if st.form_submit_button("💾 Guardar Cambios", type="primary", use_container_width=True):
                                    db.edit_entrega(id_e, e_desc, str(e_fec), float(e_pond) if e_cuenta else None)
                                    st.rerun()
                            with c_btn2:
                                if st.form_submit_button("🗑️ Eliminar Tarea", use_container_width=True):
                                    db.delete_entrega(id_e)
                                    st.rerun()

# ==============================================================================
# TAB 6: ASIGNATURAS Y ENLACES
# ==============================================================================
with tab_asig:
    sub_asig, sub_extra = st.tabs(["📚 Asignaturas", "🏅 Convalidaciones y Extra"])

    with sub_asig:
        col_c, col_a = st.columns(2)
        
        with col_c:
            st.subheader("➕ Crear Asignatura")
            with st.form("form_nasig", clear_on_submit=True):
                nom = st.text_input("Nombre de la Asignatura")
                c1, c2, c3 = st.columns(3)
                with c1: curso = st.selectbox("Curso", [1, 2, 3, 4, 5, 6], index=0)
                with c2: cuatri = st.selectbox("Cuatrimestre", [1, 2, 3], index=0)
                with c3: matricula = st.number_input("Nº Matrícula", min_value=1, max_value=6, value=1)
                    
                c4, c5 = st.columns(2)
                with c4: creditos = st.number_input("Créditos ECTS", min_value=1.0, max_value=30.0, value=6.0, step=0.5)
                with c5: min_asistencia = st.number_input("% Mín. Asistencia", min_value=0, max_value=100, value=80, step=5)
                
                st.markdown("**Enlaces Rápidos (Opcional)**")
                cl1, cl2, cl3 = st.columns(3)
                with cl1: l_camp = st.text_input("🌐 Campus Virtual URL")
                with cl2: l_guia = st.text_input("📄 Guía Docente URL")
                with cl3: l_apun = st.text_input("📁 Carpeta Apuntes URL")
                
                comentarios = st.text_area("Detalles (Profesor, aula...)")
                
                if st.form_submit_button("Crear Asignatura", width="stretch"):
                    if not nom.strip():
                        st.error("El nombre es obligatorio.")
                    else:
                        db.add_asignatura(nom, curso, cuatri, creditos, min_asistencia, comentarios, matricula, l_guia, l_camp, l_apun)
                        st.rerun()

        with col_a:
            st.subheader("🏁 Finalizar Asignatura")
            if mapa_activas:
                with st.form("form_ap"):
                    asig_ap = st.selectbox("Asignatura a cerrar", list(mapa_activas.keys()))
                    resultado = st.radio("Resultado final", ["Aprobada", "Suspensada"], horizontal=True)
                    notaf = st.number_input("Nota Definitiva (Acta)", value=5.0, min_value=0.0, max_value=10.0, step=0.1)
                    
                    if st.form_submit_button("Guardar Resultado", width="stretch"):
                        if resultado == "Aprobada":
                            db.aprobar_asignatura(mapa_activas[asig_ap], notaf)
                            st.success(f"¡Asignatura superada con un {notaf}!")
                        else:
                            db.suspender_asignatura(mapa_activas[asig_ap], notaf)
                            st.warning(f"Asignatura suspensa. Queda guardada en el expediente.")
                        st.rerun()
            else:
                st.info("No hay asignaturas en curso para finalizar.")
                
        # NUEVO: EDICIÓN DE ASIGNATURAS (Para poder meter enlaces a las importadas)
        with st.expander("✏️ Editar o Eliminar Asignatura"):
            if df_asignaturas.empty:
                st.info("No hay asignaturas para editar.")
            else:
                opciones_asig = {f"{r['nombre']} (C{r['curso']} - M{r['num_matricula']})": str(r['id_asignatura']) for _, r in df_asignaturas.iterrows()}
                sel_asig = st.selectbox("Asignatura a modificar", list(opciones_asig.keys()))
                if sel_asig:
                    id_as = opciones_asig[sel_asig]
                    r_as = df_asignaturas[df_asignaturas['id_asignatura'] == id_as].iloc[0]
                    with st.form("form_edit_asig"):
                        e_nom = st.text_input("Nombre", value=str(r_as['nombre']))
                        ce1, ce2, ce3 = st.columns(3)
                        with ce1: e_cur = st.number_input("Curso", min_value=1, max_value=6, value=int(r_as['curso']))
                        with ce2: e_cua = st.number_input("Cuatrimestre", min_value=1, max_value=3, value=int(r_as['cuatrimestre']))
                        with ce3: e_mat = st.number_input("Matrícula", min_value=1, max_value=6, value=int(r_as['num_matricula']))
                        
                        ce4, ce5 = st.columns(2)
                        with ce4: e_cred = st.number_input("Créditos ECTS", min_value=1.0, max_value=30.0, value=float(r_as['creditos']))
                        with ce5: e_min_as = st.number_input("% Mín. Asistencia", min_value=0.0, max_value=100.0, value=float(r_as['min_asistencia_pct']))
                        
                        st.markdown("**Enlaces Rápidos**")
                        cl1, cl2, cl3 = st.columns(3)
                        with cl1: e_camp = st.text_input("Campus Virtual", value=str(r_as.get('link_campus', '')))
                        with cl2: e_guia = st.text_input("Guía Docente", value=str(r_as.get('link_guia', '')))
                        with cl3: e_apun = st.text_input("Apuntes", value=str(r_as.get('link_apuntes', '')))
                        
                        e_com = st.text_area("Detalles", value=str(r_as.get('comentarios', '')))
                        
                        cb1, cb2 = st.columns(2)
                        with cb1:
                            if st.form_submit_button("💾 Guardar Cambios", type="primary", use_container_width=True):
                                db.edit_asignatura(id_as, e_nom, e_cur, e_cua, e_cred, e_min_as, e_com, e_mat, e_guia, e_camp, e_apun)
                                st.rerun()
                        with cb2:
                            if st.form_submit_button("🗑️ Eliminar Asignatura", use_container_width=True):
                                db.delete_asignatura(id_as)
                                st.rerun()

        st.divider()
        st.subheader("📋 Directorio de Asignaturas")
        if df_asignaturas.empty:
            st.info("Aún no tienes asignaturas registradas.")
        else:
            for _, asig in df_asignaturas.iterrows():
                if asig["estado"] == "Aprobada": 
                    icono_estado = "✅"
                    txt_estado = f"Aprobada: {asig['nota_final']}"
                elif asig["estado"] == "Suspensada": 
                    icono_estado = "❌"
                    txt_estado = f"Suspensada: {asig['nota_final']}"
                else: 
                    icono_estado = "📘"
                    txt_estado = "Cursando"
                
                badge_mat = f"⚠️ {asig['num_matricula']}ª Matrícula | " if asig["num_matricula"] > 1 else ""
                
                with st.expander(f"{icono_estado} {asig['nombre']} ({txt_estado})"):
                    # SECCIÓN DE ENLACES RÁPIDOS
                    links_html = []
                    if asig.get("link_campus") and str(asig["link_campus"]).strip(): 
                        links_html.append(f"<a href='{asig['link_campus']}' target='_blank' style='text-decoration:none;'>🌐 Campus Virtual</a>")
                    if asig.get("link_guia") and str(asig["link_guia"]).strip(): 
                        links_html.append(f"<a href='{asig['link_guia']}' target='_blank' style='text-decoration:none;'>📄 Guía Docente</a>")
                    if asig.get("link_apuntes") and str(asig["link_apuntes"]).strip(): 
                        links_html.append(f"<a href='{asig['link_apuntes']}' target='_blank' style='text-decoration:none;'>📁 Apuntes</a>")
                    
                    if links_html:
                        st.markdown(" | ".join(links_html), unsafe_allow_html=True)
                        st.markdown("") # Espacio en blanco
                    
                    nota_info = f"**Nota Final:** {asig['nota_final']} | " if asig["estado"] != "Cursando" else ""
                    st.write(f"{badge_mat}{nota_info}**Créditos:** {asig['creditos']} ECTS | **Curso:** {asig['curso']} | **Cuatrimestre:** {asig['cuatrimestre']}")
                    tiene_comentarios = pd.notnull(asig.get('comentarios')) and str(asig.get('comentarios')).strip() != ""
                    if tiene_comentarios:
                        st.info(f"📝 **Detalles:**\n\n{asig['comentarios']}")

    with sub_extra:
        st.subheader("🏅 Créditos Extra y Convalidaciones")
        st.write("Añade aquí los créditos obtenidos por idiomas, deportes, torneos, cursos externos o representación estudiantil. Estos créditos suman a tu total pero no afectan a tu nota media.")
        
        c_ex_form, c_ex_list = st.columns([1, 1.2])
        
        with c_ex_form:
            with st.form("form_extra", clear_on_submit=True):
                desc_extra = st.text_input("Descripción (Ej: Certificado B2 Inglés)")
                cred_extra = st.number_input("Créditos ECTS", min_value=0.5, max_value=30.0, value=3.0, step=0.5)
                fec_extra = st.date_input("Fecha de obtención", value=datetime.now())
                
                if st.form_submit_button("Añadir Créditos", width="stretch"):
                    if not desc_extra.strip():
                        st.error("Introduce una descripción válida.")
                    else:
                        db.add_credito_extra(desc_extra, cred_extra, str(fec_extra))
                        st.rerun()
                        
        with c_ex_list:
            if df_creditos_extra.empty:
                st.info("No tienes créditos extra registrados.")
            else:
                for _, extra in df_creditos_extra.iterrows():
                    with st.container():
                        c_txt, c_btn = st.columns([4, 1])
                        with c_txt:
                            f_str = extra['fecha']
                            st.markdown(f"**{extra['descripcion']}**  \n*{extra['creditos']} ECTS* | 📅 {f_str}")
                        with c_btn:
                            if st.button("🗑️", key=f"del_ex_{extra['id_credito']}", help="Eliminar"):
                                db.delete_credito_extra(extra['id_credito'])
                                st.rerun()
                        st.markdown("---")

# ==============================================================================
# TAB 7: AJUSTES Y BACKUP
# ==============================================================================
with tab_ajustes:
    st.subheader("⚙️ Ajustes y Copias de Seguridad")
    st.write("Gestiona la base de datos de tu aplicación de forma local y segura.")
    st.divider()

    col_down, col_up = st.columns(2)

    with col_down:
        st.markdown("#### ⬇️ Exportar Datos")
        st.write("Descarga una copia de seguridad completa de tu expediente. Este archivo contiene todas tus notas, horarios y configuraciones en su estado actual.")
        try:
            with open(db.DB_FILE, "rb") as f:
                db_bytes = f.read()
            st.download_button(
                label="💾 Descargar copia de seguridad (.db)",
                data=db_bytes,
                file_name=f"backup_carrera_{datetime.now().strftime('%Y%m%d_%H%M')}.db",
                mime="application/octet-stream",
                use_container_width=True
            )
        except Exception as e:
            st.error("No se pudo leer la base de datos para exportar.")

    with col_up:
        st.markdown("#### ⬆️ Importar Datos")
        st.warning("⚠️ **Peligro:** Importar una copia sobrescribirá TODOS los datos actuales de tu aplicación. Esta acción no se puede deshacer.")
        uploaded_file = st.file_uploader("Sube tu archivo de base de datos (.db)", type=["db"])
        
        if uploaded_file is not None:
            if st.button("🚨 Confirmar Restauración", type="primary", use_container_width=True):
                try:
                    with open(db.DB_FILE, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.success("¡Base de datos restaurada con éxito! Recargando...")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al restaurar la base de datos: {e}")
