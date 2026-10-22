"""
UniHub - Prototipo visual de plataforma universitaria "Todo en Uno"
Requisitos: pip install "streamlit>=1.37" pandas
Ejecutar:   streamlit run app.py
"""

import calendar
import copy
import random
import time
from datetime import date, timedelta

import pandas as pd
import streamlit as st

# ─────────────────────────────────────────────────────────────
# Configuración general
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="UniHub | Plataforma universitaria",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stMarkdown, button, input, textarea {
    font-family: 'Figtree', system-ui, -apple-system, sans-serif !important;
}
.block-container {padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1500px;}

/* Barra superior */
.topbar {display:flex; justify-content:space-between; align-items:center; gap:16px;
    padding:16px 24px; border-radius:18px; background:#1E2A4A; color:#F5F7FB; margin-bottom:14px;
    background-image: radial-gradient(rgba(255,255,255,.07) 1px, transparent 1px); background-size: 14px 14px;}
.topbar .brand {font-size:1.5rem; font-weight:800; letter-spacing:-.02em;}
.topbar .sub {opacity:.75; font-size:.9rem;}
.topbar .right {text-align:right;}

/* Elementos comunes */
.pill {display:inline-block; padding:3px 10px; border-radius:999px; font-size:.75rem; font-weight:700;}
.pill-green {background:rgba(47,125,91,.15); color:#2F7D5B;}
.pill-amber {background:rgba(224,165,38,.18); color:#A9740A;}
.pill-red {background:rgba(214,69,61,.15); color:#D6453D;}
.pill-blue {background:rgba(59,91,219,.14); color:#3B5BDB;}
.pill-white {background:rgba(255,255,255,.16); color:#fff;}
.muted {opacity:.65; font-size:.83rem;}
.card {border:1px solid rgba(128,128,128,.22); border-radius:16px; padding:16px 18px;
    background:rgba(128,128,128,.05); height:100%; margin-bottom:12px;}
.subject {border-top:5px solid var(--accent);}
.subject .code {font-size:.75rem; font-weight:700; color:var(--accent);}
.subject .name {font-size:1.05rem; font-weight:700; margin:4px 0 2px 0;}
.subject .foot {display:flex; justify-content:space-between; align-items:center; margin-top:10px; font-size:.85rem;}
.track {height:6px; background:rgba(128,128,128,.2); border-radius:99px; overflow:hidden; margin-top:10px;}
.fill {height:100%; background:var(--accent); border-radius:99px;}

/* Horario */
.tl {display:flex; gap:14px; margin-bottom:10px;}
.tl-time {min-width:105px; font-weight:700; font-size:.85rem; padding-top:12px; font-variant-numeric:tabular-nums;}
.tl-body {flex:1; border-radius:12px; padding:10px 14px; border:1px solid rgba(128,128,128,.22);
    border-left:5px solid var(--accent); background:rgba(128,128,128,.04);}
.tl-now {background:rgba(59,91,219,.09); border-color:#3B5BDB; border-left-color:var(--accent);}
.tl-done {opacity:.5;}
.tl-title {font-weight:700;}

/* Video */
.video {position:relative; background:radial-gradient(circle at 50% 40%, #273449 0%, #000 75%);
    border-radius:18px; height:410px; display:flex; flex-direction:column; align-items:center;
    justify-content:center; color:#E5E7EB; overflow:hidden;}
.video .avatar {font-size:6rem; line-height:1;}
.video .who {margin-top:10px; font-weight:600; opacity:.85;}
.video .live {position:absolute; top:14px; left:14px; background:#D6453D; color:#fff; font-weight:800;
    font-size:.75rem; padding:4px 10px; border-radius:6px;}
.video .live::before {content:""; display:inline-block; width:8px; height:8px; border-radius:50%;
    background:#fff; margin-right:6px; animation:pulse 1.4s infinite;}
.video .viewers {position:absolute; top:14px; right:14px; background:rgba(0,0,0,.55); padding:4px 10px;
    border-radius:6px; font-size:.8rem;}
.video .slide {position:absolute; top:56px; left:18px; background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.15);
    padding:10px 14px; border-radius:10px; font-size:.8rem; max-width:240px;}
.video .pip {position:absolute; bottom:64px; right:16px; width:150px; height:92px; border-radius:10px;
    background:#1F2937; border:2px solid #4B5563; display:flex; align-items:center; justify-content:center; font-size:2.2rem;}
.video .bar {position:absolute; bottom:0; left:0; right:0; padding:12px 16px; display:flex; justify-content:space-between;
    background:linear-gradient(transparent, rgba(0,0,0,.85)); font-size:.85rem;}
@keyframes pulse {0%{opacity:1} 50%{opacity:.25} 100%{opacity:1}}

/* Transcripción */
.transcript {border-radius:14px; padding:12px 16px; background:rgba(128,128,128,.06); border:1px solid rgba(128,128,128,.22);}
.transcript .line {padding:5px 0; opacity:.55; display:flex; gap:12px;}
.transcript .line.current {opacity:1; font-weight:600;}
.transcript .ts {font-variant-numeric:tabular-nums; opacity:.7; min-width:62px;}
.cursor {display:inline-block; width:8px; height:1em; background:currentColor; margin-left:4px;
    animation:blink 1s steps(1) infinite; vertical-align:-2px;}
@keyframes blink {50% {opacity:0}}

/* Calendario */
.cal {display:grid; grid-template-columns:repeat(7, 1fr); gap:4px; text-align:center; font-size:.85rem;}
.cal .h {font-weight:700; opacity:.6; padding:4px 0;}
.cal .d {padding:8px 0; border-radius:8px; font-variant-numeric:tabular-nums;}
.cal .o {opacity:.25;}
.cal .t {outline:2px solid #3B5BDB; font-weight:800;}
.cal .m {color:#fff; font-weight:700;}

/* Cronómetro */
.timer {font-size:3.4rem; font-weight:800; text-align:center; font-variant-numeric:tabular-nums; letter-spacing:-.02em;}

/* Perfil lateral */
.profile {text-align:center; border-radius:18px; padding:20px 14px; border:1px solid rgba(128,128,128,.22);
    background:rgba(128,128,128,.05);}
.profile .av {width:84px; height:84px; margin:0 auto 10px auto; border-radius:50%; display:flex; align-items:center;
    justify-content:center; font-size:2.8rem; background:#1E2A4A; border:3px solid #2F7D5B;}
.profile .pn {font-weight:800; font-size:1.1rem;}
.profile .pr {opacity:.75; font-size:.88rem; margin-bottom:8px;}

/* Componentes nativos */
div[data-testid="stMetric"] {border:1px solid rgba(128,128,128,.22); border-radius:14px; padding:12px 16px; background:rgba(128,128,128,.04);}
.stTabs [data-baseweb="tab-list"] {gap:6px;}
.stTabs [data-baseweb="tab"] {padding:8px 16px; font-weight:600;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def html(markup: str) -> None:
    """Renderiza HTML sin sangrías ni líneas vacías (evita que Markdown lo trate como código)."""
    clean = "\n".join(line.strip() for line in markup.splitlines() if line.strip())
    st.markdown(clean, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# Datos simulados
# ─────────────────────────────────────────────────────────────
HOY = date.today()
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def fecha_larga(d: date) -> str:
    return f"{DIAS[d.weekday()].capitalize()} {d.day} de {MESES[d.month - 1]}"


def fecha_corta(d: date) -> str:
    return f"{DIAS[d.weekday()][:3].capitalize()} {d.day} {MESES[d.month - 1][:3]}"


PERFILES = {
    "Vista Estudiante": {
        "avatar": "👨‍🎓", "nombre": "Benjamín Espinoza",
        "rol": "Estudiante, Ing. Informática", "extra": "Matrícula 2022-4581, 4.º año",
    },
    "Vista Profesor": {
        "avatar": "👩‍🏫", "nombre": "Dra. Carolina Muñoz",
        "rol": "Profesora, Depto. de Informática", "extra": "4 cursos activos, 168 alumnos",
    },
}

ASIGNATURAS = [
    {"codigo": "INF-331", "nombre": "Ingeniería de Software", "profe": "Prof. Rodrigo Vergara",
     "sala": "Sala A-204", "avance": 68, "nota": 6.1, "alumnos": 42, "color": "#3B5BDB"},
    {"codigo": "INF-239", "nombre": "Bases de Datos", "profe": "Prof. Daniela Rojas",
     "sala": "Lab B-12", "avance": 54, "nota": 5.7, "alumnos": 38, "color": "#0E9AA7"},
    {"codigo": "MAT-023", "nombre": "Cálculo III", "profe": "Prof. Andrés Fuentes",
     "sala": "Sala C-301", "avance": 72, "nota": 5.2, "alumnos": 55, "color": "#E0A526"},
    {"codigo": "INF-256", "nombre": "Redes de Computadores", "profe": "Dra. Carolina Muñoz",
     "sala": "Modalidad híbrida", "avance": 41, "nota": 6.4, "alumnos": 33, "color": "#2F7D5B"},
]

HORARIO = [  # (inicio, fin, asignatura, lugar, estado, color)
    ("08:30", "10:00", "Cálculo III", "Sala C-301", "done", "#E0A526"),
    ("10:15", "11:45", "Ingeniería de Software (en vivo)", "Sala A-204 + streaming", "now", "#3B5BDB"),
    ("13:00", "14:30", "Bases de Datos", "Lab B-12", "next", "#0E9AA7"),
    ("15:00", "16:30", "Redes de Computadores", "Modalidad híbrida", "next", "#2F7D5B"),
    ("17:00", "18:00", "Ayudantía Cálculo III", "Sala C-105", "next", "#8E7CC3"),
]

EVALUACIONES = [  # (título, asignatura, días desde hoy, lugar, tipo, color, ponderación)
    ("Control 3", "Cálculo III", 2, "Sala C-301, 08:30", "Prueba", "#E0A526", "20%"),
    ("Quiz online: Normalización", "Bases de Datos", 4, "En la plataforma, hasta 23:59", "Quiz online", "#0E9AA7", "10%"),
    ("Entrega Sprint 2", "Ingeniería de Software", 7, "GitHub Classroom", "Proyecto", "#3B5BDB", "25%"),
    ("Certamen 2", "Redes de Computadores", 9, "Híbrida, 15:00", "Certamen", "#2F7D5B", "30%"),
]

TRANSCRIPCION = [
    ("Bien, retomemos lo que vimos la clase pasada sobre patrones creacionales.",
     "Okay, let's pick up where we left off last class on creational patterns."),
    ("El patrón Singleton garantiza que una clase tenga una única instancia.",
     "The Singleton pattern ensures a class has only one instance."),
    ("Ojo, que abusar del Singleton genera acoplamiento y complica las pruebas.",
     "Careful, overusing Singleton creates coupling and makes testing harder."),
    ("Ahora pasemos al patrón Observer, muy usado en interfaces reactivas.",
     "Now let's move on to the Observer pattern, widely used in reactive UIs."),
    ("Un sujeto notifica a sus observadores cada vez que cambia su estado.",
     "A subject notifies its observers whenever its state changes."),
    ("Piensen en el chat de esta misma plataforma: es un Observer en acción.",
     "Think of this platform's own chat: it's an Observer in action."),
    ("¿Alguien me puede dar un ejemplo de Observer en su proyecto semestral?",
     "Can someone give me an example of Observer in their semester project?"),
    ("Exacto, las notificaciones push son un muy buen ejemplo.",
     "Exactly, push notifications are a great example."),
    ("Para el Sprint 2 quiero que documenten al menos dos patrones aplicados.",
     "For Sprint 2 I want you to document at least two applied patterns."),
    ("Recuerden subir el diagrama de clases actualizado al repositorio.",
     "Remember to upload the updated class diagram to the repository."),
]

RESPUESTAS_CHAT = [
    ("Camila Torres", "👩‍💻", "¡Buena pregunta! Yo tenía la misma duda 🙌"),
    ("Matías González", "🧑‍💻", "Lo explicó en la diapositiva 12, creo."),
    ("Prof. Vergara", "👨‍🏫", "Lo vemos al final de la clase, anótalo en tus apuntes 😉"),
    ("Valentina Rojas", "👩‍🎓", "+1, ¿alguien tiene el link del repo?"),
]

ENCUESTA = {
    "pregunta": "¿Cuál es la complejidad de la búsqueda binaria?",
    "opciones": {"A": "O(n)", "B": "O(log n)", "C": "O(n log n)", "D": "O(1)"},
    "pesos": [2, 6, 3, 1],
}

BANCO_SORPRESA = {
    "Patrones de diseño": ("¿Qué patrón notifica a varios objetos cuando cambia un estado?",
                           ["Singleton", "Observer", "Factory", "Adapter"], 1),
    "Bases de datos": ("¿Qué forma normal elimina las dependencias transitivas?",
                       ["1FN", "2FN", "3FN", "FNBC"], 2),
    "Redes": ("¿En qué capa del modelo OSI opera el protocolo IP?",
              ["Enlace", "Red", "Transporte", "Aplicación"], 1),
}

NICKS = ["@cami_t", "@mati.g", "@vale_r", "@seba_m", "@isi.perez", "@tomas_s", "@cata_d", "@joaco_c"]

# ─────────────────────────────────────────────────────────────
# Estado de sesión
# ─────────────────────────────────────────────────────────────
DEFAULTS = {
    "rol": "Vista Estudiante",
    "chat": [
        {"autor": "Prof. Vergara", "avatar": "👨‍🏫", "texto": "¡Buenos días! Hoy cerramos patrones de diseño. La grabación queda disponible al terminar."},
        {"autor": "Camila Torres", "avatar": "👩‍💻", "texto": "Profe, ¿el Sprint 2 se entrega el viernes o el lunes?"},
        {"autor": "Prof. Vergara", "avatar": "👨‍🏫", "texto": "El lunes a las 23:59, por GitHub Classroom 👍"},
        {"autor": "Matías González", "avatar": "🧑‍💻", "texto": "Gracias profe 🙏"},
    ],
    "transcript_idx": 4,
    "aviso_fin": False,
    "notas": "## Patrones de diseño\n- Singleton: una sola instancia (¡cuidado con el acoplamiento!)\n- Observer: sujeto notifica a observadores\n\nTODO: documentar 2 patrones para el Sprint 2",
    "edt_raiz": "Proyecto semestral: App de reservas",
    "edt_texto": "Análisis\n- Entrevistas a usuarios\n- Historias de usuario\nDiseño\n- Arquitectura (patrón Observer)\n- Prototipo UI\nDesarrollo\n- API backend\n- Frontend web\nPruebas y despliegue\n- Pruebas unitarias\n- Deploy en la nube",
    "justificaciones": [
        {"alumno": "Camila Torres", "fecha": HOY - timedelta(days=3), "motivo": "Cuadro febril, reposo de 48 h indicado por médico.",
         "archivo": "certificado_ctorres.pdf", "estado": "pendiente"},
    ],
    "votacion_activa": False,
    "votos": {"A": 0, "B": 0, "C": 0, "D": 0},
    "voto_propio": None,
    "feed_votos": [],
    "bano_inicio": None,
    "bano_historial": [],
    "sorpresa": None,
    "sorpresa_respuesta": None,
    "sorpresa_notificada": False,
}

for clave, valor in DEFAULTS.items():
    if clave not in st.session_state:
        st.session_state[clave] = copy.deepcopy(valor)

# ─────────────────────────────────────────────────────────────
# Barra lateral
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    html("<div style='font-size:1.4rem;font-weight:800'>🎓 UniHub</div>")
    st.caption("Tu universidad en una sola pantalla")
    st.radio("Cambiar vista", ["Vista Estudiante", "Vista Profesor"], key="rol", horizontal=True)

es_profe = st.session_state.rol == "Vista Profesor"
perfil = PERFILES[st.session_state.rol]
pendientes_just = sum(1 for j in st.session_state.justificaciones if j["estado"] == "pendiente")

with st.sidebar:
    html(f"""
    <div class="profile">
    <div class="av">{perfil['avatar']}</div>
    <div class="pn">{perfil['nombre']}</div>
    <div class="pr">{perfil['rol']}</div>
    <div class="muted">{perfil['extra']}</div>
    <div style="margin-top:10px"><span class="pill pill-green">● En línea</span></div>
    </div>
    """)
    st.write("")
    st.markdown("##### 📈 Métricas rápidas")
    c1, c2 = st.columns(2)
    if es_profe:
        c1.metric("Asistencia curso", "87%", "-2%")
        c2.metric("Por revisar", pendientes_just)
        st.progress(0.87, text="Asistencia promedio del curso: 87%")
    else:
        c1.metric("Asistencia", "92%", "+3%")
        c2.metric("Promedio", "5,9", "+0,2")
        st.progress(0.92, text="Asistencia general: 92% (mínimo 75%)")
    st.divider()
    st.markdown("##### ⏭️ Próxima clase")
    st.caption("Bases de Datos, 13:00 en Lab B-12")
    st.divider()
    if st.button("🔄 Reiniciar demo"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# ─────────────────────────────────────────────────────────────
# Barra superior y alertas globales
# ─────────────────────────────────────────────────────────────
modo = "👩‍🏫 Modo profesor" if es_profe else "👨‍🎓 Modo estudiante"
html(f"""
<div class="topbar">
<div><div class="brand">UniHub</div><div class="sub">{fecha_larga(HOY)}, semestre de primavera {HOY.year}</div></div>
<div class="right"><span class="pill pill-white">{modo}</span><div class="sub" style="margin-top:6px">🔔 3 notificaciones nuevas</div></div>
</div>
""")

sorpresa_pendiente = st.session_state.sorpresa is not None and st.session_state.sorpresa_respuesta is None
if not es_profe and sorpresa_pendiente:
    if not st.session_state.sorpresa_notificada:
        st.toast("¡Evaluación sorpresa disponible! Responde rápido para ganar décimas.", icon="⚡")
        st.session_state.sorpresa_notificada = True
    st.info("⚡ **Evaluación sorpresa activa.** Ve a la pestaña *Herramientas Interactivas* para responder.")

tab_dash, tab_aula, tab_cal, tab_tools = st.tabs([
    "📊 Dashboard & Horario",
    "🎥 Aula Híbrida (En Vivo)",
    "📅 Calendario & Evaluaciones",
    "🛠️ Herramientas Interactivas",
])

# ─────────────────────────────────────────────────────────────
# 1. Dashboard & Horario
# ─────────────────────────────────────────────────────────────
with tab_dash:
    m1, m2, m3, m4 = st.columns(4)
    if es_profe:
        m1.metric("Clases hoy", "2", "1 híbrida")
        m2.metric("Tareas por corregir", "18", "+6 hoy", delta_color="inverse")
        m3.metric("Justificaciones", pendientes_just, "pendientes", delta_color="off")
        m4.metric("Conectados ahora", "38 / 42", "90%")
    else:
        m1.metric("Clases hoy", "5", "1 en vivo ahora")
        m2.metric("Tareas pendientes", "3", "-1 desde ayer")
        m3.metric("Próxima evaluación", fecha_corta(HOY + timedelta(days=2)), "Control 3", delta_color="off")
        m4.metric("Promedio semestral", "5,9", "+0,2")

    st.markdown("#### 📚 Asignaturas del semestre")
    cols = st.columns(4)
    for col, a in zip(cols, ASIGNATURAS):
        dato = f"👥 {a['alumnos']} alumnos" if es_profe else f"Nota: <b>{a['nota']:.1f}</b>".replace(".", ",")
        with col:
            html(f"""
            <div class="card subject" style="--accent:{a['color']}">
            <div class="code">{a['codigo']}</div>
            <div class="name">{a['nombre']}</div>
            <div class="muted">{a['profe']}</div>
            <div class="muted">📍 {a['sala']}</div>
            <div class="track"><div class="fill" style="width:{a['avance']}%"></div></div>
            <div class="foot"><span class="muted">{a['avance']}% del curso</span><span>{dato}</span></div>
            </div>
            """)

    st.divider()
    izq, der = st.columns([1.6, 1], gap="large")

    with izq:
        st.markdown("#### 🗓️ Horario de hoy")
        st.caption("Hora simulada: 11:20")
        bloques = []
        for ini, fin, nombre, lugar, estado, color in HORARIO:
            clase = {"done": "tl-done", "now": "tl-now", "next": ""}[estado]
            badge = {"done": "<span class='pill pill-green'>Finalizada</span>",
                     "now": "<span class='pill pill-red'>● En curso</span>",
                     "next": "<span class='pill pill-blue'>Próxima</span>"}[estado]
            bloques.append(f"""
            <div class="tl {clase}">
            <div class="tl-time">{ini} – {fin}</div>
            <div class="tl-body" style="--accent:{color}">
            <div style="display:flex;justify-content:space-between;align-items:center">
            <span class="tl-title">{nombre}</span>{badge}</div>
            <div class="muted">📍 {lugar}</div>
            </div></div>
            """)
        html("".join(bloques))

    with der:
        st.markdown("#### 💬 Chat del curso")
        st.caption("Ingeniería de Software, 42 participantes")
        caja = st.container(height=400)
        with caja:
            for m in st.session_state.chat:
                with st.chat_message(m["autor"], avatar=m["avatar"]):
                    st.markdown(f"**{m['autor']}**  \n{m['texto']}")
        with st.form("chat_form", clear_on_submit=True, border=False):
            fc1, fc2 = st.columns([5, 1], vertical_alignment="bottom")
            mensaje = fc1.text_input("Mensaje", placeholder="Escribe un mensaje al curso…", label_visibility="collapsed")
            enviar = fc2.form_submit_button("Enviar")
        if enviar and mensaje.strip():
            st.session_state.chat.append({"autor": perfil["nombre"], "avatar": perfil["avatar"], "texto": mensaje.strip()})
            autor, avatar, texto = random.choice(RESPUESTAS_CHAT)
            st.session_state.chat.append({"autor": autor, "avatar": avatar, "texto": texto})
            st.rerun()

# ─────────────────────────────────────────────────────────────
# 2. Aula Híbrida (En Vivo)
# ─────────────────────────────────────────────────────────────
@st.fragment(run_every=2.5)
def transcripcion_en_vivo():
    idx = st.session_state.transcript_idx
    st.session_state.transcript_idx = idx + 1
    traducir = st.session_state.get("idioma", "Original (español)") != "Original (español)"
    base = 10 * 3600 + 15 * 60 + 30 * 60  # 10:45 como referencia
    lineas = []
    for k in range(4, -1, -1):
        i = idx - k
        es, en = TRANSCRIPCION[i % len(TRANSCRIPCION)]
        seg = base + i * 7
        ts = f"{seg // 3600:02d}:{seg % 3600 // 60:02d}:{seg % 60:02d}"
        texto = en if traducir else es
        actual = k == 0
        cursor = "<span class='cursor'></span>" if actual else ""
        lineas.append(f"<div class='line {'current' if actual else ''}'><span class='ts'>{ts}</span><span>{texto}{cursor}</span></div>")
    html(f"<div class='transcript'>{''.join(lineas)}</div>")
    st.caption("🤖 Modelo de voz a texto simulado. Precisión estimada: 97%")


def construir_dot(raiz: str, texto: str) -> str:
    def esc(s: str) -> str:
        return s.replace('"', "'")

    dot = [
        "digraph EDT {",
        'graph [rankdir=TB, bgcolor="transparent", nodesep=0.25, ranksep=0.45];',
        'node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=10, color="#3B5BDB", fillcolor="#EEF2FF", fontcolor="#1E2A4A"];',
        'edge [color="#94A3B8", arrowhead=none];',
        f'root [label="0. {esc(raiz)}", fillcolor="#1E2A4A", fontcolor="white", color="#1E2A4A", fontsize=11];',
    ]
    principal, n, sub = None, 0, 0
    for linea in texto.splitlines():
        if not linea.strip():
            continue
        if linea.strip().startswith("-"):
            if principal is None:
                continue
            sub += 1
            nodo = f"n{n}_{sub}"
            dot.append(f'{nodo} [label="{n}.{sub} {esc(linea.strip()[1:].strip())}", fillcolor="#F1F7F4", color="#2F7D5B"];')
            dot.append(f"{principal} -> {nodo};")
        else:
            n += 1
            sub = 0
            principal = f"n{n}"
            dot.append(f'{principal} [label="{n}. {esc(linea.strip())}"];')
            dot.append(f"root -> {principal};")
    dot.append("}")
    return "\n".join(dot)


with tab_aula:
    if st.session_state.aviso_fin:
        st.warning("⏰ **Profesor:** La clase termina en 10 minutos. Revisen sus apuntes y dejen sus preguntas en el chat.")

    izq, der = st.columns([1.7, 1], gap="large")

    with izq:
        h1, h2 = st.columns([3, 1.3], vertical_alignment="center")
        h1.markdown("#### INF-331 Ingeniería de Software: Clase 14, patrones de diseño")
        etiqueta = "🔔 Avisar fin de clase" if es_profe else "🔔 Simular aviso del profesor"
        if h2.button(etiqueta, type="primary"):
            st.session_state.aviso_fin = True
            st.toast("Profesor: La clase termina en 10 minutos", icon="⏰")
            st.rerun()

        html("""
        <div class="video">
        <div class="live">EN VIVO</div>
        <div class="viewers">👁️ 38 conectados &nbsp; ⏱️ 01:07:42</div>
        <div class="slide">📑 Diapositiva 14 de 22<br><b>Patrón Observer</b><br>Sujeto → Observadores</div>
        <div class="avatar">👨‍🏫</div>
        <div class="who">Prof. Rodrigo Vergara, Sala A-204</div>
        <div class="pip">👨‍🎓</div>
        <div class="bar"><span>🎙️ Audio HD &nbsp; 📶 1080p</span><span>⛶ Pantalla completa</span></div>
        </div>
        """)

        b1, b2, b3, b4 = st.columns(4)
        if b1.button("✋ Levantar la mano"):
            st.toast("Mano levantada. El profesor verá tu turno en la cola.", icon="✋")
        if b2.button("👏 Reaccionar"):
            st.toast("Reacción enviada 👏")
        if b3.button("🎙️ Pedir la palabra"):
            st.toast("Solicitud enviada al moderador", icon="🎙️")
        if b4.button("⏺️ Marcar momento"):
            st.toast("Marcador guardado en 01:07:42", icon="📌")

        st.write("")
        t1, t2 = st.columns([2.2, 1.5], vertical_alignment="center")
        t1.markdown("##### 🤖 Transcripción y traducción IA en tiempo real")
        t2.radio("Idioma", ["Original (español)", "Traducción (inglés)"], key="idioma",
                 horizontal=True, label_visibility="collapsed")
        transcripcion_en_vivo()

    with der:
        st.markdown("##### 📝 Bloc de notas")
        st.text_area("Tus apuntes", key="notas", height=200, label_visibility="collapsed")
        n1, n2 = st.columns(2)
        n1.download_button("⬇️ Descargar .md", st.session_state.notas, file_name="apuntes_clase14.md")
        if n2.button("✨ Resumir con IA"):
            st.toast("Resumen generado (simulado): Singleton y Observer, tarea Sprint 2.", icon="✨")

        st.divider()
        st.markdown("##### 🧩 Generador de diagramas EDT")
        st.caption("Escribe una tarea por línea. Usa “-” al inicio para crear subtareas.")
        st.text_input("Entregable principal", key="edt_raiz")
        st.text_area("Puntos clave", key="edt_texto", height=170)
        st.graphviz_chart(construir_dot(st.session_state.edt_raiz, st.session_state.edt_texto))

# ─────────────────────────────────────────────────────────────
# 3. Calendario & Evaluaciones
# ─────────────────────────────────────────────────────────────
def mini_calendario(hoy: date, marcas: dict) -> str:
    semanas = calendar.Calendar(firstweekday=0).monthdatescalendar(hoy.year, hoy.month)
    celdas = [f"<div class='h'>{d}</div>" for d in ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]]
    for semana in semanas:
        for d in semana:
            clases, estilo = ["d"], ""
            if d.month != hoy.month:
                clases.append("o")
            if d == hoy:
                clases.append("t")
            if d in marcas:
                clases.append("m")
                estilo = f"style='background:{marcas[d]}'"
            celdas.append(f"<div class='{' '.join(clases)}' {estilo}>{d.day}</div>")
    titulo = f"<div style='font-weight:700;margin-bottom:8px'>{MESES[hoy.month - 1].capitalize()} {hoy.year}</div>"
    return f"<div class='card'>{titulo}<div class='cal'>{''.join(celdas)}</div></div>"


@st.cache_data
def tiempos_quiz() -> pd.DataFrame:
    rng = random.Random(7)
    nombres = ["Benjamín Espinoza", "Camila Torres", "Matías González", "Valentina Rojas", "Sebastián Muñoz",
               "Isidora Pérez", "Tomás Soto", "Catalina Díaz", "Joaquín Contreras", "Fernanda Silva",
               "Vicente Morales", "Antonia Araya"]
    filas = []
    for n in nombres:
        minutos = round(rng.uniform(13, 36), 1)
        puntaje = int(min(100, max(35, rng.gauss(72, 14))))
        filas.append({"Alumno": n, "Tiempo (min)": minutos, "Puntaje": puntaje,
                      "Cambios de pestaña": rng.randint(0, 2)})
    filas[8].update({"Tiempo (min)": 2.1, "Puntaje": 100, "Cambios de pestaña": 7})
    filas[10].update({"Tiempo (min)": 3.4, "Puntaje": 95, "Cambios de pestaña": 4})
    filas[4].update({"Tiempo (min)": 7.2, "Puntaje": 88})
    return pd.DataFrame(filas)


with tab_cal:
    st.markdown("#### 📅 Próximas evaluaciones")
    izq, der = st.columns([2, 1], gap="large")
    marcas = {}
    with izq:
        filas_ev = [EVALUACIONES[:2], EVALUACIONES[2:]]
        for fila in filas_ev:
            cols = st.columns(2)
            for col, (titulo, asig, dias, lugar, tipo, color, pond) in zip(cols, fila):
                f = HOY + timedelta(days=dias)
                marcas[f] = color
                urg = "pill-red" if dias <= 3 else ("pill-amber" if dias <= 7 else "pill-blue")
                with col:
                    html(f"""
                    <div class="card subject" style="--accent:{color}">
                    <div style="display:flex;justify-content:space-between"><span class="code">{tipo}</span>
                    <span class="pill {urg}">En {dias} días</span></div>
                    <div class="name">{titulo}</div>
                    <div class="muted">{asig}</div>
                    <div class="foot"><span>🗓️ {fecha_corta(f)}</span><span class="muted">Pondera {pond}</span></div>
                    <div class="muted" style="margin-top:4px">📍 {lugar}</div>
                    </div>
                    """)
    with der:
        html(mini_calendario(HOY, marcas))
        st.caption("Los días con color tienen una evaluación agendada.")

    st.divider()

    if not es_profe:
        c1, c2 = st.columns([1.3, 1], gap="large")
        with c1:
            with st.expander("🩺 Justificación médica", expanded=True):
                with st.form("form_justificacion", clear_on_submit=True, border=False):
                    fecha_aus = st.date_input("Fecha de la inasistencia", value=HOY, max_value=HOY, format="DD/MM/YYYY")
                    asig_aus = st.selectbox("Evaluación o clase afectada", [e[0] + ", " + e[1] for e in EVALUACIONES] + ["Clase regular"])
                    motivo = st.text_area("Motivo", placeholder="Describe brevemente la razón de tu ausencia…")
                    archivo = st.file_uploader("Certificado médico (PDF o imagen)", type=["pdf", "png", "jpg", "jpeg"])
                    enviada = st.form_submit_button("Enviar justificación", type="primary")
                if enviada:
                    if not motivo.strip():
                        st.error("Escribe el motivo de la inasistencia para poder enviar la solicitud.")
                    else:
                        st.session_state.justificaciones.append({
                            "alumno": PERFILES["Vista Estudiante"]["nombre"], "fecha": fecha_aus,
                            "motivo": f"{asig_aus}: {motivo.strip()}",
                            "archivo": archivo.name if archivo else "Sin adjunto", "estado": "pendiente",
                        })
                        st.success("Justificación enviada. Quedó pendiente de revisión por el profesor.")
        with c2:
            st.markdown("##### 📂 Mis solicitudes")
            propias = [j for j in st.session_state.justificaciones if j["alumno"] == "Benjamín Espinoza"]
            if not propias:
                st.caption("Aún no has enviado justificaciones. Usa el formulario para crear la primera.")
            for j in reversed(propias):
                pill = {"pendiente": ("pill-amber", "⏳ Pendiente de revisión por el profesor"),
                        "aprobada": ("pill-green", "✅ Aprobada"),
                        "rechazada": ("pill-red", "❌ Rechazada")}[j["estado"]]
                html(f"""
                <div class="card">
                <div style="display:flex;justify-content:space-between"><b>{j['fecha'].strftime('%d/%m/%Y')}</b>
                <span class="pill {pill[0]}">{pill[1]}</span></div>
                <div class="muted" style="margin-top:6px">{j['motivo']}</div>
                <div class="muted">📎 {j['archivo']}</div>
                </div>
                """)
    else:
        c1, c2 = st.columns([1, 1.5], gap="large")
        with c1:
            st.markdown("##### 🩺 Bandeja de justificaciones")
            for i, j in enumerate(st.session_state.justificaciones):
                with st.container(border=True):
                    st.markdown(f"**{j['alumno']}**, {j['fecha'].strftime('%d/%m/%Y')}")
                    st.caption(j["motivo"])
                    st.caption(f"📎 {j['archivo']}")
                    if j["estado"] == "pendiente":
                        a1, a2 = st.columns(2)
                        if a1.button("✅ Aprobar", key=f"apr_{i}"):
                            j["estado"] = "aprobada"
                            st.toast(f"Justificación de {j['alumno']} aprobada", icon="✅")
                            st.rerun()
                        if a2.button("❌ Rechazar", key=f"rec_{i}"):
                            j["estado"] = "rechazada"
                            st.toast(f"Justificación de {j['alumno']} rechazada", icon="❌")
                            st.rerun()
                    else:
                        st.markdown("✅ Aprobada" if j["estado"] == "aprobada" else "❌ Rechazada")

        with c2:
            st.markdown("##### ⏱️ Tiempos del quiz online: Normalización")
            df = tiempos_quiz().copy()
            umbral = st.slider("Marcar como sospechoso si el alumno tarda menos de este % de la mediana",
                               10, 60, 30, step=5, format="%d%%")
            mediana = df["Tiempo (min)"].median()

            def estado(t):
                if t < mediana * umbral / 100:
                    return "🚨 Sospechoso"
                if t < mediana * (umbral + 15) / 100:
                    return "⚠️ Revisar"
                return "✅ Normal"

            df["Estado"] = df["Tiempo (min)"].apply(estado)
            df = df.sort_values("Tiempo (min)")

            k1, k2, k3 = st.columns(3)
            k1.metric("Mediana", f"{mediana:.1f} min")
            k2.metric("Más rápido", f"{df['Tiempo (min)'].min():.1f} min")
            k3.metric("Casos sospechosos", int((df["Estado"] == "🚨 Sospechoso").sum()))

            def colorear(fila):
                if fila["Estado"].startswith("🚨"):
                    return ["background-color: rgba(214,69,61,.18)"] * len(fila)
                if fila["Estado"].startswith("⚠️"):
                    return ["background-color: rgba(224,165,38,.18)"] * len(fila)
                return [""] * len(fila)

            st.dataframe(
                df.style.apply(colorear, axis=1),
                hide_index=True,
                column_config={
                    "Tiempo (min)": st.column_config.NumberColumn(format="%.1f min"),
                    "Puntaje": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%d pts"),
                },
                height=300,
            )
            st.bar_chart(df.set_index("Alumno")["Tiempo (min)"], height=220, color="#3B5BDB")

# ─────────────────────────────────────────────────────────────
# 4. Herramientas Interactivas
# ─────────────────────────────────────────────────────────────
@st.fragment(run_every=1.5)
def encuesta_en_vivo():
    votos = st.session_state.votos
    if st.session_state.votacion_activa:
        for _ in range(random.randint(1, 3)):
            op = random.choices(list(votos), weights=ENCUESTA["pesos"])[0]
            votos[op] += 1
            st.session_state.feed_votos.insert(0, f"{random.choice(NICKS)} votó {op}")
        st.session_state.feed_votos = st.session_state.feed_votos[:6]

    total = sum(votos.values())
    estado = "<span class='pill pill-red'>● EN VIVO</span>" if st.session_state.votacion_activa \
        else "<span class='pill pill-blue'>Cerrada</span>"
    html(f"""
    <div style="display:flex;justify-content:space-between;align-items:center">
    <b>{ENCUESTA['pregunta']}</b>{estado}</div>
    <div class="muted">{total} votos recibidos</div>
    """)

    datos = pd.DataFrame({"Votos": [votos[k] for k in votos]},
                         index=[f"{k}) {v}" for k, v in ENCUESTA["opciones"].items()])
    st.bar_chart(datos, height=260, color="#7C4DFF")

    if not es_profe:
        if st.session_state.voto_propio:
            st.success(f"Votaste por la opción {st.session_state.voto_propio}.")
        elif st.session_state.votacion_activa:
            cols = st.columns(4)
            for col, (k, v) in zip(cols, ENCUESTA["opciones"].items()):
                if col.button(f"{k}) {v}", key=f"voto_{k}"):
                    votos[k] += 1
                    st.session_state.voto_propio = k
                    st.session_state.feed_votos.insert(0, f"@benja_e (tú) votó {k}")
                    st.rerun(scope="fragment")
        else:
            st.caption("La votación abrirá cuando el profesor la inicie.")

    if st.session_state.feed_votos:
        st.caption("  \n".join(f"🟣 {e}" for e in st.session_state.feed_votos[:4]))


@st.fragment(run_every=1)
def cronometro_bano():
    inicio = st.session_state.bano_inicio
    if inicio is None:
        html("<div class='timer' style='opacity:.35'>00:00</div>")
        st.caption("Nadie está fuera de la sala en este momento." if es_profe else "Estás en clase.")
        return
    seg = int(time.time() - inicio)
    mm, ss = divmod(seg, 60)
    color = "#2F7D5B" if seg < 300 else ("#E0A526" if seg < 600 else "#D6453D")
    html(f"<div class='timer' style='color:{color}'>{mm:02d}:{ss:02d}</div>")
    if es_profe:
        st.caption("🚻 Benjamín Espinoza está fuera de la sala.")
        if seg >= 600:
            st.error("Lleva más de 10 minutos fuera de la sala.")
    else:
        st.caption("El profesor puede ver este cronómetro.")


@st.fragment(run_every=1)
def sorpresa_alumno():
    s = st.session_state.sorpresa
    r = st.session_state.sorpresa_respuesta
    if s is None:
        st.caption("No hay evaluaciones sorpresa activas. Te avisaremos cuando el profesor lance una.")
        return
    if r is not None:
        if r.get("expirada"):
            st.error("Se acabó el tiempo de la evaluación sorpresa. La próxima vez responde más rápido.")
        elif r["correcta"]:
            st.success(f"🎉 ¡Correcto! Respondiste en {r['segundos']:.1f} s y ganaste **+{r['decimas']:.1f} décimas**.")
        else:
            st.warning(f"Respuesta incorrecta ({r['segundos']:.1f} s). Esta vez no sumas décimas.")
        return

    restante = max(0.0, s["limite"] - (time.time() - s["enviada"]))
    if restante <= 0:
        st.session_state.sorpresa_respuesta = {"expirada": True}
        st.rerun()
    potencial = s["decimas"] * restante / s["limite"]
    st.info(f"⚡ **¡Evaluación sorpresa!** Si respondes bien ahora ganas **+{potencial:.1f} décimas**. "
            f"Quedan **{int(restante)} s**.")
    st.progress(restante / s["limite"])
    eleccion = st.radio(s["pregunta"], s["opciones"], index=None, key="sorpresa_eleccion")
    if st.button("Enviar respuesta", type="primary", disabled=eleccion is None):
        seg = time.time() - s["enviada"]
        correcta = s["opciones"].index(eleccion) == s["correcta"]
        dec = round(s["decimas"] * max(0.0, s["limite"] - seg) / s["limite"], 1) if correcta else 0.0
        st.session_state.sorpresa_respuesta = {"correcta": correcta, "segundos": seg, "decimas": dec}
        st.rerun()


with tab_tools:
    c1, c2 = st.columns([1.5, 1], gap="large")

    with c1:
        st.markdown("#### 🟣 Quiz en vivo estilo Twitch")
        if es_profe:
            p1, p2, p3 = st.columns(3)
            if p1.button("▶️ Iniciar votación", type="primary", disabled=st.session_state.votacion_activa):
                st.session_state.votacion_activa = True
                st.rerun()
            if p2.button("⏸️ Cerrar votación", disabled=not st.session_state.votacion_activa):
                st.session_state.votacion_activa = False
                st.rerun()
            if p3.button("🔁 Reiniciar"):
                st.session_state.votos = {k: 0 for k in ENCUESTA["opciones"]}
                st.session_state.voto_propio = None
                st.session_state.feed_votos = []
                st.session_state.votacion_activa = False
                st.rerun()
        with st.container(border=True):
            encuesta_en_vivo()

    with c2:
        st.markdown("#### 🚻 Permiso para ir al baño")
        with st.container(border=True):
            if not es_profe:
                if st.session_state.bano_inicio is None:
                    if st.button("🚻 Ir al baño", type="primary"):
                        st.session_state.bano_inicio = time.time()
                        st.toast("Permiso registrado. El cronómetro está corriendo.", icon="🚻")
                        st.rerun()
                else:
                    if st.button("✅ Ya volví"):
                        dur = int(time.time() - st.session_state.bano_inicio)
                        st.session_state.bano_historial.append(dur)
                        st.session_state.bano_inicio = None
                        st.toast("Bienvenido de vuelta a clase", icon="✅")
                        st.rerun()
            cronometro_bano()
            if es_profe and st.session_state.bano_historial:
                prom = sum(st.session_state.bano_historial) / len(st.session_state.bano_historial)
                st.caption(f"Permisos hoy: {len(st.session_state.bano_historial)}, "
                           f"duración promedio {int(prom // 60):02d}:{int(prom % 60):02d}")

    st.divider()
    st.markdown("#### ⚡ Evaluación sorpresa")

    if es_profe:
        s1, s2 = st.columns([1.2, 1], gap="large")
        with s1:
            with st.container(border=True):
                tema = st.selectbox("Tema", list(BANCO_SORPRESA))
                pregunta, opciones, correcta = BANCO_SORPRESA[tema]
                st.caption(f"Pregunta: {pregunta}")
                d1, d2 = st.columns(2)
                decimas = d1.slider("Décimas máximas", 1, 10, 5)
                limite = d2.slider("Tiempo límite (s)", 15, 90, 30, step=5)
                if st.button("⚡ Lanzar evaluación sorpresa", type="primary"):
                    st.session_state.sorpresa = {"pregunta": pregunta, "opciones": opciones, "correcta": correcta,
                                                 "decimas": decimas, "limite": limite, "enviada": time.time()}
                    st.session_state.sorpresa_respuesta = None
                    st.session_state.sorpresa_notificada = False
                    st.session_state.pop("sorpresa_eleccion", None)
                    st.toast("Evaluación sorpresa enviada a 38 alumnos conectados", icon="⚡")
                    st.rerun()
        with s2:
            st.markdown("##### 📱 Vista previa en la pantalla del alumno")
            s = st.session_state.sorpresa
            r = st.session_state.sorpresa_respuesta
            if s is None:
                st.caption("Lanza una evaluación para ver cómo la recibe el alumno.")
            else:
                st.info(f"⚡ **¡Evaluación sorpresa!** Responde rápido y gana hasta **+{s['decimas']} décimas**.  \n{s['pregunta']}")
                if r is None:
                    st.caption("Esperando respuestas. Cambia a *Vista Estudiante* para responder como Benjamín.")
                elif r.get("expirada"):
                    st.caption("Benjamín Espinoza no respondió a tiempo.")
                else:
                    resultado = "correcta" if r["correcta"] else "incorrecta"
                    st.caption(f"Benjamín Espinoza: respuesta {resultado} en {r['segundos']:.1f} s, "
                               f"+{r['decimas']:.1f} décimas.")
    else:
        with st.container(border=True):
            sorpresa_alumno()

st.divider()
st.caption("UniHub, prototipo visual de alta fidelidad. Todos los datos son simulados.")
