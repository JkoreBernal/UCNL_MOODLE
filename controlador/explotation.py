
# controlador/explotation.py

import re
import requests

from controlador import material


BASE_URL = "https://licenciatura.ucnl.edu.mx"


def get_user_id(session):

    paginas = [
        f"{BASE_URL}/my/",
        f"{BASE_URL}/my/courses.php",
        f"{BASE_URL}/user/profile.php"
    ]

    for url in paginas:

        try:

            response = session.get(
                url,
                timeout=15
            )

        except requests.RequestException:

            continue

        if "login/index.php" in response.url:

            return None

        match = re.search(
            r"/user/profile\.php\?id=(\d+)",
            response.url
        )

        if match and match.group(1) != "0":

            return match.group(1)

        matches = re.findall(
            r"/user/profile\.php\?id=(\d+)",
            response.text
        )

        for user_id in matches:

            if user_id != "0":

                return user_id

        matches = re.findall(
            r'data-userid=["\'](\d+)["\']',
            response.text
        )

        for user_id in matches:

            if user_id != "0":

                return user_id

    return None


def consultar_calificaciones(session):

    print("\n======================================")
    print("🎓 OBTENIENDO ESTADO ACADÉMICO")
    print("======================================")

    user_id = get_user_id(session)

    if not user_id:

        print(
            "[-] No se pudo obtener el ID del usuario."
        )

        return []

    print(
        f"[+] Usuario detectado: {user_id}"
    )

    cursos, sesskey = material.get_user_courses(
        session
    )

    if not cursos:

        print(
            "[-] No se encontraron materias."
        )

        return []

    print(
        f"[+] Materias encontradas: "
        f"{len(cursos)}"
    )

    datos = []

    for curso in cursos:

        course_id = curso["id"]

        nombre = curso["fullname"]

        print("\n--------------------------------------")

        print(
            f"📚 {nombre}"
        )

        print(
            f"   ID: {course_id}"
        )

        actividades = material.obtener_actividades(
            session,
            user_id,
            course_id
        )

        filas = []

        metadatos = []

        for actividad in actividades:

            textos = actividad["textos"]

            filas.append(
                textos
            )

            metadatos.append({

                "id_actividad":
                    actividad["id_actividad"],

                "url_actividad":
                    actividad["url"],

                "fecha_abre":
                    actividad["fecha_abre"],

                "fecha_cierra":
                    actividad["fecha_cierra"],

                "estado":
                    actividad["estado"],

                "completada":
                    actividad["completada"]

            })

            print(
                f"   🔗 ID actividad: "
                f"{actividad['id_actividad']}"
            )

            if actividad["fecha_abre"]:

                print(
                    f"   🟢 Abre: "
                    f"{actividad['fecha_abre']}"
                )

            if actividad["fecha_cierra"]:

                print(
                    f"   🔴 Cierra: "
                    f"{actividad['fecha_cierra']}"
                )

        datos.append({

            "course":
                nombre,

            "course_id":
                course_id,

            "filas":
                filas,

            "metadatos":
                metadatos

        })

    return datos
