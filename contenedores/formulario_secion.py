import flet as ft


def formulario(page: ft.Page):

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

    def mostrar_formulario(visible=True):
        usuario.visible = visible
        password.visible = visible
        boton.visible = visible
        page.update()

    def ocultar_formulario():
        mostrar_formulario(False)

    return {
        "usuario": usuario,
        "password": password,
        "boton": boton,
        "resultado": resultado,
        "mostrar_cargando": mostrar_cargando,
        "ocultar_formulario": ocultar_formulario,
        "mostrar_formulario": mostrar_formulario
    }