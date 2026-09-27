
# configuracion/materials.py
# Obtiene materias, actividades, IDs, fechas y estado desde Moodle

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


BASE_URL = "https://licenciatura.ucnl.edu.mx"


def get_user_courses(session_obj):
    """
    Obtiene las materias del usuario.
    """

    response = session_obj.get(
        f"{BASE_URL}/my/courses.php"
    )

    match = re.search(
        r'"sesskey":"([^"]+)"',
        response.text
    )

    if not match:
        return [], None

    sesskey = match.group(1)

    ajax_url = (
        f"{BASE_URL}/lib/ajax/service.php"
        f"?sesskey={sesskey}"
    )

    payload = [{
        "index": 0,
        "methodname":
        "core_course_get_enrolled_courses_by_timeline_classification",
        "args": {
            "offset": 0,
            "limit": 0,
            "classification": "all",
            "sort": "fullname"
        }
    }]

    try:
        res = session_obj.post(
            ajax_url,
            json=payload,
            timeout=15
        )
    except requests.RequestException:
        return [], sesskey

    if res.status_code != 200:
        return [], sesskey

    try:
        data = res.json()

        if not data:
            return [], sesskey

        if data[0].get("error"):
            return [], sesskey

        cursos_raw = data[0]["data"]["courses"]

        cursos = []

        for curso in cursos_raw:
            cursos.append({
                "id": curso["id"],
                "fullname": curso["fullname"],
                "shortname": curso["shortname"],
                "url": curso["viewurl"]
            })

        return cursos, sesskey

    except (KeyError, ValueError, IndexError, TypeError):
        return [], sesskey


def obtener_fechas(session, url):
    """
    Obtiene fechas y estado de una actividad de Moodle.

    Devuelve:
    - fecha de apertura
    - fecha de cierre
    - estado
    - completada
    """

    try:
        response = session.get(
            url,
            timeout=15
        )
    except requests.RequestException:
        return None, None, None, False

    if response.status_code != 200:
        return None, None, None, False

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    texto = soup.get_text(
        " ",
        strip=True
    )

    texto_lower = texto.lower()

    abre = None
    cierra = None
    estado = None
    completada = False

    # =========================================================
    # FECHA DE APERTURA
    # =========================================================

    match_abre = re.search(
        r"Abiertos\s*:\s*(.*?)(?=\s*Pendientes\s*:)",
        texto,
        re.I
    )

    if match_abre:
        abre = match_abre.group(1).strip()

    # =========================================================
    # FECHA DE CIERRE
    # =========================================================

    match_cierra = re.search(
        r"Pendientes\s*:\s*(.*?\d{2}:\d{2})",
        texto,
        re.I
    )

    if match_cierra:
        cierra = match_cierra.group(1).strip()

    # =========================================================
    # ESTADO DE ENTREGA
    # =========================================================

    if "enviado para calificar" in texto_lower:
        estado = "Enviado para calificar"
        completada = True

    elif "enviado" in texto_lower:
        estado = "Enviado"
        completada = True

    elif "calificado" in texto_lower:
        estado = "Calificado"
        completada = True

    # =========================================================
    # MOSTRAR INFORMACIÓN
    # =========================================================

    if abre:
        print(
            f"   🟢 Abiertos: {abre}"
        )

    if cierra:
        print(
            f"   🔴 Pendientes: {cierra}"
        )

    if estado:
        print(
            f"   📌 Estado: {estado}"
        )

    print(
        f"   ☑️ Completada: {completada}"
    )

    return abre, cierra, estado, completada


def obtener_actividades(
    session,
    user_id,
    course_id
):
    """
    Obtiene las actividades de una materia.

    Aquí se obtiene:
    - nombre/datos de la fila
    - ID de actividad
    - URL
    - fecha de apertura
    - fecha de cierre
    - estado
    - completada
    """

    url = (
        f"{BASE_URL}/course/user.php"
        f"?mode=grade&id={course_id}"
        f"&user={user_id}"
    )

    try:
        response = session.get(
            url,
            timeout=15
        )
    except requests.RequestException:
        return []

    if response.status_code != 200:
        return []

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    actividades = []

    for fila in soup.find_all("tr"):

        celdas = fila.find_all(
            ["td", "th"]
        )

        if len(celdas) < 2:
            continue

        textos = [
            celda.get_text(
                " ",
                strip=True
            )
            for celda in celdas
        ]

        textos = [
            texto
            for texto in textos
            if texto
        ]

        enlace = fila.find(
            "a",
            href=True
        )

        if not enlace:
            continue

        href = enlace["href"]

        if "/mod/" not in href:
            continue

        id_match = re.search(
            r"[?&]id=(\d+)",
            href
        )

        if not id_match:
            continue

        id_actividad = int(
            id_match.group(1)
        )

        url_actividad = urljoin(
            BASE_URL,
            href
        )

        (
            fecha_abre,
            fecha_cierra,
            estado,
            completada
        ) = obtener_fechas(
            session,
            url_actividad
        )

        actividades.append({
            "textos": textos,
            "id_actividad": id_actividad,
            "url": url_actividad,
            "fecha_abre": fecha_abre,
            "fecha_cierra": fecha_cierra,
            "estado": estado,
            "completada": completada
        })

    return actividades


def materias(session_obj):
    """
    Compatibilidad con configuracion.__init__.

    No duplica la obtención de materias.
    """

    return get_user_courses(session_obj)