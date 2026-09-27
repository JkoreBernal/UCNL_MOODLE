#logo-es simplemente el banner

import flet as ft

def logo_ucnl():
    return """
██║   ██║██████╗ ███╗   ██╗██║     
██║   ██║██╔════╝████╗  ██║██║     
██║   ██║██║     ██╔██╗ ██║██║     
██║   ██║██║     ██║╚██╗██║██║      
██║   ██║██║     ██║ ╚████║██║     
     ╚██████╔╝╚██████╗██║  ╚███║███████╗
      ╚═════╝  ╚═════╝╚═╝   ╚══╝╚══════╝
"""

def logo_linea():
    return """
══════████████████████████████████████████████████════
  ╚═══════════════════════════════════════════╝
"""

def pagina_principal(page: ft.Page):
    page.title = "UCNL MOODLE"

    encabezado = ft.Text(
        spans=[
            ft.TextSpan(
                logo_ucnl().rstrip() + "\n",
                style=ft.TextStyle(
                    font_family="monospace",
                    size=12,
                    color="#FF8C00"
                )
            ),
            ft.TextSpan(
                logo_linea().lstrip(),
                style=ft.TextStyle(
                    font_family="monospace",
                    size=12,
                    color="#7700FFC1"
                )
            )
        ],
        text_align=ft.TextAlign.CENTER
    )

    usuario = ft.TextField(
        hint_text="¿Cuál es tu usuario?",
        width=400
    )

    password = ft.TextField(
        hint_text="¿Cuál es tu contraseña?",
        password=True,
        can_reveal_password=True,
        width=400
    )

    resultado = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=5
    )

    boton = ft.Button("Iniciar sesión")

    def mostrar_cargando(mensaje):
        resultado.controls.clear()
        resultado.controls.append(ft.Text(mensaje))
        page.update()

    def ocultar_formulario():
        usuario.visible = False
        password.visible = False
        boton.visible = False
        page.update()

    def mostrar_formulario():
        usuario.visible = True
        password.visible = True
        boton.visible = True
        page.update()

    view = ft.Column(
        width=600,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
        controls=[
            encabezado,
            usuario,
            password,
            ft.Row(
                controls=[boton],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            resultado
        ]
    )

    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.add(view)

    return {
        "usuario": usuario,
        "password": password,
        "boton": boton,
        "resultado": resultado,
        "mostrar_cargando": mostrar_cargando,
        "ocultar_formulario": ocultar_formulario,
        "mostrar_formulario": mostrar_formulario
    }