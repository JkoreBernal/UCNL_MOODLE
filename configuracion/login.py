#login.py
#basicamente es el inicio de secion(carga credenciales capturadas)
import json
import os
import getpass


# Siempre usa la carpeta donde está este archivo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")

def load_credentials():
    """
    Carga las credenciales guardadas.

    Devuelve:
        dict -> si existen credenciales válidas
        None -> si no existen o están dañadas
    """

    if not os.path.exists(CREDENTIALS_FILE):
        return None

    try:
        with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if data.get("username") and data.get("password"):
            return data

    except (json.JSONDecodeError, ValueError, OSError):
        try:
            os.remove(CREDENTIALS_FILE)
        except OSError:
            pass

    return None


def save_credentials(username, password):
    """
    Guarda usuario y contraseña en credentials.json.

    Devuelve:
        True  -> guardado correctamente
        False -> ocurrió un error
    """

    data = {
        "username": username,
        "password": password
    }

    try:
        with open(CREDENTIALS_FILE, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )

        return True

    except OSError as e:
        print(f"❌ Error al guardar credenciales: {e}")
        return False


def get_user_credentials():
    """
    Solicita las credenciales desde la consola.
    """

    usuario = input(
        "Ingrese su nombre de usuario: "
    ).strip()

    contrasena = getpass.getpass(
        "Ingrese su contraseña: "
    ).strip()

    return usuario, contrasena


def registro():
    """
    Aqui se ejecuta todo
    """
    return load_credentials()