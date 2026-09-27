# controlador/main.py
# Se encarga de coordinar todo (conecta)

import os
import sys

# ================================================================
# AGREGAR LA CARPETA RAÍZ DEL PROYECTO
# ================================================================

ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


import flet as ft
import requests

# Importaciones desde paquetes/subcarpetas del proyecto
from configuracion import login, session
from contenedores import UCNL
from extras import work


def main(page: ft.Page):

    # Obtenemos la UI del login desde el módulo en contenedores
    ui = UCNL.pagina_principal(page)

    usuario = ui["usuario"]
    password = ui["password"]
    boton = ui["boton"]
    resultado = ui["resultado"]

    ocultar = ui["ocultar_formulario"]
    mostrar = ui["mostrar_formulario"]

    def comprobar_moodle():

        moodle = requests.Session()

        if session.login(moodle):

            credenciales = login.load_credentials()
            nombre = credenciales.get("username", "")

            resultado.controls.clear()

            resultado.controls.append(
                ft.Text("🟢 CONECTADO")
            )

            resultado.controls.append(
                ft.Text(f"👤 Usuario: {nombre}")
            )

            resultado.controls.append(
                ft.Text("🔐 Sesión Moodle activa.")
            )

            page.update()

            # ====================================================
            # TRANSICIÓN A LA INTERFAZ VISUAL
            # ====================================================

            work.mostrar(
                page,
                moodle
            )

        else:

            resultado.controls.clear()

            resultado.controls.append(
                ft.Text(
                    "❌ Las credenciales no son válidas."
                )
            )

            resultado.controls.append(
                ft.Text(
                    "🔑 Introduce nuevamente tus datos."
                )
            )

            try:
                login.os.remove(
                    login.CREDENTIALS_FILE
                )
            except OSError:
                pass

            boton.disabled = False
            mostrar()

            page.update()

    def iniciar_sesion(e):

        user = usuario.value.strip()
        passwd = password.value.strip()

        if not user or not passwd:

            resultado.controls.clear()

            resultado.controls.append(
                ft.Text(
                    "⚠️ Introduce usuario y contraseña."
                )
            )

            page.update()

            return

        if not login.save_credentials(
            user,
            passwd
        ):
            return

        boton.disabled = True

        ocultar()

        resultado.controls.clear()

        resultado.controls.append(
            ft.Text(
                "⏳ Comprobando credenciales..."
            )
        )

        resultado.controls.append(
            ft.Text(
                "🌐 Conectando con Moodle..."
            )
        )

        page.update()

        page.run_thread(
            comprobar_moodle
        )

    boton.on_click = iniciar_sesion

    # ============================================================
    # LOGIN AUTOMÁTICO
    # ============================================================

    if login.load_credentials():

        ocultar()

        resultado.controls.clear()

        resultado.controls.append(
            ft.Text(
                "🔐 Credenciales encontradas."
            )
        )

        resultado.controls.append(
            ft.Text(
                "⏳ Comprobando credenciales..."
            )
        )

        resultado.controls.append(
            ft.Text(
                "🌐 Conectando con Moodle..."
            )
        )

        page.update()

        page.run_thread(
            comprobar_moodle
        )


if __name__ == "__main__":

    print(
        "🚀 Iniciando UCNL Moodle Ops Center..."
    )

    ft.run(main)