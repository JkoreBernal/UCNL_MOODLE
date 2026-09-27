
# controlador/principal.py
# Lógica Principal
# UCNL MOODLE // OPS CENTER

import os
import sys
import flet as ft


# =========================================================
# CONFIGURACIÓN DE LA RAÍZ DEL PROYECTO
# =========================================================

RAIZ_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if RAIZ_DIR not in sys.path:
    sys.path.append(RAIZ_DIR)


# =========================================================
# IMPORTACIONES
# =========================================================

from configuracion import selec
from configuracion import materials
from configuracion import relacion
from configuracion import calificaciones

from contenedores import week
from contenedores import status
from contenedores import expired


# =========================================================
# COLORES
# =========================================================

FONDO = "#0B1020"

SUPERFICIE = "#11182B"
SUPERFICIE_2 = "#151E35"
SUPERFICIE_3 = "#1A2540"

BLANCO = "#F8FAFC"
TEXTO = "#E5E7EB"

GRIS = "#94A3B8"
GRIS_OSCURO = "#64748B"

VERDE = "#A3E635"
VERDE_OSCURO = "#1C3F3E"

AZUL = "#60A5FA"
AZUL_SUAVE = "#172554"

ROJO = "#F87171"
ROJO_SUAVE = "#3F1515"

BORDE = "#26324A"


# =========================================================
# BORDE
# =========================================================

def crear_borde(color):

    return ft.Border(
        left=ft.BorderSide(
            width=1,
            color=color
        ),
        top=ft.BorderSide(
            width=1,
            color=color
        ),
        right=ft.BorderSide(
            width=1,
            color=color
        ),
        bottom=ft.BorderSide(
            width=1,
            color=color
        ),
    )


# =========================================================
# CONFIGURACIÓN VISUAL DE PÁGINA
# =========================================================

def configurar_pagina(page):

    page.bgcolor = FONDO
    page.padding = 20

    page.horizontal_alignment = (
        ft.CrossAxisAlignment.CENTER
    )

    page.vertical_alignment = (
        ft.MainAxisAlignment.START
    )


# =========================================================
# ENCABEZADO
# =========================================================

def encabezado(
    titulo,
    subtitulo=""
):

    controles = [

        ft.Text(
            titulo,
            size=28,
            weight=ft.FontWeight.BOLD,
            color=BLANCO,
        )
    ]

    if subtitulo:

        controles.append(

            ft.Text(
                subtitulo,
                size=14,
                color=GRIS,
            )
        )

    return ft.Container(

        content=ft.Column(
            controls=controles,
            spacing=4,
        ),

        width=850,

        padding=20,

        bgcolor=SUPERFICIE,

        border=crear_borde(
            BORDE
        ),

        border_radius=20,
    )


# =========================================================
# BOTÓN REGRESAR
# =========================================================

def boton_regresar(page, moodle_session):

    from extras import work

    return ft.Container(

        content=ft.Row(

            controls=[

                ft.Text(
                    "←",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=VERDE,
                ),

                ft.Text(
                    "REGRESAR AL PANEL",
                    size=13,
                    weight=ft.FontWeight.BOLD,
                    color=BLANCO,
                ),
            ],

            alignment=ft.MainAxisAlignment.CENTER,

            spacing=8,
        ),

        alignment=ft.Alignment(0, 0),

        padding=12,

        bgcolor=VERDE_OSCURO,

        border=crear_borde(
            VERDE
        ),

        border_radius=15,

        on_click=lambda e: work.mostrar(
            page,
            moodle_session
        ),
    )


# =========================================================
# CURSOS
# =========================================================

def cursos(page, moodle_session):

    configurar_pagina(page)

    materials.cursos_actuales(
        page,
        moodle_session
    )

    page.add(

        ft.Container(

            content=boton_regresar(
                page,
                moodle_session
            ),

            margin=10,
        )
    )

    page.update()


# =========================================================
# ACTIVIDADES
# =========================================================

def actividades(page, moodle_session):

    configurar_pagina(page)

    base_url = (
        "https://licenciatura.ucnl.edu.mx"
    )

    # =====================================================
    # OBTENER SESSKEY
    # =====================================================

    sesskey = relacion.obtener_sesskey(
        moodle_session,
        base_url
    )

    if not sesskey:

        page.clean()

        configurar_pagina(page)

        error_card = ft.Container(

            content=ft.Column(

                controls=[

                    ft.Text(
                        "⚠️",
                        size=40,
                    ),

                    ft.Text(
                        "NO SE PUDO OBTENER EL SESSKEY",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=BLANCO,
                    ),

                    ft.Text(
                        "No fue posible establecer "
                        "la comunicación con Moodle.",
                        size=14,
                        color=GRIS,
                        text_align=ft.TextAlign.CENTER,
                    ),

                    ft.Container(

                        content=boton_regresar(
                            page,
                            moodle_session
                        ),

                        margin=10,
                    ),
                ],

                horizontal_alignment=(
                    ft.CrossAxisAlignment.CENTER
                ),

                spacing=10,
            ),

            width=550,

            padding=30,

            bgcolor=SUPERFICIE,

            border=crear_borde(
                ROJO
            ),

            border_radius=22,
        )

        page.add(
            error_card
        )

        page.update()

        return

    # =====================================================
    # OBTENER EVENTOS
    # =====================================================

    eventos = relacion.obtener_eventos_api(
        moodle_session,
        base_url,
        sesskey
    )

    lista_actividades = (
        relacion.procesar_eventos_moodle(
            eventos
        )
    )

    # =====================================================
    # CONTENIDO
    # =====================================================

    contenido = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=12,
        expand=True,
    )

    # =====================================================
    # ENCABEZADO
    # =====================================================

    contenido.controls.append(

        encabezado(

            "📅 ACTIVIDADES DEL CALENDARIO",

            f"{len(lista_actividades)} "
            "actividades encontradas en Moodle"

        )
    )

    # =====================================================
    # INFORMACIÓN DEL CALENDARIO
    # =====================================================

    contenido.controls.append(

        ft.Container(

            content=ft.Row(

                controls=[

                    ft.Container(

                        content=ft.Text(
                            "CALENDARIO MOODLE",
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=AZUL,
                        ),

                        padding=10,

                        bgcolor=AZUL_SUAVE,

                        border_radius=10,
                    ),

                    ft.Text(
                        "Eventos académicos",
                        size=13,
                        color=GRIS,
                    ),
                ],

                spacing=12,
            ),

            width=850,

            padding=15,

            bgcolor=SUPERFICIE_2,

            border=crear_borde(
                BORDE
            ),

            border_radius=15,
        )
    )

    # =====================================================
    # ACTIVIDADES
    # =====================================================

    for actividad in lista_actividades:

        nombre = actividad.get(
            "actividad",
            "Sin nombre"
        )

        fecha = actividad.get(
            "fecha_cierre_str",
            "Sin fecha"
        )

        tipo = actividad.get(
            "tipo",
            "Actividad"
        )

        url = actividad.get(
            "url",
            ""
        )

        tarjeta = ft.Container(

            content=ft.Column(

                controls=[

                    # -------------------------------------
                    # CABECERA DE ACTIVIDAD
                    # -------------------------------------

                    ft.Row(

                        controls=[

                            ft.Container(

                                content=ft.Text(
                                    "📝",
                                    size=22,
                                ),

                                width=42,

                                height=42,

                                alignment=(
                                    ft.Alignment(0, 0)
                                ),

                                bgcolor=AZUL_SUAVE,

                                border_radius=12,
                            ),

                            ft.Column(

                                controls=[

                                    ft.Text(
                                        nombre,
                                        size=17,
                                        weight=(
                                            ft.FontWeight.BOLD
                                        ),
                                        color=BLANCO,
                                    ),

                                    ft.Text(
                                        "Actividad académica",
                                        size=12,
                                        color=GRIS,
                                    ),
                                ],

                                spacing=2,

                                expand=True,
                            ),
                        ],

                        spacing=12,
                    ),

                    ft.Divider(
                        color=BORDE,
                        height=1,
                    ),

                    # -------------------------------------
                    # INFORMACIÓN
                    # -------------------------------------

                    ft.Row(

                        controls=[

                            ft.Container(

                                content=ft.Text(
                                    f"📅  {fecha}",
                                    size=13,
                                    color=TEXTO,
                                ),

                                padding=10,

                                bgcolor=SUPERFICIE_3,

                                border_radius=10,

                                expand=True,
                            ),

                            ft.Container(

                                content=ft.Text(
                                    f"📚  {tipo}",
                                    size=13,
                                    color=TEXTO,
                                ),

                                padding=10,

                                bgcolor=SUPERFICIE_3,

                                border_radius=10,

                                expand=True,
                            ),
                        ],

                        spacing=10,
                    ),

                    # -------------------------------------
                    # URL
                    # -------------------------------------

                    ft.Container(

                        content=ft.Text(
                            f"🔗 {url}",
                            size=11,
                            color=GRIS_OSCURO,
                            max_lines=2,
                            overflow=(
                                ft.TextOverflow.ELLIPSIS
                            ),
                        ),

                        padding=10,

                        bgcolor=FONDO,

                        border_radius=9,
                    ),
                ],

                spacing=10,
            ),

            width=850,

            padding=18,

            bgcolor=SUPERFICIE,

            border=crear_borde(
                BORDE
            ),

            border_radius=18,
        )

        contenido.controls.append(
            tarjeta
        )

    # =====================================================
    # SI NO HAY ACTIVIDADES
    # =====================================================

    if not lista_actividades:

        contenido.controls.append(

            ft.Container(

                content=ft.Column(

                    controls=[

                        ft.Text(
                            "📭",
                            size=42,
                        ),

                        ft.Text(
                            "NO HAY ACTIVIDADES",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=BLANCO,
                        ),

                        ft.Text(
                            "Moodle no devolvió eventos "
                            "en este momento.",
                            size=13,
                            color=GRIS,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],

                    horizontal_alignment=(
                        ft.CrossAxisAlignment.CENTER
                    ),

                    spacing=8,
                ),

                width=850,

                padding=35,

                bgcolor=SUPERFICIE,

                border=crear_borde(
                    BORDE
                ),

                border_radius=18,
            )
        )

    # =====================================================
    # BOTÓN REGRESAR
    # =====================================================

    boton = boton_regresar(
        page,
        moodle_session
    )

    # =====================================================
    # PANTALLA
    # =====================================================

    page.clean()

    page.add(

        ft.Column(

            controls=[

                contenido,

                ft.Container(

                    content=boton,

                    margin=5,
                ),
            ],

            expand=True,

            horizontal_alignment=(
                ft.CrossAxisAlignment.CENTER
            ),

            spacing=10,
        )
    )

    page.update()


# =========================================================
# ESTA SEMANA
# =========================================================

def seven_days(page, moodle_session):

    lista_actividades = (
        selec.actividades_actuales(
            moodle_session
        )
    )

    week.mostrar_actividades_semanal(
        page,
        lista_actividades
    )

    page.add(
        boton_regresar(
            page,
            moodle_session
        )
    )

    page.update()


# =========================================================
# ESTADO ACADÉMICO
# =========================================================

def estado_academico(page, moodle_session):

    lista_actividades = (
        selec.actividades_actuales(
            moodle_session
        )
    )

    lista_calificaciones = (
        calificaciones.get_grades_overview(
            moodle_session
        )
    )

    status.mostrar_estado_general(
        page=page,
        actividades=lista_actividades,
        moodle_session=moodle_session,
        calificaciones=lista_calificaciones
    )


# =========================================================
# EXPIRADAS
# =========================================================

def expiradas(page, moodle_session):

    lista_pendientes = (
        selec.actividades_actuales(
            moodle_session
        )
    )

    expired.act_vencidas(
        page,
        lista_pendientes
    )

    page.add(
        boton_regresar(
            page,
            moodle_session
        )
    )

    page.update()


# =========================================================
# PANTALLA PRINCIPAL
# =========================================================

def mostrar(page: ft.Page, moodle_session):

    from extras import work

    work.mostrar(
        page,
        moodle_session
    )
