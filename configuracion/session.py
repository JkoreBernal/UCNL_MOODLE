# configuracion/session.py
import requests
from bs4 import BeautifulSoup

from configuracion import login as login_manager

BASE_URL = "https://licenciatura.ucnl.edu.mx"
LOGIN_URL = f"{BASE_URL}/login/index.php"

def iniciar_sesion(session):
    """
    Inicia sesión en Moodle usando las credenciales
    guardadas en credentials.json.
    """

    credentials = login_manager.load_credentials()

    if not credentials:
        print("❌ No hay credenciales guardadas.")
        return False

    username = credentials.get("username")
    password = credentials.get("password")

    if not username or not password:
        print("❌ Las credenciales están incompletas.")
        return False

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Referer": LOGIN_URL
    }

    try:

        # 1. Abrimos la página de Moodle
        response_get = session.get(
            LOGIN_URL,
            headers=headers,
            timeout=20
        )

        if response_get.status_code != 200:
            print(
                f"❌ Moodle respondió HTTP "
                f"{response_get.status_code}"
            )
            return False

        soup = BeautifulSoup(
            response_get.text,
            "html.parser"
        )

        # 2. Buscamos el token de Moodle
        token_input = soup.find(
            "input",
            {"name": "logintoken"}
        )

        payload = {
            "username": username,
            "password": password
        }

        if token_input:

            token = token_input.get("value")

            if token:
                payload["logintoken"] = token

        # 3. Enviamos las credenciales
        response_post = session.post(
            LOGIN_URL,
            data=payload,
            headers=headers,
            timeout=20,
            allow_redirects=True
        )

        if response_post.status_code != 200:
            print(
                f"❌ Error HTTP durante login: "
                f"{response_post.status_code}"
            )
            return False

        # 4. Comprobamos la respuesta
        url_final = response_post.url.lower()

        soup_final = BeautifulSoup(
            response_post.text,
            "html.parser"
        )

        login_form = soup_final.find(
            "form",
            id="login"
        )

        if "login/index.php" in url_final and login_form:

            print(
                "❌ Usuario o contraseña incorrectos."
            )

            return False

        # 5. Comprobación adicional
        respuesta_mi = session.get(
            f"{BASE_URL}/my/",
            headers=headers,
            timeout=20
        )

        if respuesta_mi.status_code != 200:
            print("❌ No se pudo comprobar la sesión.")
            return False

        if "login/index.php" in respuesta_mi.url.lower():

            print(
                "❌ Moodle no mantuvo la sesión."
            )

            return False

        print("✅ Login exitoso.")

        return True

    except requests.RequestException as e:

        print(
            f"❌ Error de conexión con Moodle: {e}"
        )

        return False


def secion(session):
    """
    aqui va todo el ejecutable
    """
    return iniciar_sesion(session)