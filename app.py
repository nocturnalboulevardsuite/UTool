"""
UniHub v2 — Plataforma universitaria "Todo en Uno" (prototipo funcional)

Reemplaza en una sola app: aula virtual (ramos, contenido, evaluaciones), clases en vivo con cámara,
chat en tiempo real, asistencia, calendario de evaluaciones con justificaciones, quizzes en vivo,
evaluaciones sorpresa, control de salidas al baño, monitoreo de evaluaciones online y herramientas de
IA (transcripción, traducción, apuntes y diagramas EDT) usando la API key de cada usuario.

Ejecutar:  pip install -r requirements.txt  &&  streamlit run app.py
Cuentas demo (contraseña: demo1234):
  benjamin.espinoza@alumnos.unihub.cl  (Estudiante, Ing. en Informática)
  juan.perez@alumnos.unihub.cl         (Estudiante, Ing. en Mecánica Automotriz)
  carolina.munoz@docentes.unihub.cl    (Docente)
  rodrigo.vergara@docentes.unihub.cl   (Docente)

Para probar el tiempo real: abre la app en dos navegadores (o uno normal y uno en incógnito),
entra como docente en uno y como estudiante en el otro.
"""

import base64
import calendar
import copy
import hashlib
import json
import random
import secrets
import threading
import time
import uuid
from datetime import date, datetime, timedelta

import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("America/Santiago")
except Exception:  # pragma: no cover
    TZ = None

st.set_page_config(page_title="UniHub", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

# ═════════════════════════════════════════════════════════════════════
# Estilos
# ═════════════════════════════════════════════════════════════════════
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], .stMarkdown, button, input, textarea, select {font-family:'Figtree', system-ui, sans-serif !important;}
.block-container {padding-top:1.4rem; padding-bottom:2rem; max-width:1500px;}
h2 {letter-spacing:-.02em;}
.pill {display:inline-block; padding:3px 10px; border-radius:999px; font-size:.75rem; font-weight:700; white-space:nowrap;}
.p-green {background:rgba(47,125,91,.15); color:#2F7D5B;}
.p-amber {background:rgba(224,165,38,.2); color:#9A6A08;}
.p-red {background:rgba(214,69,61,.15); color:#D6453D;}
.p-blue {background:rgba(59,91,219,.14); color:#3B5BDB;}
.p-gray {background:rgba(128,128,128,.16);}
.muted {opacity:.68; font-size:.85rem;}
.card {border:1px solid rgba(128,128,128,.22); border-radius:16px; padding:14px 18px; background:rgba(128,128,128,.05); margin-bottom:10px;}
.accent {border-left:5px solid var(--c);}
.ctitle {font-weight:700; font-size:1.02rem;}
.row {display:flex; justify-content:space-between; align-items:center; gap:10px;}
.hero {border-radius:18px; padding:20px 24px; color:#F5F7FB; background:#1E2A4A; margin-bottom:14px;
  background-image:radial-gradient(rgba(255,255,255,.07) 1px, transparent 1px); background-size:14px 14px;}
.hero .t {font-size:1.6rem; font-weight:800; letter-spacing:-.02em;}
.hero .s {opacity:.8;}
.track {height:7px; background:rgba(128,128,128,.2); border-radius:99px; overflow:hidden; margin-top:8px;}
.fill {height:100%; border-radius:99px;}
.tl {display:flex; gap:12px; margin-bottom:8px;}
.tl-h {min-width:96px; font-weight:700; font-size:.85rem; padding-top:11px; font-variant-numeric:tabular-nums;}
.tl-b {flex:1; border-radius:12px; padding:9px 14px; border:1px solid rgba(128,128,128,.22); border-left:5px solid var(--c);}
.tl-now {background:rgba(59,91,219,.09); border-color:#3B5BDB;}
.tl-done {opacity:.5;}
.week {display:grid; grid-template-columns:repeat(5, 1fr); gap:10px;}
.wday {border:1px solid rgba(128,128,128,.22); border-radius:14px; padding:10px; min-height:260px;}
.wday.today {border:2px solid #3B5BDB;}
.wday .dh {font-weight:800; margin-bottom:8px;}
.blk {border-radius:10px; padding:8px 10px; margin-bottom:8px; color:#fff; font-size:.85rem;}
.cal {display:grid; grid-template-columns:repeat(7,1fr); gap:5px; text-align:center;}
.cal .h {font-weight:700; opacity:.6; font-size:.8rem; padding:4px 0;}
.cal .d {border-radius:10px; padding:6px 2px; min-height:52px; border:1px solid rgba(128,128,128,.15); font-size:.85rem;}
.cal .o {opacity:.3;}
.cal .t {outline:2px solid #3B5BDB; font-weight:800;}
.cal .dots {margin-top:3px; font-size:.7rem; line-height:1.1;}
.live-bar {display:flex; justify-content:space-between; align-items:center; padding:10px 16px; border-radius:14px;
  background:rgba(214,69,61,.1); border:1px solid rgba(214,69,61,.35); margin-bottom:10px;}
.dot-live {display:inline-block; width:9px; height:9px; border-radius:50%; background:#D6453D; margin-right:6px; animation:pulse 1.4s infinite;}
@keyframes pulse {0%{opacity:1} 50%{opacity:.25} 100%{opacity:1}}
.timer {font-size:3rem; font-weight:800; text-align:center; font-variant-numeric:tabular-nums;}
.big-code {font-size:3rem; font-weight:800; letter-spacing:.3em; text-align:center; font-variant-numeric:tabular-nums;}
.transcript {border-radius:14px; padding:10px 14px; background:rgba(128,128,128,.06); border:1px solid rgba(128,128,128,.22); max-height:300px; overflow-y:auto;}
.tline {padding:6px 0; border-bottom:1px dashed rgba(128,128,128,.2);}
.tline:last-child {border-bottom:none;}
.tts {font-variant-numeric:tabular-nums; opacity:.6; font-size:.8rem; margin-right:8px;}
.tr {opacity:.75; font-style:italic; font-size:.9rem; margin-top:2px;}
.profile {text-align:center; border-radius:18px; padding:16px 12px; border:1px solid rgba(128,128,128,.22); background:rgba(128,128,128,.05);}
.av {width:78px; height:78px; margin:0 auto 8px; border-radius:50%; display:flex; align-items:center; justify-content:center;
  font-size:2.6rem; background:#1E2A4A; border:3px solid #2F7D5B; overflow:hidden;}
.av img {width:100%; height:100%; object-fit:cover;}
.pn {font-weight:800; font-size:1.05rem;}
.pr {opacity:.75; font-size:.85rem;}
div[data-testid="stMetric"] {border:1px solid rgba(128,128,128,.22); border-radius:14px; padding:10px 14px; background:rgba(128,128,128,.04);}
.login-brand {font-size:2.6rem; font-weight:800; letter-spacing:-.03em;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def iframe_html(codigo: str, alto: int) -> None:
    """Inserta HTML con JavaScript (usa st.iframe en versiones nuevas de Streamlit)."""
    if hasattr(st, "iframe"):
        st.iframe(codigo, height=max(alto, 1))
    else:
        components.html(codigo, height=alto)


def html(markup: str) -> None:
    """Renderiza HTML sin sangrías ni líneas vacías (Markdown no lo confunde con código)."""
    st.markdown("\n".join(l.strip() for l in markup.splitlines() if l.strip()), unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════
# Utilidades de fecha y formato
# ═════════════════════════════════════════════════════════════════════
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]


def ahora() -> datetime:
    return datetime.now(TZ)


def hoy() -> date:
    return ahora().date()


def dt(ts: float) -> datetime:
    return datetime.fromtimestamp(ts, TZ)


def fmt_fecha(d: date) -> str:
    return d.strftime("%d-%m-%Y")


def fecha_larga(d: date) -> str:
    return f"{DIAS[d.weekday()]} {d.day} de {MESES[d.month - 1]} de {d.year}"


def mmss(seg: float) -> str:
    seg = max(0, int(seg))
    h, r = divmod(seg, 3600)
    m, s = divmod(r, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def pill_dias(n: int) -> str:
    if n < 0:
        return "<span class='pill p-gray'>Finalizada</span>"
    if n == 0:
        return "<span class='pill p-red'>¡Hoy!</span>"
    if n == 1:
        return "<span class='pill p-red'>Mañana</span>"
    clase = "p-red" if n <= 3 else ("p-amber" if n <= 7 else "p-blue")
    return f"<span class='pill {clase}'>En {n} días</span>"


def nuevo_id() -> str:
    return uuid.uuid4().hex[:10]


def hash_pw(pw: str, sal: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", pw.encode(), sal.encode(), 20_000).hex()


# ═════════════════════════════════════════════════════════════════════
# Datos semilla
# ═════════════════════════════════════════════════════════════════════
DOM_AL, DOM_DO = "@alumnos.unihub.cl", "@docentes.unihub.cl"
PASS_DEMO = "demo1234"
ASISTENCIA_MIN = 75  # % mínimo exigido (configurable por institución)
SESION_LARGA_DIAS, SESION_CORTA_HORAS = 30, 12

CARRERAS = ["Ingeniería en Informática", "Ingeniería en Mecánica Automotriz", "Analista Programador",
            "Ingeniería en Electricidad", "Ingeniería en Construcción"]

PROFESORES = [
    ("carolina.munoz", "Carolina Muñoz", "👩‍🏫"),
    ("rodrigo.vergara", "Rodrigo Vergara", "👨‍🏫"),
]
ESTUDIANTES = [
    ("benjamin.espinoza", "Benjamín Espinoza", "Ingeniería en Informática", "👨‍🎓", 4),
    ("juan.perez", "Juan Pérez", "Ingeniería en Mecánica Automotriz", "🧑‍🔧", 3),
    ("camila.torres", "Camila Torres", "Ingeniería en Informática", "👩‍💻", 4),
    ("matias.gonzalez", "Matías González", "Ingeniería en Informática", "🧑‍💻", 4),
    ("valentina.rojas", "Valentina Rojas", "Ingeniería en Informática", "👩‍🎓", 4),
    ("sebastian.munoz", "Sebastián Muñoz", "Ingeniería en Mecánica Automotriz", "🧑‍🔧", 3),
    ("isidora.perez", "Isidora Pérez", "Ingeniería en Informática", "👩‍🎓", 4),
    ("tomas.soto", "Tomás Soto", "Analista Programador", "🧑‍🎓", 2),
    ("catalina.diaz", "Catalina Díaz", "Ingeniería en Informática", "👩‍💻", 4),
    ("joaquin.contreras", "Joaquín Contreras", "Ingeniería en Informática", "🧑‍💻", 4),
    ("vicente.morales", "Vicente Morales", "Ingeniería en Mecánica Automotriz", "🧑‍🔧", 3),
    ("antonia.araya", "Antonia Araya", "Analista Programador", "👩‍🎓", 2),
]
MECANICA = {"juan.perez", "sebastian.munoz", "vicente.morales"}


def _unidades(*bloques):
    return [{"titulo": t, "semanas": s, "temas": temas, "materiales": mats} for t, s, temas, mats in bloques]


CURSOS_BASE = {
    "INF331": {
        "nombre": "Ingeniería de Software", "seccion": "001D", "prof": "rodrigo.vergara", "sala": "A-204",
        "modalidad": "Híbrida", "color": "#3B5BDB", "bloques": [(0, "10:15", "11:45"), (2, "10:15", "11:45")],
        "descripcion": "Procesos, diseño y calidad de software. Proyecto semestral en equipos usando Scrum.",
        "unidades": _unidades(
            ("Unidad 1: Procesos de desarrollo", "Semanas 1 a 4", ["Modelos de proceso", "Scrum y Kanban", "Historias de usuario"],
             [("📄", "Guía de Scrum.pdf"), ("🎞️", "Clase 3 grabada"), ("📝", "Plantilla de backlog.xlsx")]),
            ("Unidad 2: Diseño de software", "Semanas 5 a 10", ["Principios SOLID", "Patrones de diseño", "Diagramas UML"],
             [("📄", "Patrones GoF resumen.pdf"), ("🎞️", "Clase 14: Observer y Singleton"), ("🧪", "Taller UML.pdf")]),
            ("Unidad 3: Calidad y pruebas", "Semanas 11 a 18", ["Pruebas unitarias", "Integración continua", "Despliegue"],
             [("📄", "Guía pytest.pdf"), ("🔗", "Repositorio base CI")]),
        ),
    },
    "INF239": {
        "nombre": "Bases de Datos", "seccion": "002D", "prof": "carolina.munoz", "sala": "Lab B-12",
        "modalidad": "Presencial", "color": "#0E9AA7", "bloques": [(1, "13:00", "14:30"), (3, "13:00", "14:30")],
        "descripcion": "Modelado relacional, normalización, SQL avanzado y transacciones.",
        "unidades": _unidades(
            ("Unidad 1: Modelo relacional", "Semanas 1 a 5", ["Modelo E-R", "Álgebra relacional", "Claves"],
             [("📄", "Apunte modelo E-R.pdf"), ("🧪", "Guía de ejercicios 1.pdf")]),
            ("Unidad 2: Normalización", "Semanas 6 a 10", ["Dependencias funcionales", "1FN a 3FN", "FNBC"],
             [("📄", "Normalización paso a paso.pdf"), ("🎞️", "Clase 9 grabada")]),
            ("Unidad 3: SQL avanzado", "Semanas 11 a 18", ["JOINs y subconsultas", "Vistas e índices", "Transacciones"],
             [("📄", "Cheat sheet SQL.pdf"), ("🔗", "Base de datos de práctica")]),
        ),
    },
    "MAT023": {
        "nombre": "Cálculo III", "seccion": "005D", "prof": "rodrigo.vergara", "sala": "C-301",
        "modalidad": "Presencial", "color": "#E0A526", "bloques": [(0, "08:30", "10:00"), (3, "08:30", "10:00")],
        "descripcion": "Funciones de varias variables, derivadas parciales e integrales múltiples.",
        "unidades": _unidades(
            ("Unidad 1: Funciones de varias variables", "Semanas 1 a 6", ["Límites", "Continuidad", "Derivadas parciales"],
             [("📄", "Guía 1 resuelta.pdf")]),
            ("Unidad 2: Optimización", "Semanas 7 a 12", ["Gradiente", "Multiplicadores de Lagrange"],
             [("📄", "Guía 2.pdf"), ("🎞️", "Ayudantía Lagrange")]),
            ("Unidad 3: Integrales múltiples", "Semanas 13 a 18", ["Integrales dobles", "Cambio de variable"],
             [("📄", "Formulario certamen.pdf")]),
        ),
    },
    "INF256": {
        "nombre": "Redes de Computadores", "seccion": "001V", "prof": "carolina.munoz", "sala": "A-110 + online",
        "modalidad": "Híbrida", "color": "#2F7D5B", "bloques": [(2, "15:00", "16:30"), (4, "10:15", "11:45")],
        "descripcion": "Modelo OSI y TCP/IP, direccionamiento, enrutamiento y seguridad de redes.",
        "unidades": _unidades(
            ("Unidad 1: Fundamentos", "Semanas 1 a 5", ["Modelo OSI", "TCP/IP", "Medios físicos"],
             [("📄", "Resumen OSI.pdf"), ("🧪", "Lab Packet Tracer 1.pkt")]),
            ("Unidad 2: Direccionamiento", "Semanas 6 a 11", ["IPv4 y subnetting", "IPv6", "VLAN"],
             [("📄", "Ejercicios subnetting.pdf")]),
            ("Unidad 3: Enrutamiento y seguridad", "Semanas 12 a 18", ["OSPF", "Firewalls", "VPN"],
             [("📄", "Guía OSPF.pdf")]),
        ),
    },
}

QUIZ_NORMALIZACION = [
    ("¿Qué forma normal elimina los grupos repetitivos?", ["1FN", "2FN", "3FN", "FNBC"], 0),
    ("Una tabla está en 2FN si está en 1FN y además…",
     ["No tiene claves foráneas", "No hay dependencias parciales de la clave", "No tiene valores nulos", "Tiene una sola columna clave"], 1),
    ("¿Qué elimina la 3FN?", ["Dependencias transitivas", "Dependencias multivaluadas", "Claves candidatas", "Índices"], 0),
    ("¿Qué significa la dependencia funcional X → Y?",
     ["X determina unívocamente a Y", "Y determina a X", "X e Y son claves", "X e Y son independientes"], 0),
    ("La FNBC exige que todo determinante sea…", ["Una clave foránea", "Una superclave", "Un atributo no primo", "Un índice"], 1),
]

BANCO_PREGUNTAS = {
    "Patrones de diseño": ("¿Qué patrón notifica a varios objetos cuando cambia un estado?", ["Singleton", "Observer", "Factory", "Adapter"], 1),
    "Normalización": ("¿Qué forma normal elimina las dependencias transitivas?", ["1FN", "2FN", "3FN", "FNBC"], 2),
    "Redes": ("¿En qué capa del modelo OSI opera el protocolo IP?", ["Enlace", "Red", "Transporte", "Aplicación"], 1),
    "Cálculo": ("¿Qué vector apunta a la dirección de máximo crecimiento?", ["Normal", "Tangente", "Gradiente", "Binormal"], 2),
}

DEMO_FRASES = [
    ("es", "Hoy vamos a definir los requisitos del sistema de reservas del proyecto.", None),
    ("en", "The first requirement is user authentication with two-factor support.",
     "El primer requisito es la autenticación de usuarios con soporte de doble factor."),
    ("es", "La descripción 1 es bastante buena, pero primero va la descripción 2, que utiliza FFF.", None),
    ("en", "Remember that FFF stands for fast failure feedback in our testing pipeline.",
     "Recuerden que FFF significa retroalimentación rápida de fallos en nuestro pipeline de pruebas."),
    ("es", "Después de eso, la descripción 1 se apoya en lo que definió la descripción 2.", None),
    ("en", "For the next sprint, document at least two design patterns you applied.",
     "Para el próximo sprint, documenten al menos dos patrones de diseño que hayan aplicado."),
    ("es", "No olviden subir el diagrama de clases actualizado al repositorio.", None),
]
DEMO_EDT = """Requisitos del sistema de reservas
- Autenticación de usuarios
-- Doble factor (2FA)
- Descripción 2 (va primero)
-- Utiliza FFF (retroalimentación rápida de fallos)
- Descripción 1 (va después)
-- Se apoya en la Descripción 2
Entregables del sprint
- Documentar 2 patrones de diseño
- Diagrama de clases actualizado"""
DEMO_APUNTES = """### Apuntes generados por IA
- **Requisito principal:** autenticación de usuarios con doble factor (2FA).
- **Orden de implementación:** primero la Descripción 2 (usa FFF), después la Descripción 1, que depende de ella.
- **FFF:** retroalimentación rápida de fallos en el pipeline de pruebas.
- **Tarea:** documentar 2 patrones de diseño y subir el diagrama de clases actualizado."""

PROVEEDORES_IA = {
    "OpenAI": {"base": "https://api.openai.com/v1", "stt": "whisper-1", "llm": "gpt-4o-mini"},
    "Groq": {"base": "https://api.groq.com/openai/v1", "stt": "whisper-large-v3-turbo", "llm": "llama-3.3-70b-versatile"},
}

PAGINAS = {
    "inicio": "🏠 Inicio", "ramos": "📚 Ramos", "horario": "🗓️ Horario", "aula": "🎥 Aula en vivo",
    "evaluaciones": "📅 Evaluaciones", "asistencia": "✅ Asistencia", "chat": "💬 Chat",
    "interactiva": "🎮 Clase interactiva", "perfil": "👤 Perfil",
}


# ═════════════════════════════════════════════════════════════════════
# "Base de datos" compartida en memoria (todas las sesiones del servidor la ven en tiempo real)
# En producción: PostgreSQL + Redis/WebSockets.
# ═════════════════════════════════════════════════════════════════════
def _fechas_clase(code: str, desde: date, hasta: date) -> list:
    dias = {b[0] for b in CURSOS_BASE[code]["bloques"]}
    out, d = [], desde
    while d <= hasta:
        if d.weekday() in dias:
            out.append(d)
        d += timedelta(days=1)
    return out


@st.cache_resource
def get_db() -> dict:
    rng = random.Random(2026)
    H = hoy()
    now = time.time()
    db = {
        "lock": threading.RLock(), "usuarios": {}, "sesiones": {}, "cursos": {}, "inscritos": {},
        "mensajes": [], "evaluaciones": [], "notas": {}, "justificaciones": [], "asistencia": {},
        "vivo": {}, "bano": {}, "bano_log": [], "encuestas": {}, "sorpresas": {}, "puntos": {},
        "decimas": {}, "quizzes": {}, "apuntes": {}, "edt": {}, "anuncios": [],
        "config": {"bano_limite_min": 10},
    }
    # Usuarios
    for user, nombre, av in PROFESORES:
        email = user + DOM_DO
        sal = secrets.token_hex(8)
        db["usuarios"][email] = {"email": email, "nombre": nombre, "rol": "profesor", "avatar": av,
                                 "carrera": "Docente, Escuela de Informática y Telecomunicaciones",
                                 "sal": sal, "hash": hash_pw(PASS_DEMO, sal), "foto": None, "sonido": True, "anio": None}
    for user, nombre, carrera, av, anio in ESTUDIANTES:
        email = user + DOM_AL
        sal = secrets.token_hex(8)
        db["usuarios"][email] = {"email": email, "nombre": nombre, "rol": "estudiante", "avatar": av,
                                 "carrera": carrera, "sal": sal, "hash": hash_pw(PASS_DEMO, sal), "foto": None,
                                 "sonido": True, "anio": anio}
    # Cursos e inscripciones
    for code, c in CURSOS_BASE.items():
        cc = copy.deepcopy(c)
        cc["profesor"] = c["prof"] + DOM_DO
        db["cursos"][code] = cc
    for code in CURSOS_BASE:
        alumnos = []
        for user, *_ in ESTUDIANTES:
            mec = user in MECANICA
            if code == "MAT023" or (code == "INF256") or (not mec and code in ("INF331", "INF239")):
                alumnos.append(user + DOM_AL)
        db["inscritos"][code] = alumnos
    # Asistencia histórica (últimas 6 semanas)
    for code in CURSOS_BASE:
        for d in _fechas_clase(code, H - timedelta(days=42), H - timedelta(days=1)):
            reg = {}
            for email in db["inscritos"][code]:
                p = 0.93 if email.startswith("benjamin") else 0.8 + rng.random() * 0.17
                x = rng.random()
                reg[email] = "Presente" if x < p else ("Atrasado" if x < p + 0.04 else "Ausente")
            db["asistencia"][f"{code}|{d.isoformat()}"] = reg
    # Evaluaciones
    def ev(code, titulo, tipo, delta, hora, lugar, pond, contenidos, quiz=None):
        e = {"id": nuevo_id(), "curso": code, "titulo": titulo, "tipo": tipo, "fecha": H + timedelta(days=delta),
             "hora": hora, "lugar": lugar, "ponderacion": pond, "contenidos": contenidos, "creada": now - 86400 * 20, "quiz": quiz}
        db["evaluaciones"].append(e)
        return e
    pasadas = [
        ev("INF331", "Certamen 1", "Certamen", -20, "10:15", "Sala A-204", 25, "Unidad 1"),
        ev("INF239", "Prueba 1", "Prueba", -14, "13:00", "Lab B-12", 20, "Modelo relacional"),
        ev("MAT023", "Control 2", "Control", -10, "08:30", "Sala C-301", 15, "Derivadas parciales"),
        ev("INF256", "Certamen 1", "Certamen", -18, "15:00", "Híbrida", 25, "Modelo OSI y TCP/IP"),
    ]
    for e in pasadas:
        db["notas"][e["id"]] = {em: round(min(7.0, max(2.5, rng.gauss(5.4, 0.9))), 1) for em in db["inscritos"][e["curso"]]}
    ev_control = ev("MAT023", "Control 3", "Control", 2, "08:30", "Sala C-301", 20, "Optimización y Lagrange")
    qid = "Q-NORM"
    ev("INF239", "Quiz online: Normalización", "Quiz online", 4, "23:59", "En la plataforma", 10, "1FN a FNBC", quiz=qid)
    ev("INF331", "Entrega Sprint 2", "Proyecto", 7, "23:59", "Repositorio del equipo", 25, "Patrones de diseño aplicados")
    ev("INF256", "Certamen 2", "Certamen", 31, "15:00", "Sala A-110 + online", 30, "Direccionamiento, VLAN y OSPF")
    # Quiz online con intentos de ejemplo (incluye dos resoluciones sospechosamente rápidas)
    intentos = {}
    for email in db["inscritos"]["INF239"]:
        if email.startswith(("benjamin", "juan")):
            continue
        dur = rng.uniform(11, 27)
        punt = int(min(100, max(40, rng.gauss(72, 14))) // 20 * 20)
        if email.startswith("joaquin"):
            dur, punt = 2.1, 100
        if email.startswith("catalina"):
            dur, punt = 3.4, 100
        inicio = now - rng.uniform(3600, 86400)
        intentos[email] = {"inicio": inicio, "fin": inicio + dur * 60, "puntaje": punt}
    db["quizzes"][qid] = {"id": qid, "curso": "INF239", "titulo": "Quiz online: Normalización", "preguntas": QUIZ_NORMALIZACION,
                          "min_esperado": 8, "limite_min": 30, "intentos": intentos}
    # Justificación de ejemplo (Juan, hora médica el día del Control 3)
    db["justificaciones"].append({
        "id": nuevo_id(), "eval_id": ev_control["id"], "alumno": "juan.perez" + DOM_AL, "motivo": "Hora médica",
        "detalle": "Tengo hora con traumatología ese día a las 09:00 (control de rodilla). Adjunto el comprobante de la reserva.",
        "archivos": [{"nombre": "comprobante_hora_medica.txt", "tipo": "text/plain", "tamano": 120,
                      "sha256": hashlib.sha256(b"demo").hexdigest(),
                      "datos": "Comprobante de reserva (archivo de ejemplo)\nPaciente: Juan Pérez\nEspecialidad: Traumatología\n".encode()}],
        "estado": "pendiente", "comentario": "", "ts": now - 7200,
    })
    # Mensajes
    prof_is = "rodrigo.vergara" + DOM_DO
    seed_msgs = [
        ("curso:INF331", prof_is, "¡Buenos días! Hoy cerramos patrones de diseño. La clase queda grabada.", 5400),
        ("curso:INF331", "camila.torres" + DOM_AL, "Profe, ¿el Sprint 2 se entrega el viernes o el lunes?", 5000),
        ("curso:INF331", prof_is, "Se entrega el día que aparece en Evaluaciones, a las 23:59 👍", 4800),
        ("curso:INF239", "carolina.munoz" + DOM_DO, "Ya está publicado el quiz online de normalización. Tienen 30 minutos.", 3600),
        ("curso:MAT023", "juan.perez" + DOM_AL, "¿La ayudantía de Lagrange queda grabada?", 3000),
        (canal_dm("benjamin.espinoza" + DOM_AL, prof_is), prof_is, "Benjamín, revisé tu avance del proyecto, va muy bien.", 2000),
    ]
    for canal, autor, texto, hace in seed_msgs:
        db["mensajes"].append({"id": nuevo_id(), "canal": canal, "autor": autor, "texto": texto, "ts": now - hace})
    db["anuncios"].append({"id": nuevo_id(), "curso": "INF256", "autor": "carolina.munoz" + DOM_DO,
                           "texto": "El Certamen 2 incluye VLAN y OSPF. Revisen la guía de la Unidad 3.", "ts": now - 86400})
    return db


def canal_dm(a: str, b: str) -> str:
    return "dm:" + "|".join(sorted([a, b]))


DB = get_db()
LOCK = DB["lock"]


# ═════════════════════════════════════════════════════════════════════
# Acceso a datos
# ═════════════════════════════════════════════════════════════════════
def usuario(email: str | None = None) -> dict:
    return DB["usuarios"][email or st.session_state.user]


def es_profe(u: dict | None = None) -> bool:
    return (u or usuario())["rol"] == "profesor"


def curso(code: str) -> dict:
    return DB["cursos"][code]


def mis_cursos(u: dict | None = None) -> list:
    u = u or usuario()
    if es_profe(u):
        return [c for c, d in DB["cursos"].items() if d["profesor"] == u["email"]]
    return [c for c, al in DB["inscritos"].items() if u["email"] in al]


def nombre(email: str) -> str:
    u = DB["usuarios"].get(email)
    return u["nombre"] if u else email


def evaluacion(eid: str) -> dict | None:
    return next((e for e in DB["evaluaciones"] if e["id"] == eid), None)


def clase_en_vivo(code: str) -> dict | None:
    lv = DB["vivo"].get(code)
    return lv if lv and lv["activa"] else None


def asistencia_alumno(email: str, code: str) -> tuple:
    total = asistio = 0
    for k, reg in DB["asistencia"].items():
        if k.startswith(code + "|") and email in reg:
            total += 1
            asistio += reg[email] in ("Presente", "Atrasado", "Justificado")
    return (round(100 * asistio / total) if total else 100), asistio, total


def asistencia_general(email: str) -> int:
    vals = [asistencia_alumno(email, c)[0] for c in mis_cursos(usuario(email))]
    return round(sum(vals) / len(vals)) if vals else 100


def avatar_html(u: dict, size: int = 78) -> str:
    if u.get("foto"):
        inner = f"<img src='data:image/png;base64,{u['foto']}'>"
    else:
        inner = u["avatar"]
    return f"<div class='av' style='width:{size}px;height:{size}px;font-size:{size * 0.033:.1f}rem'>{inner}</div>"


def ir_a(pagina: str, code: str | None = None, canal: str | None = None) -> None:
    st.session_state.nav = PAGINAS[pagina]
    if code:
        st.session_state.curso_activo = code
        for k in [k for k in st.session_state if str(k).startswith("selcurso_")]:
            del st.session_state[k]
    if canal:
        st.session_state.chat_canal = canal


def selector_curso(key: str, label: str = "Ramo") -> str | None:
    cursos = mis_cursos()
    if not cursos:
        st.info("No tienes ramos asociados todavía.")
        return None
    actual = st.session_state.get("curso_activo")
    if actual not in cursos:
        en_vivo = [c for c in cursos if clase_en_vivo(c)]
        actual = en_vivo[0] if en_vivo else cursos[0]
    val = st.selectbox(label, cursos, index=cursos.index(actual), key=f"selcurso_{key}",
                       format_func=lambda c: f"{c}  {curso(c)['nombre']}")
    st.session_state.curso_activo = val
    return val


# ═════════════════════════════════════════════════════════════════════
# IA con la API key del propio usuario (OpenAI o Groq, ambos con API compatible)
# ═════════════════════════════════════════════════════════════════════
def ia_cfg() -> dict:
    return st.session_state.setdefault("ia", {"proveedor": "Demo"})


def ia_activa() -> bool:
    c = ia_cfg()
    return c["proveedor"] != "Demo" and bool(c.get("key"))


class ErrorIA(Exception):
    pass


def _ia_post(ruta: str, **kw) -> dict:
    c = ia_cfg()
    try:
        r = requests.post(f"{c['base']}{ruta}", headers={"Authorization": f"Bearer {c['key']}"}, timeout=90, **kw)
    except requests.RequestException as e:
        raise ErrorIA(f"No se pudo conectar con {c['proveedor']}: {e}") from e
    if r.status_code == 401:
        raise ErrorIA("La API key fue rechazada. Revísala en Perfil > Inteligencia artificial.")
    if r.status_code == 429:
        raise ErrorIA("Tu cuenta de IA alcanzó el límite de uso o no tiene saldo.")
    if r.status_code >= 400:
        raise ErrorIA(f"Error {r.status_code} del proveedor: {r.text[:200]}")
    return r.json()


def ia_transcribir(audio: bytes, nombre_archivo: str = "clip.wav") -> str:
    c = ia_cfg()
    data = _ia_post("/audio/transcriptions", files={"file": (nombre_archivo, audio, "audio/wav")}, data={"model": c["stt"]})
    return data.get("text", "").strip()


def ia_chat(sistema: str, usuario_txt: str, json_mode: bool = False) -> str:
    c = ia_cfg()
    body = {"model": c["llm"], "temperature": 0.2,
            "messages": [{"role": "system", "content": sistema}, {"role": "user", "content": usuario_txt}]}
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    data = _ia_post("/chat/completions", json=body)
    return data["choices"][0]["message"]["content"].strip()


def ia_detectar_y_traducir(texto: str) -> tuple:
    out = ia_chat(
        "Detectas el idioma de un fragmento dicho por un profesor. Si no está en español, lo traduces al español "
        "de forma natural y fiel. Responde SOLO JSON: {\"idioma\": \"código ISO\", \"es\": \"traducción o null\"}.",
        texto, json_mode=True)
    try:
        d = json.loads(out)
        idioma = (d.get("idioma") or "es").lower()[:2]
        return idioma, (d.get("es") if idioma != "es" else None)
    except json.JSONDecodeError:
        return "es", None


def texto_transcripcion(code: str) -> str:
    lv = DB["vivo"].get(code) or {}
    return "\n".join(t["traduccion"] or t["original"] for t in lv.get("transcripcion", []))


# ═════════════════════════════════════════════════════════════════════
# Sesión persistente (token en la URL + almacén del servidor)
# En producción: cookie httpOnly con JWT/refresh token.
# ═════════════════════════════════════════════════════════════════════
def crear_sesion(email: str, recordar: bool) -> None:
    tok = secrets.token_urlsafe(24)
    exp = time.time() + (SESION_LARGA_DIAS * 86400 if recordar else SESION_CORTA_HORAS * 3600)
    with LOCK:
        DB["sesiones"][tok] = {"email": email, "expira": exp, "creada": time.time()}
    st.session_state.user = email
    st.session_state.token = tok
    st.session_state.t0 = time.time()
    st.query_params["sesion"] = tok


def restaurar_sesion() -> None:
    if "user" in st.session_state:
        return
    tok = st.query_params.get("sesion")
    s = DB["sesiones"].get(tok) if tok else None
    if s and s["expira"] > time.time() and s["email"] in DB["usuarios"]:
        st.session_state.user = s["email"]
        st.session_state.token = tok
        st.session_state.t0 = time.time()


def cerrar_sesion(todas: bool = False) -> None:
    email = st.session_state.get("user")
    with LOCK:
        if todas:
            for t in [t for t, s in DB["sesiones"].items() if s["email"] == email]:
                del DB["sesiones"][t]
        else:
            DB["sesiones"].pop(st.session_state.get("token"), None)
    st.query_params.clear()
    for k in list(st.session_state.keys()):
        del st.session_state[k]


# ═════════════════════════════════════════════════════════════════════
# Notificaciones en tiempo real (toasts + sonido)
# ═════════════════════════════════════════════════════════════════════
def sonar(tipo: str = "aviso") -> None:
    if not usuario().get("sonido", True):
        return
    notas = {"aviso": [880, 660, 880], "fin": [784, 659, 523, 392], "info": [740, 988]}[tipo]
    iframe_html(f"""<!-- {time.time()} --><script>
    (function(){{try{{const C=new (window.AudioContext||window.webkitAudioContext)();let t=C.currentTime+0.05;
    {json.dumps(notas)}.forEach(function(f){{const o=C.createOscillator(),g=C.createGain();o.type='sine';o.frequency.value=f;
    g.gain.setValueAtTime(0.0001,t);g.gain.exponentialRampToValueAtTime(0.35,t+0.03);g.gain.exponentialRampToValueAtTime(0.0001,t+0.4);
    o.connect(g);g.connect(C.destination);o.start(t);o.stop(t+0.45);t+=0.45;}});}}catch(e){{}}}})();</script>""", 0)


@st.fragment(run_every=3)
def vigilante() -> None:
    """Revisa cada 3 s si hay eventos nuevos para este usuario y los muestra como notificación."""
    if "user" not in st.session_state:
        return
    u = usuario()
    t0 = st.session_state.get("t0", time.time())
    vistos = st.session_state.setdefault("vistos", set())
    now = time.time()
    sonido = None

    def notificar(clave, texto, icono, dur=10, tipo=None):
        nonlocal sonido
        if clave in vistos:
            return
        vistos.add(clave)
        st.toast(texto, icon=icono, duration=dur)
        if tipo:
            sonido = tipo

    profe = es_profe(u)
    cursos = mis_cursos(u)
    for code in cursos:
        nom = curso(code)["nombre"]
        lv = DB["vivo"].get(code)
        if lv:
            if lv["activa"]:
                restante = lv["inicio"] + lv["duracion"] * 60 - now
                if restante <= 0:
                    with LOCK:
                        lv["activa"] = False
                        lv["fin"] = now
                elif profe and restante <= 600:
                    notificar(f"aviso10:{lv['id']}:{lv['duracion']}", f"Profesor, la clase de {nom} termina en 10 minutos",
                              "⏰", 10, "aviso")
                if not profe and lv["inicio"] > t0 - 5:
                    notificar(f"inicio:{lv['id']}", f"{nom}: el profesor inició la clase en vivo", "🎥", 8, "info")
            if not lv["activa"] and lv.get("fin") and lv["fin"] > t0 - 5:
                texto = f"Clase de {nom} finalizada" if profe else f"La clase de {nom} ha finalizado"
                notificar(f"fin:{lv['id']}", texto, "🔔", 10, "fin")
        if not profe:
            enc = DB["encuestas"].get(code)
            if enc and enc["abierta"] and enc["creada"] > t0 - 5:
                notificar(f"enc:{enc['id']}", f"Nueva votación en vivo en {nom}", "🟣", 8, "info")
            sor = DB["sorpresas"].get(code)
            if sor and sor["enviada"] > t0 - 5:
                notificar(f"sor:{sor['id']}", f"¡Evaluación sorpresa en {nom}! Ve a Clase interactiva", "⚡", 10, "aviso")
    for e in list(DB["evaluaciones"]):
        if e["curso"] in cursos and e["creada"] > t0 - 5 and not profe:
            notificar(f"ev:{e['id']}", f"Nueva evaluación: {e['titulo']} ({curso(e['curso'])['nombre']}) el {fmt_fecha(e['fecha'])}",
                      "📅", 10, "info")
    for a in list(DB["anuncios"]):
        if a["curso"] in cursos and a["ts"] > t0 - 5 and a["autor"] != u["email"]:
            notificar(f"an:{a['id']}", f"Anuncio en {curso(a['curso'])['nombre']}: {a['texto'][:60]}", "📢", 8)
    for j in list(DB["justificaciones"]):
        ev = evaluacion(j["eval_id"])
        if not ev:
            continue
        if profe and ev["curso"] in cursos and j["ts"] > t0 - 5:
            notificar(f"jn:{j['id']}", f"{nombre(j['alumno'])} justificó su inasistencia a {ev['titulo']}", "🩺", 8)
        if not profe and j["alumno"] == u["email"] and j.get("resuelta", 0) > t0 - 5:
            txt = "aprobada ✅" if j["estado"] == "aprobada" else "rechazada"
            notificar(f"jr:{j['id']}:{j['estado']}", f"Tu justificación para {ev['titulo']} fue {txt}", "🩺", 8)
    for m in DB["mensajes"][-30:]:
        if m["ts"] > t0 - 5 and m["autor"] != u["email"] and m["canal"].startswith("dm:") and u["email"] in m["canal"]:
            notificar(f"msg:{m['id']}", f"{nombre(m['autor'])}: {m['texto'][:60]}", "💬", 6)
    if profe:
        limite = DB["config"]["bano_limite_min"] * 60
        for email, b in list(DB["bano"].items()):
            if b["curso"] in cursos and now - b["inicio"] > limite:
                notificar(f"bano:{email}:{b['inicio']}", f"{nombre(email)} lleva más de {DB['config']['bano_limite_min']} min fuera de la sala",
                          "🚻", 10, "aviso")
    if sonido:
        sonar(sonido)


# ═════════════════════════════════════════════════════════════════════
# Componentes reutilizables
# ═════════════════════════════════════════════════════════════════════
def sala_video(sala: str, nombre_usuario: str, alto: int = 470) -> None:
    """Sala de videollamada real con Jitsi Meet (código abierto). En producción: Jitsi propio, LiveKit o JaaS."""
    iframe_html(f"""
<div id="meet" style="height:{alto}px;border-radius:16px;overflow:hidden;background:#000"></div>
<script src="https://meet.jit.si/external_api.js"></script>
<script>
new JitsiMeetExternalAPI("meet.jit.si", {{
  roomName: {json.dumps(sala)}, parentNode: document.querySelector('#meet'), width: "100%", height: {alto}, lang: "es",
  userInfo: {{displayName: {json.dumps(nombre_usuario)}}},
  configOverwrite: {{prejoinPageEnabled: false, startWithAudioMuted: true, disableDeepLinking: true}}
}});
</script>""", alto + 6)


def parsear_edt(texto: str) -> list:
    nodos = []
    for linea in texto.splitlines():
        s = linea.strip()
        if not s:
            continue
        nivel = len(s) - len(s.lstrip("-"))
        etiqueta = s.lstrip("-").strip()
        if etiqueta:
            if nodos:
                nivel = min(nivel, nodos[-1][0] + 1)
            else:
                nivel = 0
            nodos.append((nivel, etiqueta))
    return nodos


def edt_a_texto(nodos: list) -> str:
    return "\n".join(("-" * n + " " if n else "") + t for n, t in nodos)


def edt_dot(titulo: str, nodos: list) -> str:
    esc = lambda s: s.replace('"', "'")
    out = ["digraph EDT {", 'graph [rankdir=TB, bgcolor="transparent", nodesep=0.25, ranksep=0.45];',
           'node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=10, color="#3B5BDB", fillcolor="#EEF2FF", fontcolor="#1E2A4A"];',
           'edge [color="#94A3B8", arrowhead=none];',
           f'root [label="{esc(titulo)}", fillcolor="#1E2A4A", fontcolor="white", color="#1E2A4A", fontsize=11];']
    pila, contadores = [("root", -1)], []
    paleta = ["#EEF2FF", "#F1F7F4", "#FFF7E6", "#FDEDEC"]
    bordes = ["#3B5BDB", "#2F7D5B", "#E0A526", "#D6453D"]
    for i, (nivel, texto) in enumerate(nodos):
        while len(contadores) > nivel + 1:
            contadores.pop()
        while len(contadores) < nivel + 1:
            contadores.append(0)
        contadores[nivel] += 1
        numero = ".".join(str(x) for x in contadores[: nivel + 1])
        while pila and pila[-1][1] >= nivel:
            pila.pop()
        padre = pila[-1][0] if pila else "root"
        nid = f"n{i}"
        out.append(f'{nid} [label="{numero}  {esc(texto)}", fillcolor="{paleta[nivel % 4]}", color="{bordes[nivel % 4]}"];')
        out.append(f"{padre} -> {nid};")
        pila.append((nid, nivel))
    out.append("}")
    return "\n".join(out)


def mostrar_error_ia(e: Exception) -> None:
    st.error(str(e))


# ═════════════════════════════════════════════════════════════════════
# Login
# ═════════════════════════════════════════════════════════════════════
def pantalla_login() -> None:
    _, centro, _ = st.columns([1, 1.25, 1])
    with centro:
        st.write("")
        html("<div class='login-brand'>🎓 UniHub</div>")
        st.caption("Ramos, clases en vivo, evaluaciones, asistencia y chat en un solo lugar.")
        tab_in, tab_reg = st.tabs(["Iniciar sesión", "Crear cuenta de estudiante"])
        with tab_in:
            with st.form("login"):
                email = st.text_input("Correo institucional", placeholder="nombre.apellido@alumnos.unihub.cl")
                pw = st.text_input("Contraseña", type="password")
                recordar = st.checkbox("Mantener la sesión iniciada en este dispositivo (30 días)", value=True)
                entrar = st.form_submit_button("Iniciar sesión", type="primary")
            if entrar:
                u = DB["usuarios"].get(email.strip().lower())
                if not u or hash_pw(pw, u["sal"]) != u["hash"]:
                    st.error("Correo o contraseña incorrectos. Revisa los datos e inténtalo de nuevo.")
                else:
                    crear_sesion(u["email"], recordar)
                    st.rerun()
            st.markdown("**Entrar rápido con una cuenta demo**")
            demos = [("Benjamín (Informática)", "benjamin.espinoza" + DOM_AL), ("Juan (Mecánica)", "juan.perez" + DOM_AL),
                     ("Prof. Carolina", "carolina.munoz" + DOM_DO), ("Prof. Rodrigo", "rodrigo.vergara" + DOM_DO)]
            cols = st.columns(2)
            for i, (lab, em) in enumerate(demos):
                if cols[i % 2].button(lab, key=f"demo_{i}"):
                    crear_sesion(em, True)
                    st.rerun()
            st.caption("Contraseña de todas las cuentas demo: demo1234. Para ver el tiempo real, abre otra ventana "
                       "en incógnito con una cuenta distinta.")
        with tab_reg:
            with st.form("registro"):
                nom = st.text_input("Nombre completo")
                em = st.text_input("Correo institucional", placeholder=f"nombre.apellido{DOM_AL}")
                car = st.selectbox("Carrera", CARRERAS)
                anio = st.number_input("Año de la carrera", 1, 6, 1)
                ramos = st.multiselect("Ramos inscritos", list(DB["cursos"]),
                                       format_func=lambda c: f"{c}  {curso(c)['nombre']}")
                pw1 = st.text_input("Contraseña (mínimo 8 caracteres)", type="password")
                crear = st.form_submit_button("Crear cuenta", type="primary")
            if crear:
                em = em.strip().lower()
                if len(nom.strip()) < 3 or "@" not in em:
                    st.error("Escribe tu nombre completo y un correo válido.")
                elif em in DB["usuarios"]:
                    st.error("Ese correo ya tiene una cuenta. Inicia sesión.")
                elif len(pw1) < 8:
                    st.error("La contraseña debe tener al menos 8 caracteres.")
                else:
                    sal = secrets.token_hex(8)
                    with LOCK:
                        DB["usuarios"][em] = {"email": em, "nombre": nom.strip(), "rol": "estudiante", "avatar": "🧑‍🎓",
                                              "carrera": car, "sal": sal, "hash": hash_pw(pw1, sal), "foto": None,
                                              "sonido": True, "anio": int(anio)}
                        for c in ramos:
                            DB["inscritos"][c].append(em)
                    crear_sesion(em, True)
                    st.rerun()


# ═════════════════════════════════════════════════════════════════════
# Barra lateral
# ═════════════════════════════════════════════════════════════════════
@st.fragment(run_every=1)
def cronometro_bano_propio() -> None:
    b = DB["bano"].get(st.session_state.user)
    if not b:
        return
    seg = time.time() - b["inicio"]
    color = "#2F7D5B" if seg < 300 else ("#E0A526" if seg < 600 else "#D6453D")
    html(f"<div class='timer' style='font-size:2rem;color:{color}'>{mmss(seg)}</div>")


def curso_actual_para_bano(u: dict) -> str | None:
    cursos = mis_cursos(u)
    for c in cursos:
        if clase_en_vivo(c):
            return c
    hh = ahora().strftime("%H:%M")
    for c in cursos:
        for d, ini, fin in curso(c)["bloques"]:
            if d == hoy().weekday() and ini <= hh <= fin:
                return c
    return cursos[0] if cursos else None


def barra_lateral() -> None:
    u = usuario()
    with st.sidebar:
        rol = "Docente" if es_profe(u) else f"Estudiante, {u['carrera']}"
        extra = u["carrera"].replace("Docente, ", "") if es_profe(u) else f"{u.get('anio') or 1}.º año"
        html(f"""
        <div class="profile">{avatar_html(u)}
        <div class="pn">{u['nombre']}</div><div class="pr">{rol}</div>
        <div class="muted">{extra}</div>
        <div style="margin-top:8px"><span class="pill p-green">● En línea</span></div></div>""")
        st.write("")
        if es_profe(u):
            cursos = mis_cursos(u)
            alumnos = {a for c in cursos for a in DB["inscritos"][c]}
            pend = sum(1 for j in DB["justificaciones"] if j["estado"] == "pendiente"
                       and (evaluacion(j["eval_id"]) or {}).get("curso") in cursos)
            c1, c2 = st.columns(2)
            c1.metric("Alumnos", len(alumnos))
            c2.metric("Por revisar", pend)
        else:
            gen = asistencia_general(u["email"])
            c1, c2 = st.columns(2)
            c1.metric("Asistencia", f"{gen}%")
            c2.metric("Mínimo", f"{ASISTENCIA_MIN}%")
            st.progress(gen / 100, text="Sobre el mínimo ✅" if gen >= ASISTENCIA_MIN else "Bajo el mínimo ⚠️")

        if "nav" not in st.session_state:
            st.session_state.nav = PAGINAS.get(st.query_params.get("p", "inicio"), PAGINAS["inicio"])
        st.radio("Navegación", list(PAGINAS.values()), key="nav", label_visibility="collapsed")

        if not es_profe(u):
            st.divider()
            b = DB["bano"].get(u["email"])
            if not b:
                if st.button("🚻 Voy al baño"):
                    code = curso_actual_para_bano(u)
                    with LOCK:
                        DB["bano"][u["email"]] = {"inicio": time.time(), "curso": code}
                    st.rerun()
            else:
                st.caption("🚻 Fuera de la sala. Tu profesor ve este tiempo.")
                cronometro_bano_propio()
                if st.button("✅ Ya volví"):
                    with LOCK:
                        b = DB["bano"].pop(u["email"], None)
                        if b:
                            DB["bano_log"].append({"alumno": u["email"], "curso": b["curso"], "inicio": b["inicio"],
                                                   "duracion": time.time() - b["inicio"]})
                    st.rerun()
        st.divider()
        if st.button("Cerrar sesión"):
            cerrar_sesion()
            st.rerun()


# ═════════════════════════════════════════════════════════════════════
# Páginas
# ═════════════════════════════════════════════════════════════════════
def pagina_inicio() -> None:
    u = usuario()
    cursos = mis_cursos(u)
    html(f"""<div class="hero"><div class="t">Hola, {u['nombre'].split()[0]} 👋</div>
    <div class="s">Hoy es {fecha_larga(hoy())}</div></div>""")

    for c in cursos:
        lv = clase_en_vivo(c)
        if lv:
            with st.container(border=True):
                a, b = st.columns([4, 1], vertical_alignment="center")
                a.markdown(f"🔴 **{curso(c)['nombre']} está en vivo ahora.** Tema: {lv['tema']}")
                b.button("Entrar al aula", key=f"go_{c}", type="primary", on_click=ir_a, args=("aula", c))

    proximas = sorted([e for e in DB["evaluaciones"] if e["curso"] in cursos and e["fecha"] >= hoy()], key=lambda e: e["fecha"])
    m = st.columns(4)
    if es_profe(u):
        alumnos = {a for c in cursos for a in DB["inscritos"][c]}
        pend = [j for j in DB["justificaciones"] if j["estado"] == "pendiente" and (evaluacion(j["eval_id"]) or {}).get("curso") in cursos]
        m[0].metric("Cursos a cargo", len(cursos))
        m[1].metric("Alumnos", len(alumnos))
        m[2].metric("Justificaciones por revisar", len(pend))
        m[3].metric("Evaluaciones próximas", len(proximas))
    else:
        clases_hoy = sum(1 for c in cursos for d, *_ in curso(c)["bloques"] if d == hoy().weekday())
        notas = [DB["notas"][e][u["email"]] for e in DB["notas"] if u["email"] in DB["notas"][e]]
        m[0].metric("Clases hoy", clases_hoy)
        m[1].metric("Próxima evaluación", f"en {(proximas[0]['fecha'] - hoy()).days} días" if proximas else "Ninguna")
        m[2].metric("Asistencia general", f"{asistencia_general(u['email'])}%")
        m[3].metric("Promedio de notas", f"{sum(notas) / len(notas):.1f}".replace(".", ",") if notas else "-")

    izq, der = st.columns([1.3, 1], gap="large")
    with izq:
        st.markdown("#### 🗓️ Clases de hoy")
        bloques = sorted([(ini, fin, c) for c in cursos for d, ini, fin in curso(c)["bloques"] if d == hoy().weekday()])
        if not bloques:
            st.caption("Hoy no tienes clases. Aprovecha de adelantar materia o revisar tus evaluaciones.")
        hh = ahora().strftime("%H:%M")
        partes = []
        for ini, fin, c in bloques:
            cc = curso(c)
            estado = "now" if ini <= hh <= fin or clase_en_vivo(c) else ("done" if fin < hh else "next")
            badge = {"now": "<span class='pill p-red'>● En curso</span>", "done": "<span class='pill p-green'>Finalizada</span>",
                     "next": "<span class='pill p-blue'>Próxima</span>"}[estado]
            partes.append(f"""<div class="tl {'tl-now' if estado == 'now' else 'tl-done' if estado == 'done' else ''}">
            <div class="tl-h">{ini} – {fin}</div><div class="tl-b" style="--c:{cc['color']}">
            <div class="row"><b>{cc['nombre']}</b>{badge}</div><div class="muted">📍 {cc['sala']}, {cc['modalidad'].lower()}</div></div></div>""")
        html("".join(partes))
        anuncios = sorted([a for a in DB["anuncios"] if a["curso"] in cursos], key=lambda a: -a["ts"])[:3]
        if anuncios:
            st.markdown("#### 📢 Anuncios")
            for a in anuncios:
                html(f"""<div class="card accent" style="--c:{curso(a['curso'])['color']}"><div class="row"><b>{curso(a['curso'])['nombre']}</b>
                <span class="muted">{dt(a['ts']).strftime('%d-%m %H:%M')}</span></div><div>{a['texto']}</div>
                <div class="muted">{nombre(a['autor'])}</div></div>""")
    with der:
        st.markdown("#### 📅 Próximas evaluaciones")
        if not proximas:
            st.caption("No hay evaluaciones programadas.")
        for e in proximas[:5]:
            cc = curso(e["curso"])
            html(f"""<div class="card accent" style="--c:{cc['color']}">
            <div class="row"><span class="ctitle">{e['titulo']}</span>{pill_dias((e['fecha'] - hoy()).days)}</div>
            <div class="muted">{cc['nombre']}</div>
            <div class="row"><span>🗓️ {fmt_fecha(e['fecha'])}, {e['hora']}</span><span class="muted">Pondera {e['ponderacion']}%</span></div></div>""")
        st.button("Ver calendario completo", on_click=ir_a, args=("evaluaciones",))


def pagina_ramos() -> None:
    u = usuario()
    st.markdown("## 📚 " + ("Mis cursos" if es_profe(u) else "Mis ramos"))
    code = selector_curso("ramos")
    if not code:
        return
    cc = curso(code)
    alumnos = DB["inscritos"][code]
    html(f"""<div class="card accent" style="--c:{cc['color']}"><div class="row"><div>
    <div class="muted">{code}, sección {cc['seccion']}</div><div style="font-size:1.4rem;font-weight:800">{cc['nombre']}</div>
    <div class="muted">👤 {nombre(cc['profesor'])} &nbsp; 📍 {cc['sala']} &nbsp; 🧭 {cc['modalidad']} &nbsp; 👥 {len(alumnos)} estudiantes</div></div>
    {'<span class="pill p-red">● En vivo</span>' if clase_en_vivo(code) else ''}</div></div>""")

    t_info, t_cont, t_eval, t_part, t_anun = st.tabs(["ℹ️ Información", "📂 Contenido", "📝 Evaluaciones y notas", "👥 Participantes", "📢 Anuncios"])
    with t_info:
        a, b = st.columns([1.4, 1], gap="large")
        with a:
            st.markdown("##### Descripción")
            st.write(cc["descripcion"])
            st.markdown("##### Horario")
            for d, ini, fin in cc["bloques"]:
                st.markdown(f"- {DIAS[d].capitalize()} de {ini} a {fin}, {cc['sala']}")
        with b:
            st.markdown("##### Avance del semestre")
            total_sem = 18
            semana = min(total_sem, 11)
            st.progress(semana / total_sem, text=f"Semana {semana} de {total_sem}")
            if not es_profe(u):
                pct, asis, tot = asistencia_alumno(u["email"], code)
                st.metric("Tu asistencia en este ramo", f"{pct}%", f"{asis} de {tot} clases", delta_color="off")
            st.button("💬 Abrir chat del ramo", on_click=ir_a, args=("chat", None, f"curso:{code}"))
    with t_cont:
        for i, un in enumerate(cc["unidades"]):
            with st.expander(f"{un['titulo']}  ({un['semanas']})", expanded=i == 1):
                st.markdown("**Temas:** " + ", ".join(un["temas"]))
                for j, (ic, mat) in enumerate(un["materiales"]):
                    c1, c2 = st.columns([4, 1], vertical_alignment="center")
                    c1.markdown(f"{ic} {mat}")
                    c2.download_button("Descargar", f"Material de ejemplo: {mat}\n{cc['nombre']}".encode(),
                                       file_name=mat.replace(" ", "_") + ".txt", key=f"mat_{code}_{i}_{j}")
        if es_profe(u):
            with st.form(f"subir_mat_{code}"):
                st.markdown("**Publicar material**")
                un_sel = st.selectbox("Unidad", [x["titulo"] for x in cc["unidades"]])
                arch = st.file_uploader("Archivo")
                if st.form_submit_button("Publicar material") and arch:
                    with LOCK:
                        next(x for x in cc["unidades"] if x["titulo"] == un_sel)["materiales"].append(("📎", arch.name))
                    st.toast("Material publicado. Ya lo ven tus estudiantes.", icon="📎")
                    st.rerun()
    with t_eval:
        evs = sorted([e for e in DB["evaluaciones"] if e["curso"] == code], key=lambda e: e["fecha"])
        filas = []
        for e in evs:
            fila = {"Evaluación": e["titulo"], "Tipo": e["tipo"], "Fecha": fmt_fecha(e["fecha"]), "Pondera": f"{e['ponderacion']}%"}
            notas = DB["notas"].get(e["id"], {})
            if es_profe(u):
                fila["Promedio curso"] = round(sum(notas.values()) / len(notas), 1) if notas else None
            else:
                fila["Tu nota"] = notas.get(u["email"])
            filas.append(fila)
        st.dataframe(pd.DataFrame(filas), hide_index=True)
        if not es_profe(u):
            st.caption("Las notas van de 1,0 a 7,0. Aprobación con 4,0.")
    with t_part:
        prof = usuario(cc["profesor"])
        st.markdown(f"**Docente:** {prof['avatar']} {prof['nombre']}")
        df = pd.DataFrame([{"": usuario(a)["avatar"], "Estudiante": usuario(a)["nombre"], "Carrera": usuario(a)["carrera"],
                            "Año": usuario(a).get("anio"), "Asistencia": asistencia_alumno(a, code)[0]} for a in alumnos])
        resumen = df["Carrera"].value_counts()
        st.caption("Composición del curso: " + ", ".join(f"{n} de {c}" for c, n in resumen.items()))
        st.dataframe(df, hide_index=True, column_config={
            "Asistencia": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%d%%")})
    with t_anun:
        if es_profe(u):
            with st.form(f"anuncio_{code}", clear_on_submit=True):
                txt = st.text_area("Nuevo anuncio para el curso")
                if st.form_submit_button("Publicar anuncio", type="primary") and txt.strip():
                    with LOCK:
                        DB["anuncios"].append({"id": nuevo_id(), "curso": code, "autor": u["email"], "texto": txt.strip(), "ts": time.time()})
                    st.toast("Anuncio publicado", icon="📢")
        ans = sorted([a for a in DB["anuncios"] if a["curso"] == code], key=lambda a: -a["ts"])
        if not ans:
            st.caption("Aún no hay anuncios en este ramo.")
        for a in ans:
            html(f"""<div class="card"><div class="row"><b>{nombre(a['autor'])}</b>
            <span class="muted">{dt(a['ts']).strftime('%d-%m-%Y %H:%M')}</span></div>{a['texto']}</div>""")


def pagina_horario() -> None:
    st.markdown("## 🗓️ Horario semanal")
    cursos = mis_cursos()
    lunes = hoy() - timedelta(days=hoy().weekday())
    st.caption(f"Semana del {fmt_fecha(lunes)} al {fmt_fecha(lunes + timedelta(days=4))}")
    evs_semana = {e["fecha"]: e for e in DB["evaluaciones"] if e["curso"] in cursos and lunes <= e["fecha"] <= lunes + timedelta(days=4)}
    cols = []
    for d in range(5):
        fecha = lunes + timedelta(days=d)
        bloques = sorted([(ini, fin, c) for c in cursos for dd, ini, fin in curso(c)["bloques"] if dd == d])
        items = "".join(
            f"<div class='blk' style='background:{curso(c)['color']}'><b>{ini} – {fin}</b><br>{curso(c)['nombre']}"
            f"<br><span style='opacity:.85'>📍 {curso(c)['sala']}</span></div>" for ini, fin, c in bloques)
        if fecha in evs_semana:
            e = evs_semana[fecha]
            items += f"<div class='card' style='padding:8px 10px'>📝 <b>{e['titulo']}</b><br><span class='muted'>{curso(e['curso'])['nombre']}</span></div>"
        if not items:
            items = "<div class='muted'>Sin clases</div>"
        cols.append(f"<div class='wday {'today' if fecha == hoy() else ''}'><div class='dh'>{DIAS[d].capitalize()} {fecha.day}</div>{items}</div>")
    html(f"<div class='week'>{''.join(cols)}</div>")


@st.fragment(run_every=1)
def barra_clase_vivo(code: str) -> None:
    lv = DB["vivo"].get(code)
    if not lv or not lv["activa"]:
        st.info("La clase terminó.")
        return
    restante = lv["inicio"] + lv["duracion"] * 60 - time.time()
    color = "#D6453D" if restante <= 600 else "inherit"
    html(f"""<div class="live-bar"><div><span class="dot-live"></span><b>EN VIVO</b> &nbsp; {curso(code)['nombre']}: {lv['tema']}</div>
    <div>⏱️ Transcurrido {mmss(time.time() - lv['inicio'])} &nbsp; <b style="color:{color}">Quedan {mmss(restante)}</b></div></div>""")


@st.fragment(run_every=2)
def panel_transcripcion(code: str) -> None:
    lv = DB["vivo"].get(code) or {}
    lineas = lv.get("transcripcion", [])
    mostrar_trad = st.session_state.get("mostrar_trad", True)
    if not lineas:
        html("<div class='transcript'><span class='muted'>Aún no hay transcripción. Cuando alguien grabe un fragmento, aparecerá aquí para todos.</span></div>")
        return
    partes = []
    for t in lineas[-12:]:
        bandera = "🇬🇧" if t["idioma"] == "en" else ("🇪🇸" if t["idioma"] == "es" else "🌐")
        trad = f"<div class='tr'>🇪🇸 {t['traduccion']}</div>" if (t["traduccion"] and mostrar_trad) else ""
        partes.append(f"<div class='tline'><span class='tts'>{dt(t['ts']).strftime('%H:%M:%S')}</span>{bandera} {t['original']}{trad}</div>")
    html(f"<div class='transcript'>{''.join(reversed(partes))}</div>")


def agregar_transcripcion(code: str, original: str, idioma: str, traduccion: str | None) -> None:
    with LOCK:
        DB["vivo"][code].setdefault("transcripcion", []).append(
            {"ts": time.time(), "original": original, "idioma": idioma, "traduccion": traduccion, "autor": st.session_state.user})


def herramienta_apuntes(code: str) -> None:
    email = st.session_state.user
    clave = f"{email}|{code}"
    k = f"apuntes_{code}"
    if k not in st.session_state:
        st.session_state[k] = DB["apuntes"].get(clave, "")

    def guardar():
        with LOCK:
            DB["apuntes"][clave] = st.session_state[k]

    st.text_area("Apuntes (se guardan solos en tu cuenta)", key=k, height=260, on_change=guardar,
                 placeholder="Escribe aquí lo importante de la clase…")
    a, b = st.columns(2)
    if a.button("🤖 Apuntes desde la transcripción", key=f"ia_ap_{code}"):
        trans = texto_transcripcion(code)
        if not trans:
            st.warning("Todavía no hay transcripción en esta clase para resumir.")
        else:
            try:
                if ia_activa():
                    with st.spinner("Generando apuntes con tu IA…"):
                        res = ia_chat("Eres un asistente que toma apuntes de clases universitarias en español. Resume la "
                                      "transcripción en viñetas claras con los conceptos clave, definiciones, el orden de "
                                      "las cosas que indicó el profesor y las tareas. Usa Markdown.", trans)
                else:
                    res = DEMO_APUNTES
                st.session_state[k] = (st.session_state[k] + "\n\n" + res).strip()
                guardar()
                st.rerun()
            except ErrorIA as e:
                mostrar_error_ia(e)
    b.download_button("⬇️ Descargar", st.session_state[k] or " ", file_name=f"apuntes_{code}_{fmt_fecha(hoy())}.md", key=f"dl_ap_{code}")
    if not ia_activa():
        st.caption("Modo demo: configura tu API key en Perfil para usar tu propia IA.")


def herramienta_edt(code: str) -> None:
    email = st.session_state.user
    clave = f"{email}|{code}"
    data = DB["edt"].setdefault(clave, {"titulo": f"Clase de {curso(code)['nombre']}", "texto": ""})
    kt, kx = f"edt_tit_{code}", f"edt_txt_{code}"
    if kt not in st.session_state:
        st.session_state[kt] = data["titulo"]
        st.session_state[kx] = data["texto"]

    def guardar():
        with LOCK:
            data["titulo"] = st.session_state[kt]
            data["texto"] = st.session_state[kx]

    st.text_input("Requisito o tema principal", key=kt, on_change=guardar)
    nodos = parsear_edt(st.session_state[kx])

    with st.form(f"edt_add_{code}", clear_on_submit=True, border=False):
        c1, c2 = st.columns([1.2, 1])
        nuevo = c1.text_input("Nuevo punto clave", placeholder="Ej: Descripción 2 usa FFF")
        opciones = ["(Nivel principal)"] + [f"{'  ' * n}{t}" for n, t in nodos]
        padre = c2.selectbox("Va debajo de", range(len(opciones)), format_func=lambda i: opciones[i])
        if st.form_submit_button("➕ Agregar al diagrama") and nuevo.strip():
            if padre == 0:
                nodos.append((0, nuevo.strip()))
            else:
                p = padre - 1
                j = p + 1
                while j < len(nodos) and nodos[j][0] > nodos[p][0]:
                    j += 1
                nodos.insert(j, (nodos[p][0] + 1, nuevo.strip()))
            st.session_state[kx] = edt_a_texto(nodos)
            guardar()
            st.rerun()

    if nodos:
        st.graphviz_chart(edt_dot(st.session_state[kt], nodos))
    else:
        st.caption("Agrega puntos clave o genera el diagrama desde lo que dijo el profesor.")

    a, b = st.columns(2)
    if a.button("🤖 Generar desde la clase", key=f"edt_ia_{code}"):
        trans = texto_transcripcion(code)
        if not trans:
            st.warning("Todavía no hay transcripción en esta clase.")
        else:
            try:
                if ia_activa():
                    with st.spinner("Estructurando la EDT…"):
                        res = ia_chat(
                            "Conviertes lo que dijo un profesor en una EDT (estructura de desglose) jerárquica en español. "
                            "Respeta el orden que indique el profesor (si dice 'primero X', X va antes). Devuelve SOLO "
                            "líneas de texto: nivel principal sin guion, subniveles con '-', '--' o '---' al inicio. "
                            "Frases cortas, sin numeración ni explicaciones.", trans)
                else:
                    res = DEMO_EDT
                nuevos = parsear_edt(res)
                st.session_state[kx] = edt_a_texto(nodos + nuevos)
                guardar()
                st.rerun()
            except ErrorIA as e:
                mostrar_error_ia(e)
    with b.popover("✏️ Editar texto"):
        st.caption("Una idea por línea. Usa -, -- o --- para bajar de nivel.")
        st.text_area("Estructura", key=kx, height=220, on_change=guardar, label_visibility="collapsed")


def grabador_transcripcion(code: str) -> None:
    st.toggle("Mostrar traducción al español", value=True, key="mostrar_trad")
    with st.expander("🎙️ Transcribir desde mi micrófono", expanded=es_profe()):
        st.caption("Graba fragmentos de 15 a 30 segundos. Se transcriben con tu propia API key y todos los "
                   "participantes ven el texto (y su traducción si el profesor habla en otro idioma).")
        audio = st.audio_input("Grabar fragmento", key=f"audio_{code}")
        if audio is not None:
            datos = audio.getvalue()
            huella = hashlib.md5(datos).hexdigest()
            if st.session_state.get(f"audio_ok_{code}") != huella:
                st.session_state[f"audio_ok_{code}"] = huella
                if not ia_activa():
                    st.warning("Para transcribir audio real necesitas configurar tu API key en Perfil. "
                               "Mientras tanto puedes usar el botón de simulación.")
                else:
                    try:
                        with st.spinner("Transcribiendo y traduciendo…"):
                            texto = ia_transcribir(datos)
                            if texto:
                                idioma, trad = ia_detectar_y_traducir(texto)
                                agregar_transcripcion(code, texto, idioma, trad)
                        st.toast("Fragmento transcrito", icon="📝")
                    except ErrorIA as e:
                        mostrar_error_ia(e)
        if st.button("➕ Simular frase del profesor (demo)", key=f"sim_tr_{code}"):
            lv = DB["vivo"][code]
            i = len(lv.get("transcripcion", [])) % len(DEMO_FRASES)
            idioma, orig, trad = DEMO_FRASES[i]
            agregar_transcripcion(code, orig, idioma, trad)
            st.rerun()


@st.fragment(run_every=3)
def panel_participantes_vivo(code: str) -> None:
    lv = DB["vivo"].get(code) or {}
    reg = DB["asistencia"].get(f"{code}|{hoy().isoformat()}", {})
    presentes = [a for a, s in reg.items() if s in ("Presente", "Atrasado")]
    fuera = [a for a, b in DB["bano"].items() if b["curso"] == code]
    st.metric("Marcaron asistencia hoy", f"{len(presentes)} / {len(DB['inscritos'][code])}")
    if lv.get("codigo") and lv["codigo"]["expira"] > time.time():
        st.caption(f"Código vigente por {mmss(lv['codigo']['expira'] - time.time())}")
    for a in presentes[:20]:
        ub = usuario(a)
        extra = " 🚻" if a in fuera else ""
        st.markdown(f"{ub['avatar']} {ub['nombre']}{extra}  \n<span class='muted'>{ub['carrera']}</span>", unsafe_allow_html=True)


def marcar_con_codigo(code: str, valor: str) -> bool:
    lv = DB["vivo"].get(code)
    if not lv or not lv.get("codigo") or lv["codigo"]["expira"] < time.time() or valor.strip() != lv["codigo"]["valor"]:
        return False
    with LOCK:
        reg = DB["asistencia"].setdefault(f"{code}|{hoy().isoformat()}", {})
        tarde = time.time() - lv["inicio"] > 15 * 60
        reg[st.session_state.user] = "Atrasado" if tarde else "Presente"
    return True


def pagina_aula() -> None:
    u = usuario()
    st.markdown("## 🎥 Aula en vivo")
    code = selector_curso("aula")
    if not code:
        return
    lv = clase_en_vivo(code)

    if not lv:
        if es_profe(u):
            st.markdown("Abre la sala para que los estudiantes online vean y escuchen la clase igual que los presenciales.")
            with st.form("iniciar_clase"):
                tema = st.text_input("Tema de la clase", value="Requisitos del proyecto y patrones de diseño")
                duraciones = {"90 minutos": 90, "45 minutos": 45, "Demo: 11 minutos (aviso al minuto 1)": 11, "Demo: 2 minutos": 2}
                dur = st.selectbox("Duración", list(duraciones))
                if st.form_submit_button("🔴 Iniciar clase en vivo", type="primary"):
                    with LOCK:
                        DB["vivo"][code] = {"id": nuevo_id(), "activa": True, "tema": tema, "inicio": time.time(),
                                            "duracion": duraciones[dur], "sala": f"UniHub-{code}-{secrets.token_hex(4)}",
                                            "transcripcion": [], "codigo": None, "fin": None}
                    st.toast("Clase iniciada. Tus estudiantes recibieron la notificación.", icon="🎥")
                    st.rerun()
        else:
            st.info("Este ramo no tiene una clase en vivo en este momento. Te avisaremos cuando el profesor la inicie.")
            prox = sorted([(d, ini) for d, ini, _ in curso(code)["bloques"]], key=lambda x: ((x[0] - hoy().weekday()) % 7, x[1]))
            if prox:
                st.caption(f"Próxima clase: {DIAS[prox[0][0]]} a las {prox[0][1]}")
        return

    barra_clase_vivo(code)

    if es_profe(u):
        a, b, c, d = st.columns(4)
        if a.button("⏹️ Finalizar clase", type="primary"):
            with LOCK:
                lv["activa"] = False
                lv["fin"] = time.time()
            st.rerun()
        if b.button("➕ Extender 10 min"):
            with LOCK:
                lv["duracion"] += 10
            st.toast("Clase extendida 10 minutos", icon="⏱️")
        if c.button("🔢 Código de asistencia"):
            with LOCK:
                lv["codigo"] = {"valor": f"{random.randint(0, 9999):04d}", "expira": time.time() + 600}
        d.link_button("↗️ Abrir sala en pestaña nueva", f"https://meet.jit.si/{lv['sala']}")
        if lv.get("codigo") and lv["codigo"]["expira"] > time.time():
            html(f"<div class='card'><div class='muted' style='text-align:center'>Código de asistencia (proyéctalo en la sala)</div>"
                 f"<div class='big-code'>{lv['codigo']['valor']}</div></div>")
    else:
        a, b, c = st.columns([1.3, 1, 1.2], vertical_alignment="bottom")
        reg = DB["asistencia"].get(f"{code}|{hoy().isoformat()}", {})
        if reg.get(u["email"]) in ("Presente", "Atrasado"):
            a.success("Asistencia registrada ✅")
        else:
            with a.form("cod_asis", border=False):
                x1, x2 = st.columns([1.3, 1], vertical_alignment="bottom")
                val = x1.text_input("Código de asistencia", max_chars=4, placeholder="0000")
                if x2.form_submit_button("Marcar"):
                    if marcar_con_codigo(code, val):
                        st.toast("Asistencia registrada", icon="✅")
                        st.rerun()
                    else:
                        st.error("Código incorrecto o vencido. Pídeselo al profesor.")
        if b.button("✋ Levantar la mano"):
            with LOCK:
                DB["mensajes"].append({"id": nuevo_id(), "canal": f"curso:{code}", "autor": u["email"],
                                       "texto": "✋ levantó la mano", "ts": time.time()})
            st.toast("El profesor verá tu mano levantada en el chat", icon="✋")
        c.link_button("↗️ Abrir sala en pestaña nueva", f"https://meet.jit.si/{lv['sala']}")

    izq, der = st.columns([1.75, 1], gap="large")
    with izq:
        ver = st.toggle("🎥 Mostrar video de la sala", key=f"ver_video_{code}",
                        help="Cargar el video solo cuando lo necesitas hace que el resto de la app vaya más rápido.")
        if ver:
            sala_video(lv["sala"], u["nombre"])
            st.caption("Video con Jitsi Meet. El servidor público limita las salas incrustadas a 5 minutos; "
                       "usa “Abrir sala en pestaña nueva” para clases completas. En producción se usa un servidor propio.")
        else:
            html(f"""<div class="card" style="text-align:center;padding:40px">
            <div style="font-size:3rem">{usuario(curso(code)['profesor'])['avatar']}</div>
            <b>{nombre(curso(code)['profesor'])}</b> está transmitiendo<br><span class="muted">Activa “Mostrar video” para unirte con cámara y audio</span></div>""")
        st.markdown("##### 🤖 Transcripción y traducción en tiempo real")
        panel_transcripcion(code)
        grabador_transcripcion(code)
    with der:
        opciones = ["📝 Apuntes", "🧩 Diagrama EDT", "👥 Participantes"]
        herramienta = st.segmented_control("Herramientas", opciones, default=opciones[0], key=f"herr_{code}",
                                           label_visibility="collapsed")
        if herramienta == "📝 Apuntes":
            herramienta_apuntes(code)
        elif herramienta == "🧩 Diagrama EDT":
            herramienta_edt(code)
        elif herramienta == "👥 Participantes":
            panel_participantes_vivo(code)


# ─────────────────────────── Evaluaciones ───────────────────────────
@st.dialog("🩺 Justificar inasistencia", width="large")
def dialogo_justificar(eid: str) -> None:
    e = evaluacion(eid)
    cc = curso(e["curso"])
    st.markdown(f"**{e['titulo']}**, {cc['nombre']}  \n🗓️ {fmt_fecha(e['fecha'])} a las {e['hora']}, {e['lugar']}")
    motivo = st.selectbox("Motivo", ["Hora médica", "Licencia médica", "Trámite legal o judicial",
                                     "Fallecimiento de un familiar", "Representación institucional", "Otro (con respaldo)"])
    detalle = st.text_area("Explica tu situación", max_chars=600,
                           placeholder="Ej: Tengo hora con traumatología ese día a las 09:00…")
    archivos = st.file_uploader("Documentos de respaldo (obligatorio): certificado, licencia, comprobante de hora",
                                type=["pdf", "jpg", "jpeg", "png"], accept_multiple_files=True)
    declaro = st.checkbox("Declaro que la información y los documentos adjuntos son verídicos. Entiendo que "
                          "adjuntar documentos falsos puede tener sanciones según el reglamento académico.")
    if st.button("Enviar justificación", type="primary"):
        errores = []
        if len(detalle.strip()) < 15:
            errores.append("Explica tu situación con al menos 15 caracteres.")
        if not archivos:
            errores.append("Adjunta al menos un documento de respaldo.")
        if any(a.size > 5 * 1024 * 1024 for a in archivos or []):
            errores.append("Cada archivo debe pesar menos de 5 MB.")
        if not declaro:
            errores.append("Debes aceptar la declaración de veracidad.")
        if errores:
            for x in errores:
                st.error(x)
            return
        adj = [{"nombre": a.name, "tipo": a.type, "tamano": a.size, "datos": a.getvalue(),
                "sha256": hashlib.sha256(a.getvalue()).hexdigest()} for a in archivos]
        with LOCK:
            DB["justificaciones"] = [j for j in DB["justificaciones"]
                                     if not (j["eval_id"] == eid and j["alumno"] == st.session_state.user and j["estado"] == "rechazada")]
            DB["justificaciones"].append({"id": nuevo_id(), "eval_id": eid, "alumno": st.session_state.user, "motivo": motivo,
                                          "detalle": detalle.strip(), "archivos": adj, "estado": "pendiente",
                                          "comentario": "", "ts": time.time()})
        st.toast("Justificación enviada. Tu profesor fue notificado.", icon="🩺")
        st.rerun()


def mi_justificacion(eid: str, email: str) -> dict | None:
    js = [j for j in DB["justificaciones"] if j["eval_id"] == eid and j["alumno"] == email]
    return js[-1] if js else None


def calendario_mes(cursos: list, email: str | None) -> None:
    ref = st.session_state.setdefault("cal_ref", hoy().replace(day=1))
    a, b, c = st.columns([1, 3, 1], vertical_alignment="center")
    if a.button("◀", key="cal_prev"):
        st.session_state.cal_ref = (ref - timedelta(days=1)).replace(day=1)
        st.rerun()
    b.markdown(f"<div style='text-align:center;font-weight:800;font-size:1.1rem'>{MESES[ref.month - 1].capitalize()} {ref.year}</div>",
               unsafe_allow_html=True)
    if c.button("▶", key="cal_next"):
        st.session_state.cal_ref = (ref + timedelta(days=32)).replace(day=1)
        st.rerun()
    por_dia = {}
    for e in DB["evaluaciones"]:
        if e["curso"] in cursos:
            por_dia.setdefault(e["fecha"], []).append(e)
    celdas = [f"<div class='h'>{d}</div>" for d in ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]]
    for semana in calendar.Calendar(0).monthdatescalendar(ref.year, ref.month):
        for d in semana:
            cls = ["d"] + (["o"] if d.month != ref.month else []) + (["t"] if d == hoy() else [])
            dots = ""
            for e in por_dia.get(d, []):
                jj = mi_justificacion(e["id"], email) if email else None
                marca = " 🩺" if jj else ""
                dots += f"<div style='color:{curso(e['curso'])['color']};font-weight:700'>● {e['titulo'][:14]}{marca}</div>"
            celdas.append(f"<div class='{' '.join(cls)}' title=''>{d.day}<div class='dots'>{dots}</div></div>")
    html(f"<div class='cal'>{''.join(celdas)}</div>")


def tarjeta_evaluacion(e: dict, email: str | None) -> None:
    cc = curso(e["curso"])
    j = mi_justificacion(e["id"], email) if email else None
    estado_j = ""
    if j:
        estado_j = {"pendiente": "<span class='pill p-amber'>🩺 Justificación pendiente de revisión</span>",
                    "aprobada": "<span class='pill p-green'>🩺 Justificación aprobada</span>",
                    "rechazada": "<span class='pill p-red'>🩺 Justificación rechazada</span>"}[j["estado"]]
    html(f"""<div class="card accent" style="--c:{cc['color']}">
    <div class="row"><span class="muted">{e['tipo']}, {cc['nombre']}</span>{pill_dias((e['fecha'] - hoy()).days)}</div>
    <div class="ctitle">{e['titulo']}</div>
    <div>🗓️ <b>{fmt_fecha(e['fecha'])}</b> a las {e['hora']} &nbsp; 📍 {e['lugar']} &nbsp; <span class="muted">Pondera {e['ponderacion']}%</span></div>
    <div class="muted">Contenidos: {e['contenidos']}</div>{('<div style="margin-top:6px">' + estado_j + '</div>') if estado_j else ''}</div>""")
    if j and j["estado"] == "rechazada" and j.get("comentario"):
        st.caption(f"Comentario del profesor: {j['comentario']}")


def pagina_evaluaciones() -> None:
    u = usuario()
    cursos = mis_cursos(u)
    st.markdown("## 📅 Evaluaciones")
    if es_profe(u):
        _evaluaciones_profe(u, cursos)
    else:
        _evaluaciones_alumno(u, cursos)


def _evaluaciones_alumno(u: dict, cursos: list) -> None:
    t_cal, t_online, t_notas = st.tabs(["📅 Calendario", "🧪 Evaluaciones online", "📈 Mis notas"])
    with t_cal:
        izq, der = st.columns([1.2, 1], gap="large")
        with izq:
            calendario_mes(cursos, u["email"])
            st.caption("🩺 indica que enviaste una justificación para esa fecha.")
        with der:
            st.markdown("##### Próximas evaluaciones")
            prox = sorted([e for e in DB["evaluaciones"] if e["curso"] in cursos and e["fecha"] >= hoy()], key=lambda e: e["fecha"])
            if not prox:
                st.caption("No tienes evaluaciones programadas.")
            for e in prox:
                tarjeta_evaluacion(e, u["email"])
                j = mi_justificacion(e["id"], u["email"])
                if not j or j["estado"] == "rechazada":
                    if st.button("🩺 No podré asistir: justificar", key=f"just_{e['id']}"):
                        dialogo_justificar(e["id"])
    with t_online:
        quizzes = [q for q in DB["quizzes"].values() if q["curso"] in cursos]
        if not quizzes:
            st.caption("No hay evaluaciones online disponibles.")
        for q in quizzes:
            rendir_quiz(q, u)
    with t_notas:
        filas = []
        for e in sorted(DB["evaluaciones"], key=lambda e: e["fecha"]):
            if e["curso"] in cursos and e["id"] in DB["notas"] and u["email"] in DB["notas"][e["id"]]:
                filas.append({"Ramo": curso(e["curso"])["nombre"], "Evaluación": e["titulo"], "Fecha": fmt_fecha(e["fecha"]),
                              "Pondera": f"{e['ponderacion']}%", "Nota": DB["notas"][e["id"]][u["email"]]})
        if filas:
            df = pd.DataFrame(filas)
            st.dataframe(df, hide_index=True, column_config={"Nota": st.column_config.NumberColumn(format="%.1f")})
            st.bar_chart(df, x="Evaluación", y="Nota", color="#3B5BDB", height=240)
        else:
            st.caption("Aún no tienes notas publicadas.")


@st.fragment(run_every=1)
def reloj_quiz(inicio: float, limite_min: int) -> None:
    trans = time.time() - inicio
    rest = limite_min * 60 - trans
    st.progress(max(0.0, min(1.0, rest / (limite_min * 60))), text=f"⏱️ Tiempo transcurrido {mmss(trans)}, quedan {mmss(rest)}")


def rendir_quiz(q: dict, u: dict) -> None:
    with st.container(border=True):
        st.markdown(f"**{q['titulo']}**, {curso(q['curso'])['nombre']}")
        st.caption(f"{len(q['preguntas'])} preguntas, tiempo máximo {q['limite_min']} minutos. El tiempo empieza al presionar Comenzar.")
        it = q["intentos"].get(u["email"])
        if it and it.get("fin"):
            st.success(f"Entregado. Puntaje: {it['puntaje']}%. Tiempo: {mmss(it['fin'] - it['inicio'])}.")
            return
        if not it:
            if st.button("▶️ Comenzar", key=f"start_{q['id']}", type="primary"):
                with LOCK:
                    q["intentos"][u["email"]] = {"inicio": time.time(), "fin": None, "puntaje": None}
                st.rerun()
            return
        reloj_quiz(it["inicio"], q["limite_min"])
        with st.form(f"quiz_{q['id']}"):
            resp = [st.radio(f"{i + 1}. {p}", ops, index=None, key=f"q_{q['id']}_{i}") for i, (p, ops, _) in enumerate(q["preguntas"])]
            if st.form_submit_button("Entregar", type="primary"):
                ok = sum(1 for r, (_, ops, c) in zip(resp, q["preguntas"]) if r is not None and ops.index(r) == c)
                with LOCK:
                    it["fin"] = time.time()
                    it["puntaje"] = round(100 * ok / len(q["preguntas"]))
                st.rerun()


def _evaluaciones_profe(u: dict, cursos: list) -> None:
    t_cal, t_just, t_online = st.tabs(["📅 Calendario y publicación", "🩺 Justificaciones", "🧪 Monitoreo evaluaciones online"])
    with t_cal:
        izq, der = st.columns([1.2, 1], gap="large")
        with izq:
            calendario_mes(cursos, None)
        with der:
            st.markdown("##### Publicar evaluación")
            st.caption("Todos los estudiantes del ramo ven la fecha de inmediato y reciben una notificación.")
            with st.form("nueva_eval", clear_on_submit=True):
                code = st.selectbox("Ramo", cursos, format_func=lambda c: f"{c}  {curso(c)['nombre']}")
                titulo = st.text_input("Título", placeholder="Ej: Certamen 3")
                c1, c2 = st.columns(2)
                tipo = c1.selectbox("Tipo", ["Prueba", "Certamen", "Control", "Quiz online", "Proyecto", "Presentación"])
                fecha = c2.date_input("Fecha", value=hoy() + timedelta(days=14), min_value=hoy(), format="DD-MM-YYYY")
                c3, c4 = st.columns(2)
                hora = c3.time_input("Hora", value=datetime.strptime("10:15", "%H:%M").time())
                pond = c4.number_input("Ponderación (%)", 1, 100, 20)
                lugar = st.text_input("Lugar o modalidad", placeholder="Ej: Sala A-204 o En la plataforma")
                cont = st.text_area("Contenidos", height=80)
                if st.form_submit_button("📣 Publicar evaluación", type="primary"):
                    if not titulo.strip():
                        st.error("Escribe un título para la evaluación.")
                    else:
                        with LOCK:
                            DB["evaluaciones"].append({"id": nuevo_id(), "curso": code, "titulo": titulo.strip(), "tipo": tipo,
                                                       "fecha": fecha, "hora": hora.strftime("%H:%M"), "lugar": lugar or "Por confirmar",
                                                       "ponderacion": int(pond), "contenidos": cont or "Por confirmar",
                                                       "creada": time.time(), "quiz": None})
                        st.toast(f"Evaluación publicada para {len(DB['inscritos'][code])} estudiantes", icon="📣")
        st.markdown("##### Evaluaciones programadas")
        prox = sorted([e for e in DB["evaluaciones"] if e["curso"] in cursos and e["fecha"] >= hoy()], key=lambda e: e["fecha"])
        cols = st.columns(2)
        for i, e in enumerate(prox):
            with cols[i % 2]:
                tarjeta_evaluacion(e, None)
                js = [j for j in DB["justificaciones"] if j["eval_id"] == e["id"]]
                if js:
                    st.caption("🩺 Con justificación: " + ", ".join(f"{nombre(j['alumno'])} ({j['estado']})" for j in js))
    with t_just:
        filtro = st.segmented_control("Estado", ["Pendientes", "Aprobadas", "Rechazadas", "Todas"], default="Pendientes")
        mapa = {"Pendientes": "pendiente", "Aprobadas": "aprobada", "Rechazadas": "rechazada"}
        js = [j for j in DB["justificaciones"] if (evaluacion(j["eval_id"]) or {}).get("curso") in cursos
              and (filtro in (None, "Todas") or j["estado"] == mapa[filtro])]
        js.sort(key=lambda j: evaluacion(j["eval_id"])["fecha"])
        if not js:
            st.caption("No hay justificaciones en esta categoría.")
        for j in js:
            e = evaluacion(j["eval_id"])
            al = usuario(j["alumno"])
            with st.container(border=True):
                a, b = st.columns([3, 1])
                a.markdown(f"**{al['avatar']} {al['nombre']}** ({al['carrera']})  \n"
                           f"{e['titulo']}, {curso(e['curso'])['nombre']}: **{fmt_fecha(e['fecha'])}** a las {e['hora']}")
                estado = {"pendiente": "⏳ Pendiente", "aprobada": "✅ Aprobada", "rechazada": "❌ Rechazada"}[j["estado"]]
                b.markdown(f"**{estado}**")
                st.markdown(f"**Motivo:** {j['motivo']}  \n{j['detalle']}")
                st.caption(f"Enviada el {dt(j['ts']).strftime('%d-%m-%Y %H:%M')}")
                for k, arch in enumerate(j["archivos"]):
                    x1, x2 = st.columns([3, 1], vertical_alignment="center")
                    x1.caption(f"📎 {arch['nombre']} ({arch['tamano'] / 1024:.0f} KB). Huella SHA-256: {arch['sha256'][:16]}…")
                    x2.download_button("Ver documento", arch["datos"], file_name=arch["nombre"], key=f"dl_{j['id']}_{k}")
                    if arch["tipo"] and arch["tipo"].startswith("image/"):
                        st.image(arch["datos"], width=260)
                if j["estado"] == "pendiente":
                    com = st.text_input("Comentario para el estudiante (opcional)", key=f"com_{j['id']}")
                    c1, c2, c3 = st.columns(3)
                    for col, (lab, est) in zip((c1, c2), (("✅ Aprobar", "aprobada"), ("❌ Rechazar", "rechazada"))):
                        if col.button(lab, key=f"{est}_{j['id']}"):
                            with LOCK:
                                j["estado"], j["comentario"], j["resuelta"] = est, com, time.time()
                                if est == "aprobada":
                                    DB["asistencia"].setdefault(f"{e['curso']}|{e['fecha'].isoformat()}", {})[j["alumno"]] = "Justificado"
                            st.rerun()
                    c3.button("💬 Escribirle", key=f"chat_{j['id']}", on_click=ir_a,
                              args=("chat", None, canal_dm(u["email"], j["alumno"])))
    with t_online:
        quizzes = [q for q in DB["quizzes"].values() if q["curso"] in cursos]
        if not quizzes:
            st.caption("No tienes evaluaciones online activas. Los quizzes online que publiques aparecerán aquí.")
        for q in quizzes:
            monitoreo_quiz(q)


def monitoreo_quiz(q: dict) -> None:
    st.markdown(f"##### {q['titulo']}, {curso(q['curso'])['nombre']}")
    a, b = st.columns([1, 2])
    q["min_esperado"] = a.number_input("Tiempo mínimo razonable (min)", 1, 60, q["min_esperado"], key=f"minesp_{q['id']}",
                                       help="Quien termine antes de este tiempo se marca como sospechoso.")
    filas = []
    for email in DB["inscritos"][q["curso"]]:
        it = q["intentos"].get(email)
        al = usuario(email)
        if not it:
            filas.append({"Estudiante": al["nombre"], "Carrera": al["carrera"], "Estado": "No ha comenzado", "Minutos": None, "Puntaje": None})
        elif not it.get("fin"):
            filas.append({"Estudiante": al["nombre"], "Carrera": al["carrera"], "Estado": "En curso",
                          "Minutos": round((time.time() - it["inicio"]) / 60, 1), "Puntaje": None})
        else:
            filas.append({"Estudiante": al["nombre"], "Carrera": al["carrera"], "Estado": "Entregado",
                          "Minutos": round((it["fin"] - it["inicio"]) / 60, 1), "Puntaje": it["puntaje"]})
    df = pd.DataFrame(filas)
    entregados = df[df["Estado"] == "Entregado"]
    mediana = entregados["Minutos"].median() if not entregados.empty else 0

    def alerta(r):
        if r["Estado"] != "Entregado":
            return ""
        if r["Minutos"] < q["min_esperado"]:
            return "🚨 Demasiado rápido"
        if r["Minutos"] < mediana * 0.5:
            return "⚠️ Revisar"
        return "✅ Normal"

    df["Alerta"] = df.apply(alerta, axis=1)
    sosp = int((df["Alerta"] == "🚨 Demasiado rápido").sum())
    k = st.columns(4)
    k[0].metric("Entregados", f"{len(entregados)} / {len(df)}")
    k[1].metric("Mediana", f"{mediana:.1f} min")
    k[2].metric("Más rápido", f"{entregados['Minutos'].min():.1f} min" if not entregados.empty else "-")
    k[3].metric("Sospechosos", sosp)

    def color(r):
        if r["Alerta"].startswith("🚨"):
            return ["background-color: rgba(214,69,61,.18)"] * len(r)
        if r["Alerta"].startswith("⚠️"):
            return ["background-color: rgba(224,165,38,.18)"] * len(r)
        return [""] * len(r)

    st.dataframe(df.sort_values("Minutos", na_position="last").style.apply(color, axis=1), hide_index=True, column_config={
        "Minutos": st.column_config.NumberColumn(format="%.1f min"),
        "Puntaje": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%d%%")})
    if sosp:
        st.warning("Puntaje alto con un tiempo muy por debajo del resto suele indicar uso de IA, respuestas compartidas o "
                   "una filtración. Conviene conversar con el estudiante o pedirle que explique sus respuestas.")
    if not entregados.empty:
        st.bar_chart(entregados.set_index("Estudiante")["Minutos"], color="#3B5BDB", height=220)


# ─────────────────────────── Asistencia ───────────────────────────
def pagina_asistencia() -> None:
    u = usuario()
    st.markdown("## ✅ Asistencia" + (": pasar lista" if es_profe(u) else ""))
    if es_profe(u):
        _asistencia_profe(u)
    else:
        _asistencia_alumno(u)


def _asistencia_alumno(u: dict) -> None:
    cursos = mis_cursos(u)
    gen = asistencia_general(u["email"])
    st.metric("Asistencia general", f"{gen}%", f"{gen - ASISTENCIA_MIN:+d} puntos sobre el mínimo ({ASISTENCIA_MIN}%)")
    cols = st.columns(2)
    for i, c in enumerate(cursos):
        pct, asis, tot = asistencia_alumno(u["email"], c)
        cc = curso(c)
        col = "#2F7D5B" if pct >= ASISTENCIA_MIN + 5 else ("#E0A526" if pct >= ASISTENCIA_MIN else "#D6453D")
        faltas = tot - asis
        permitidas = int(tot * (1 - ASISTENCIA_MIN / 100)) - faltas if tot else 0
        aviso = f"Puedes faltar {max(0, permitidas)} clase(s) más sin bajar del mínimo." if permitidas >= 0 else "Estás bajo el mínimo exigido."
        with cols[i % 2]:
            html(f"""<div class="card accent" style="--c:{cc['color']}"><div class="row"><b>{cc['nombre']}</b>
            <span style="font-weight:800;color:{col}">{pct}%</span></div>
            <div class="track"><div class="fill" style="width:{pct}%;background:{col}"></div></div>
            <div class="muted" style="margin-top:6px">{asis} de {tot} clases. {aviso}</div></div>""")
    st.markdown("##### Detalle por clase")
    code = selector_curso("asis_al")
    if code:
        filas = [{"Fecha": k.split("|")[1], "Estado": reg[u["email"]]} for k, reg in DB["asistencia"].items()
                 if k.startswith(code + "|") and u["email"] in reg]
        filas.sort(key=lambda r: r["Fecha"], reverse=True)
        for f in filas:
            f["Fecha"] = fmt_fecha(date.fromisoformat(f["Fecha"]))
            f["Estado"] = {"Presente": "✅ Presente", "Atrasado": "🕒 Atrasado", "Ausente": "❌ Ausente", "Justificado": "🩺 Justificado"}[f["Estado"]]
        st.dataframe(pd.DataFrame(filas), hide_index=True, height=300)


def _asistencia_profe(u: dict) -> None:
    code = selector_curso("asis_pr", "Curso")
    if not code:
        return
    fechas_pasadas = _fechas_clase(code, hoy() - timedelta(days=42), hoy()) if code in CURSOS_BASE else []
    opciones = sorted(set(fechas_pasadas + [hoy()]), reverse=True)
    fecha = st.selectbox("Clase del día", opciones, format_func=lambda d: f"{DIAS[d.weekday()].capitalize()} {fmt_fecha(d)}")
    clave = f"{code}|{fecha.isoformat()}"
    reg = DB["asistencia"].get(clave, {})
    justif = {j["alumno"] for j in DB["justificaciones"] if j["estado"] == "aprobada"
              and (evaluacion(j["eval_id"]) or {}).get("fecha") == fecha and evaluacion(j["eval_id"])["curso"] == code}
    filas = []
    for a in DB["inscritos"][code]:
        al = usuario(a)
        estado = reg.get(a) or ("Justificado" if a in justif else "Presente")
        filas.append({"email": a, "Estudiante": f"{al['avatar']} {al['nombre']}", "Carrera": al["carrera"], "Estado": estado,
                      "Asistencia total": asistencia_alumno(a, code)[0]})
    df = pd.DataFrame(filas)
    st.caption("Por defecto todos aparecen presentes. Cambia solo a quienes faltaron o llegaron tarde. Los que marcaron con código "
               "y los que tienen justificación aprobada ya vienen marcados.")
    editado = st.data_editor(df, hide_index=True, key=f"editor_{clave}", disabled=["Estudiante", "Carrera", "Asistencia total"],
                             column_order=["Estudiante", "Carrera", "Estado", "Asistencia total"], column_config={
                                 "Estado": st.column_config.SelectboxColumn(options=["Presente", "Atrasado", "Ausente", "Justificado"], required=True),
                                 "Asistencia total": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%d%%")})
    c = editado["Estado"].value_counts()
    m = st.columns(4)
    for col, est in zip(m, ["Presente", "Atrasado", "Ausente", "Justificado"]):
        col.metric(est + "s", int(c.get(est, 0)))
    if st.button("💾 Guardar asistencia", type="primary"):
        with LOCK:
            DB["asistencia"][clave] = dict(zip(editado["email"], editado["Estado"]))
        st.toast(f"Asistencia del {fmt_fecha(fecha)} guardada", icon="✅")
    bajo = [r for r in filas if r["Asistencia total"] < ASISTENCIA_MIN]
    if bajo:
        st.warning("Bajo el mínimo de asistencia: " + ", ".join(r["Estudiante"] for r in bajo))


# ─────────────────────────── Chat ───────────────────────────
def canales_de(u: dict) -> list:
    cursos = mis_cursos(u)
    canales = [f"curso:{c}" for c in cursos]
    contactos = set()
    for c in cursos:
        contactos.add(curso(c)["profesor"])
        contactos.update(DB["inscritos"][c])
    contactos.discard(u["email"])
    profes = sorted([x for x in contactos if usuario(x)["rol"] == "profesor"], key=nombre)
    alumnos = sorted([x for x in contactos if usuario(x)["rol"] != "profesor"], key=nombre)
    return canales + [canal_dm(u["email"], x) for x in profes + alumnos]


def nombre_canal(canal: str, u: dict) -> str:
    if canal.startswith("curso:"):
        return f"# {curso(canal[6:])['nombre']}"
    otro = [x for x in canal[3:].split("|") if x != u["email"]][0]
    ou = usuario(otro)
    rol = "Docente" if ou["rol"] == "profesor" else ou["carrera"].replace("Ingeniería en ", "Ing. ")
    return f"{ou['avatar']} {ou['nombre']} ({rol})"


@st.fragment(run_every=2)
def mensajes_canal(canal: str) -> None:
    u = usuario()
    msgs = [m for m in DB["mensajes"] if m["canal"] == canal][-80:]
    caja = st.container(height=440)
    with caja:
        if not msgs:
            st.caption("No hay mensajes todavía. Escribe el primero.")
        for m in msgs:
            au = usuario(m["autor"])
            with st.chat_message(au["nombre"], avatar=au["avatar"]):
                rol = " · Docente" if au["rol"] == "profesor" else ""
                st.markdown(f"**{au['nombre']}**{rol} <span class='muted'>{dt(m['ts']).strftime('%H:%M')}</span>  \n{m['texto']}",
                            unsafe_allow_html=True)


def pagina_chat() -> None:
    u = usuario()
    st.markdown("## 💬 Chat")
    canales = canales_de(u)
    if not canales:
        st.info("Inscríbete en un ramo para chatear con tu curso y profesores.")
        return
    actual = st.session_state.get("chat_canal")
    if actual not in canales:
        actual = canales[0]
    izq, der = st.columns([1, 2.3], gap="large")
    with izq:
        st.caption("Canales de ramos y mensajes directos")
        sel = st.radio("Conversaciones", canales, index=canales.index(actual), format_func=lambda c: nombre_canal(c, u),
                       key="chat_radio", label_visibility="collapsed")
        st.session_state.chat_canal = sel
    with der:
        st.markdown(f"**{nombre_canal(sel, u)}**")
        mensajes_canal(sel)
        with st.form("enviar_msg", clear_on_submit=True, border=False):
            a, b = st.columns([6, 1], vertical_alignment="bottom")
            txt = a.text_input("Mensaje", placeholder="Escribe un mensaje…", label_visibility="collapsed")
            if b.form_submit_button("Enviar", type="primary") and txt.strip():
                with LOCK:
                    DB["mensajes"].append({"id": nuevo_id(), "canal": sel, "autor": u["email"], "texto": txt.strip()[:1000], "ts": time.time()})
                st.rerun()


# ─────────────────────────── Clase interactiva ───────────────────────────
def _votar(enc: dict, email: str, i: int) -> None:
    with LOCK:
        enc["votos"].setdefault(email, (i, time.time()))


@st.fragment(run_every=1.5)
def encuesta_vivo(code: str) -> None:
    u = usuario()
    enc = DB["encuestas"].get(code)
    if not enc:
        st.caption("No hay votaciones todavía." + ("" if es_profe(u) else " Te avisaremos cuando el profesor abra una."))
        return
    if enc["abierta"] and enc.get("simular"):
        pend = [a for a in DB["inscritos"][code] if a not in enc["votos"] and a != u["email"]]
        for a in random.sample(pend, min(len(pend), random.randint(0, 2))):
            pesos = [4 if i == enc["correcta"] else 1 for i in range(len(enc["opciones"]))]
            enc["votos"][a] = (random.choices(range(len(enc["opciones"])), weights=pesos)[0], time.time())
    conteo = [sum(1 for v in enc["votos"].values() if v[0] == i) for i in range(len(enc["opciones"]))]
    total = sum(conteo)
    estado = "<span class='pill p-red'>● EN VIVO</span>" if enc["abierta"] else "<span class='pill p-gray'>Cerrada</span>"
    html(f"<div class='row'><b style='font-size:1.1rem'>{enc['pregunta']}</b>{estado}</div><div class='muted'>{total} votos</div>")
    etiquetas = [f"{chr(65 + i)}) {o}" + (" ✅" if enc.get("revelada") and i == enc["correcta"] else "") for i, o in enumerate(enc["opciones"])]
    st.bar_chart(pd.DataFrame({"Votos": conteo}, index=etiquetas), color="#7C4DFF", height=250, horizontal=True)
    if not es_profe(u):
        mio = enc["votos"].get(u["email"])
        if mio:
            st.success(f"Votaste {chr(65 + mio[0])}.")
        elif enc["abierta"]:
            cols = st.columns(len(enc["opciones"]))
            for i, (col, o) in enumerate(zip(cols, enc["opciones"])):
                col.button(f"{chr(65 + i)}) {o}", key=f"v_{enc['id']}_{i}", on_click=_votar, args=(enc, u["email"], i))
    if enc.get("revelada"):
        ganadores = sorted([(v[1], a) for a, v in enc["votos"].items() if v[0] == enc["correcta"]])[:5]
        if ganadores:
            st.caption("Más rápidos en acertar: " + ", ".join(f"{i + 1}.º {nombre(a)}" for i, (_, a) in enumerate(ganadores)))


def _responder_sorpresa(code: str, s: dict, email: str, clave: str) -> None:
    eleccion = st.session_state.get(clave)
    if eleccion is None or email in s["respuestas"]:
        return
    seg = time.time() - s["enviada"]
    ok = s["opciones"].index(eleccion) == s["correcta"] and seg <= s["limite"]
    dec = round(s["decimas"] * max(0, s["limite"] - seg) / s["limite"], 1) if ok and s["modo"] == "decimas" else 0.0
    pts = int(100 * max(0, s["limite"] - seg) / s["limite"]) if ok else 0
    with LOCK:
        s["respuestas"][email] = {"correcta": ok, "seg": seg, "decimas": dec, "puntos": pts}
        DB["puntos"].setdefault(code, {})[email] = DB["puntos"].get(code, {}).get(email, 0) + pts
        if dec:
            DB["decimas"].setdefault(code, {})[email] = DB["decimas"].get(code, {}).get(email, 0) + dec


@st.fragment(run_every=1)
def sorpresa_alumno(code: str) -> None:
    u = usuario()
    s = DB["sorpresas"].get(code)
    if not s:
        st.caption("No hay evaluaciones sorpresa activas.")
        return
    r = s["respuestas"].get(u["email"])
    if r:
        if r["correcta"]:
            premio = f"+{r['decimas']:.1f} décimas" if s["modo"] == "decimas" else f"+{r['puntos']} puntos"
            st.success(f"🎉 ¡Correcto! Respondiste en {r['seg']:.1f} s. Ganaste {premio}.")
        else:
            st.warning(f"Respuesta incorrecta ({r['seg']:.1f} s). ¡A la próxima!")
        return
    rest = s["limite"] - (time.time() - s["enviada"])
    if rest <= 0:
        st.error("Se acabó el tiempo de esta evaluación sorpresa.")
        return
    premio = f"hasta **{s['decimas'] * rest / s['limite']:.1f} décimas**" if s["modo"] == "decimas" else "puntos para el ranking"
    st.info(f"⚡ **¡Evaluación sorpresa!** Responde bien y rápido para ganar {premio}. Quedan **{int(rest)} s**.")
    st.progress(rest / s["limite"])
    eleccion = st.radio(s["pregunta"], s["opciones"], index=None, key=f"sor_{s['id']}")
    st.button("Responder", type="primary", disabled=eleccion is None, key=f"sorb_{s['id']}",
              on_click=_responder_sorpresa, args=(code, s, u["email"], f"sor_{s['id']}"))


@st.fragment(run_every=2)
def sorpresa_resultados(code: str) -> None:
    s = DB["sorpresas"].get(code)
    if not s:
        st.caption("Lanza una evaluación sorpresa para ver aquí las respuestas en tiempo real.")
        return
    rest = s["limite"] - (time.time() - s["enviada"])
    st.markdown(f"**{s['pregunta']}**  \n{'⏳ Quedan ' + str(int(rest)) + ' s' if rest > 0 else '⏹️ Tiempo cumplido'}, "
                f"{len(s['respuestas'])} de {len(DB['inscritos'][code])} respondieron")
    filas = sorted([{"Estudiante": nombre(a), "Carrera": usuario(a)["carrera"], "Resultado": "✅" if r["correcta"] else "❌",
                     "Segundos": round(r["seg"], 1), "Décimas": r["decimas"], "Puntos": r["puntos"]}
                    for a, r in s["respuestas"].items()], key=lambda f: (f["Resultado"] != "✅", f["Segundos"]))
    if filas:
        st.dataframe(pd.DataFrame(filas), hide_index=True)


@st.fragment(run_every=1)
def monitor_bano(code: str) -> None:
    limite = DB["config"]["bano_limite_min"] * 60
    fuera = [(a, b) for a, b in DB["bano"].items() if b["curso"] == code]
    if not fuera:
        st.caption("Ningún estudiante de este curso está fuera de la sala.")
    for a, b in fuera:
        seg = time.time() - b["inicio"]
        col = "#2F7D5B" if seg < limite / 2 else ("#E0A526" if seg < limite else "#D6453D")
        al = usuario(a)
        html(f"""<div class="card"><div class="row"><div><b>{al['avatar']} {al['nombre']}</b><br>
        <span class="muted">{al['carrera']}, salió a las {dt(b['inicio']).strftime('%H:%M')}</span></div>
        <div class="timer" style="font-size:2rem;color:{col}">{mmss(seg)}</div></div></div>""")


def pagina_interactiva() -> None:
    u = usuario()
    st.markdown("## 🎮 Clase interactiva")
    code = selector_curso("inter")
    if not code:
        return
    pestañas = ["🟣 Votación en vivo", "⚡ Evaluación sorpresa", "🏆 Ranking"] + (["🚻 Salidas de sala"] if es_profe(u) else [])
    tabs = st.tabs(pestañas)

    with tabs[0]:
        if es_profe(u):
            enc = DB["encuestas"].get(code)
            with st.expander("Crear nueva votación", expanded=not enc):
                with st.form(f"enc_{code}"):
                    tema = st.selectbox("Usar pregunta del banco", ["(Escribir la mía)"] + list(BANCO_PREGUNTAS))
                    preg = st.text_input("Pregunta", placeholder="Ej: ¿Cuál es la complejidad de la búsqueda binaria?")
                    ops = st.text_area("Opciones (una por línea)", placeholder="O(n)\nO(log n)\nO(n log n)\nO(1)")
                    corr = st.number_input("Número de la opción correcta (0 si es solo opinión)", 0, 6, 0)
                    sim = st.checkbox("Simular votos de los alumnos (demo)", value=True)
                    if st.form_submit_button("🟣 Abrir votación", type="primary"):
                        if tema != "(Escribir la mía)":
                            preg, opciones, c = BANCO_PREGUNTAS[tema]
                        else:
                            opciones = [o.strip() for o in ops.splitlines() if o.strip()]
                            c = int(corr) - 1 if corr else None
                        if not preg or len(opciones) < 2:
                            st.error("Escribe una pregunta y al menos dos opciones.")
                        else:
                            with LOCK:
                                DB["encuestas"][code] = {"id": nuevo_id(), "pregunta": preg, "opciones": opciones, "correcta": c,
                                                         "abierta": True, "votos": {}, "creada": time.time(), "simular": sim, "revelada": False}
                            st.rerun()
            if enc:
                a, b = st.columns(2)
                if enc["abierta"] and a.button("⏹️ Cerrar votación"):
                    with LOCK:
                        enc["abierta"] = False
                    st.rerun()
                if not enc["abierta"] and enc["correcta"] is not None and not enc.get("revelada") and b.button("✅ Revelar respuesta y dar puntos"):
                    with LOCK:
                        enc["revelada"] = True
                        ganadores = sorted([(v[1], a) for a, v in enc["votos"].items() if v[0] == enc["correcta"]])
                        for i, (_, a) in enumerate(ganadores):
                            DB["puntos"].setdefault(code, {})[a] = DB["puntos"].get(code, {}).get(a, 0) + max(30, 100 - 10 * i)
                    st.rerun()
        with st.container(border=True):
            encuesta_vivo(code)

    with tabs[1]:
        if es_profe(u):
            a, b = st.columns([1, 1.3], gap="large")
            with a:
                with st.form(f"sor_{code}"):
                    tema = st.selectbox("Pregunta", list(BANCO_PREGUNTAS))
                    modo = st.radio("Modalidad", ["Vale décimas", "Solo juego (puntos de ranking)"], horizontal=True)
                    c1, c2 = st.columns(2)
                    dec = c1.slider("Décimas máximas", 1, 10, 5)
                    lim = c2.slider("Tiempo (s)", 15, 120, 30, step=5)
                    if st.form_submit_button("⚡ Lanzar a todo el curso", type="primary"):
                        p, ops, c = BANCO_PREGUNTAS[tema]
                        with LOCK:
                            DB["sorpresas"][code] = {"id": nuevo_id(), "pregunta": p, "opciones": ops, "correcta": c,
                                                     "modo": "decimas" if modo.startswith("Vale") else "juego",
                                                     "decimas": dec, "limite": lim, "enviada": time.time(), "respuestas": {}}
                        st.toast(f"Evaluación sorpresa enviada a {len(DB['inscritos'][code])} estudiantes", icon="⚡")
                        st.rerun()
                if DB["sorpresas"].get(code) and st.button("🤖 Simular respuestas de alumnos (demo)"):
                    s = DB["sorpresas"][code]
                    with LOCK:
                        for al in DB["inscritos"][code]:
                            if al not in s["respuestas"] and random.random() < 0.8:
                                seg = random.uniform(3, s["limite"] * 0.9)
                                ok = random.random() < 0.7
                                d = round(s["decimas"] * (s["limite"] - seg) / s["limite"], 1) if ok and s["modo"] == "decimas" else 0.0
                                pts = int(100 * (s["limite"] - seg) / s["limite"]) if ok else 0
                                s["respuestas"][al] = {"correcta": ok, "seg": seg, "decimas": d, "puntos": pts}
                                DB["puntos"].setdefault(code, {})[al] = DB["puntos"].get(code, {}).get(al, 0) + pts
                                if d:
                                    DB["decimas"].setdefault(code, {})[al] = DB["decimas"].get(code, {}).get(al, 0) + d
            with b:
                sorpresa_resultados(code)
        else:
            with st.container(border=True):
                sorpresa_alumno(code)

    with tabs[2]:
        pts = DB["puntos"].get(code, {})
        dec = DB["decimas"].get(code, {})
        if not pts:
            st.caption("El ranking se llena con las votaciones y evaluaciones sorpresa de la clase.")
        else:
            orden = sorted(pts.items(), key=lambda x: -x[1])
            medallas = ["🥇", "🥈", "🥉"]
            filas = [{"#": medallas[i] if i < 3 else str(i + 1), "Estudiante": nombre(a), "Carrera": usuario(a)["carrera"],
                      "Puntos": p, "Décimas ganadas": round(dec.get(a, 0), 1)} for i, (a, p) in enumerate(orden)]
            st.dataframe(pd.DataFrame(filas), hide_index=True)
            if not es_profe(u) and u["email"] in pts:
                pos = [a for a, _ in orden].index(u["email"]) + 1
                st.success(f"Vas en el lugar {pos} de {len(orden)} con {pts[u['email']]} puntos.")

    if es_profe(u):
        with tabs[3]:
            DB["config"]["bano_limite_min"] = st.slider("Avisarme cuando alguien supere (minutos)", 3, 30,
                                                        DB["config"]["bano_limite_min"])
            monitor_bano(code)
            log = [x for x in DB["bano_log"] if x["curso"] == code and dt(x["inicio"]).date() == hoy()]
            if log:
                st.markdown("##### Historial de hoy")
                st.dataframe(pd.DataFrame([{"Estudiante": nombre(x["alumno"]), "Salida": dt(x["inicio"]).strftime("%H:%M"),
                                            "Duración": mmss(x["duracion"])} for x in log]), hide_index=True)


# ─────────────────────────── Perfil ───────────────────────────
def pagina_perfil() -> None:
    u = usuario()
    st.markdown("## 👤 Perfil y configuración")
    a, b = st.columns([1, 1.4], gap="large")
    with a:
        with st.container(border=True):
            html(f"<div style='text-align:center'>{avatar_html(u, 110)}<div class='pn' style='font-size:1.3rem'>{u['nombre']}</div>"
                 f"<div class='pr'>{'Docente' if es_profe(u) else 'Estudiante'}, {u['carrera'].replace('Docente, ', '')}</div>"
                 f"<div class='muted'>{u['email']}</div></div>")
            foto = st.file_uploader("Cambiar foto de perfil", type=["png", "jpg", "jpeg"])
            if foto and st.button("Guardar foto"):
                if foto.size > 2 * 1024 * 1024:
                    st.error("La foto debe pesar menos de 2 MB.")
                else:
                    with LOCK:
                        u["foto"] = base64.b64encode(foto.getvalue()).decode()
                    st.rerun()
            if not es_profe(u):
                car = st.selectbox("Carrera", CARRERAS, index=CARRERAS.index(u["carrera"]) if u["carrera"] in CARRERAS else 0)
                if car != u["carrera"] and st.button("Actualizar carrera"):
                    with LOCK:
                        u["carrera"] = car
                    st.rerun()
            st.caption("Tus profesores y compañeros ven tu nombre, foto y carrera en los cursos y el chat.")
    with b:
        with st.container(border=True):
            st.markdown("#### 🤖 Inteligencia artificial (tu propia API key)")
            st.caption("La transcripción, traducción, apuntes y diagramas usan tu cuenta de IA, así la plataforma no "
                       "asume ese costo. Tu key queda solo en esta sesión del navegador: no se guarda en la base de datos.")
            cfg = ia_cfg()
            prov = st.radio("Proveedor", ["Demo", "OpenAI", "Groq"], horizontal=True,
                            index=["Demo", "OpenAI", "Groq"].index(cfg["proveedor"]),
                            captions=["Sin costo, respuestas de ejemplo", "Whisper + GPT", "Whisper + Llama, tiene plan gratuito"])
            if prov != "Demo":
                base = PROVEEDORES_IA[prov]
                key = st.text_input("API key", value=cfg.get("key", "") if cfg["proveedor"] == prov else "", type="password")
                c1, c2 = st.columns(2)
                stt = c1.text_input("Modelo de transcripción", value=cfg.get("stt", base["stt"]) if cfg["proveedor"] == prov else base["stt"])
                llm = c2.text_input("Modelo de texto", value=cfg.get("llm", base["llm"]) if cfg["proveedor"] == prov else base["llm"])
                x1, x2 = st.columns(2)
                if x1.button("Guardar configuración", type="primary"):
                    st.session_state.ia = {"proveedor": prov, "key": key.strip(), "base": base["base"], "stt": stt, "llm": llm}
                    st.toast("Configuración de IA guardada para esta sesión", icon="🤖")
                if x2.button("Probar conexión"):
                    st.session_state.ia = {"proveedor": prov, "key": key.strip(), "base": base["base"], "stt": stt, "llm": llm}
                    try:
                        r = ia_chat("Responde solo con la palabra OK.", "Prueba")
                        st.success(f"Conexión correcta. Respuesta del modelo: {r[:40]}")
                    except ErrorIA as e:
                        mostrar_error_ia(e)
            else:
                if st.button("Usar modo demo"):
                    st.session_state.ia = {"proveedor": "Demo"}
                    st.toast("Modo demo activado", icon="🤖")
        with st.container(border=True):
            st.markdown("#### 🔔 Notificaciones")
            son = st.toggle("Sonido en avisos (fin de clase, evaluaciones sorpresa)", value=u.get("sonido", True))
            if son != u.get("sonido", True):
                with LOCK:
                    u["sonido"] = son
            if st.button("Probar sonido"):
                sonar("fin")
        with st.container(border=True):
            st.markdown("#### 🔐 Sesión")
            s = DB["sesiones"].get(st.session_state.get("token"), {})
            if s:
                st.caption(f"Tu sesión sigue abierta hasta el {dt(s['expira']).strftime('%d-%m-%Y %H:%M')}, aunque cierres "
                           "o recargues la página. Guarda esta página en marcadores para entrar directo.")
            activas = sum(1 for x in DB["sesiones"].values() if x["email"] == u["email"] and x["expira"] > time.time())
            st.caption(f"Sesiones abiertas con tu cuenta: {activas}")
            if st.button("Cerrar sesión en todos los dispositivos"):
                cerrar_sesion(todas=True)
                st.rerun()


# ═════════════════════════════════════════════════════════════════════
# Programa principal
# ═════════════════════════════════════════════════════════════════════
restaurar_sesion()

if "user" not in st.session_state:
    pantalla_login()
    st.stop()

if st.query_params.get("sesion") != st.session_state.token:
    st.query_params["sesion"] = st.session_state.token

barra_lateral()
vigilante()

slug = next((k for k, v in PAGINAS.items() if v == st.session_state.nav), "inicio")
if st.query_params.get("p") != slug:
    st.query_params["p"] = slug

{
    "inicio": pagina_inicio, "ramos": pagina_ramos, "horario": pagina_horario, "aula": pagina_aula,
    "evaluaciones": pagina_evaluaciones, "asistencia": pagina_asistencia, "chat": pagina_chat,
    "interactiva": pagina_interactiva, "perfil": pagina_perfil,
}[slug]()
