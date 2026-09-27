
# controlador/work.py
# UCNL MOODLE // OPS CENTER
# Panel principal

import os
import sys
import json
import datetime
import unicodedata

import flet as ft


# =========================================================
# RAÍZ DEL PROYECTO
# =========================================================

RAIZ_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if RAIZ_DIR not in sys.path:

    sys.path.append(
        RAIZ_DIR
    )


# =========================================================
# IMPORTACIONES
# =========================================================

from extras import principal

from configuracion.limit import (
    obtener_fecha_limite,
    calcular_tiempo_restante
)


# =========================================================
# CACHE
# =========================================================

CACHE_FILE = os.path.join(
    RAIZ_DIR,
    "cache",
    "calificaciones_cache.json"
)


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
VERDE_SUAVE = "#365314"

ROJO = "#F87171"
ROJO_SUAVE = "#3F1515"

AMARILLO = "#FACC15"
AMARILLO_SUAVE = "#3F3510"

AZUL = "#60A5FA"
AZUL_SUAVE = "#172554"

BORDE = "#26324A"


# =========================================================
# BORDE COMPATIBLE CON FLET
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
# LEER CACHE DE CALIFICACIONES
# =========================================================

def leer_cache_calificaciones():

    try:

        if not os.path.exists(
            CACHE_FILE
        ):

            return None

        with open(
            CACHE_FILE,
            "r",
            encoding="utf-8"
        ) as archivo:

            return json.load(
                archivo
            )

    except Exception as e:

        print(
            f"[-] Error leyendo cache: {e}"
        )

        return None


# =========================================================
# DATOS DEL CACHE
# =========================================================

def obtener_datos_cache():

    datos = leer_cache_calificaciones()

    if not datos:

        return {
            "materias": 0,
            "actividades": 0,
            "actualizado": "Sin sincronización"
        }

    materias = datos.get(
        "materias",
        0
    )

    actividades = datos.get(
        "actividades",
        0
    )

    actualizado = datos.get(
        "actualizado",
        "Sin fecha"
    )

    return {

        "materias":
            materias,

        "actividades":
            actividades,

        "actualizado":
            actualizado
    }


# =========================================================
# NORMALIZAR TEXTO
# =========================================================

def normalizar_texto(texto):

    if not texto:

        return ""

    texto = str(
        texto
    ).strip().lower()

    texto = unicodedata.normalize(
        "NFD",
        texto
    )

    texto = "".join(

        caracter

        for caracter in texto

        if unicodedata.category(
            caracter
        ) != "Mn"
    )

    return texto


# =========================================================
# OBTENER ACTIVIDADES SEMANALES
# =========================================================

def obtener_actividades_semana(
    actividades
):

    ahora = datetime.datetime.now()

    limite_superior = (
        ahora
        + datetime.timedelta(
            days=7
        )
    )

    resultado = []

    for actividad in actividades:

        limite = obtener_fecha_limite(
            actividad
        )

        if not limite:

            continue

        if (
            ahora
            <= limite
            <= limite_superior
        ):

            resultado.append(
                actividad
            )

    return resultado


# =========================================================
# OBTENER ACTIVIDADES VENCIDAS
# =========================================================

def obtener_actividades_vencidas(
    actividades
):

    resultado = []

    for actividad in actividades:

        limite = obtener_fecha_limite(
            actividad
        )

        if not limite:

            continue

        diferencia, estado = (
            calcular_tiempo_restante(
                limite
            )
        )

        if estado == "🔴 Vencida":

            resultado.append(
                actividad
            )

    return resultado


# =========================================================
# BOTÓN PRINCIPAL
# =========================================================

def crear_boton(
    icono,
    titulo,
    subtitulo,
    color,
    accion
):

    return ft.Container(

        content=ft.Column(

            controls=[

                ft.Text(
                    icono,
                    size=30
                ),

                ft.Text(
                    titulo,
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=BLANCO,
                ),

                ft.Text(
                    subtitulo,
                    size=12,
                    color=GRIS,
                ),
            ],

            spacing=5,
        ),

        padding=18,

        bgcolor=SUPERFICIE,

        border=crear_borde(
            color
        ),

        border_radius=18,

        expand=1,

        on_click=accion,
    )


# =========================================================
# MOSTRAR PANEL
# =========================================================

def mostrar(
    page: ft.Page,
    moodle_session
):

    # =====================================================
    # CONFIGURACIÓN
    # =====================================================

    page.clean()

    page.title = (
        "UCNL MOODLE // OPS CENTER"
    )

    page.bgcolor = FONDO

    page.padding = 20

    page.horizontal_alignment = (
        ft.CrossAxisAlignment.CENTER
    )

    page.vertical_alignment = (
        ft.MainAxisAlignment.START
    )

    # =====================================================
    # DATOS DEL CACHE
    # =====================================================

    cache = obtener_datos_cache()

    total_materias = cache[
        "materias"
    ]

    total_actividades = cache[
        "actividades"
    ]

    ultima_actualizacion = cache[
        "actualizado"
    ]

    # =====================================================
    # OBTENER ACTIVIDADES PARA SEMANA / EXPIRADAS
    # =====================================================

    actividades = []

    try:

        from configuracion import selec

        actividades = (
            selec.actividades_actuales(
                moodle_session
            )
        )

    except Exception as e:

        print(
            f"[-] No se pudieron obtener "
            f"las actividades: {e}"
        )

        actividades = []

    actividades_semana = (
        obtener_actividades_semana(
            actividades
        )
    )

    actividades_vencidas = (
        obtener_actividades_vencidas(
            actividades
        )
    )

    # =====================================================
    # ENCABEZADO
    # =====================================================

    encabezado = ft.Container(

        content=ft.Column(

            controls=[

                ft.Row(

                    controls=[

                        ft.Column(

                            controls=[

                                ft.Text(
                                    "⚡ UCNL",
                                    size=30,
                                    weight=(
                                        ft.FontWeight.BOLD
                                    ),
                                    color=VERDE,
                                ),

                                ft.Text(
                                    "MOODLE // OPS CENTER",
                                    size=18,
                                    weight=(
                                        ft.FontWeight.BOLD
                                    ),
                                    color=BLANCO,
                                ),

                                ft.Text(
                                    "Centro de control académico",
                                    size=13,
                                    color=GRIS,
                                ),
                            ],

                            spacing=2,

                            expand=True,
                        ),

                        ft.Container(

                            content=ft.Row(

                                controls=[

                                    ft.Text(
                                        "●",
                                        size=12,
                                        color=VERDE,
                                    ),

                                    ft.Text(
                                        "ONLINE",
                                        size=11,
                                        weight=(
                                            ft.FontWeight.BOLD
                                        ),
                                        color=VERDE,
                                    ),
                                ],

                                spacing=6,
                            ),

                            padding=10,

                            bgcolor=VERDE_SUAVE,

                            border_radius=12,

                            border=crear_borde(
                                VERDE
                            ),
                        ),
                    ]
                ),
            ],

            spacing=5,
        ),

        width=900,

        padding=22,

        bgcolor=SUPERFICIE,

        border=crear_borde(
            BORDE
        ),

        border_radius=22,
    )

    # =====================================================
    # RESUMEN
    # =====================================================

    resumen = ft.Row(

        controls=[

            ft.Container(

                content=ft.Column(

                    controls=[

                        ft.Text(
                            "📚",
                            size=25
                        ),

                        ft.Text(
                            str(total_materias),
                            size=28,
                            weight=(
                                ft.FontWeight.BOLD
                            ),
                            color=BLANCO,
                        ),

                        ft.Text(
                            "MATERIAS",
                            size=11,
                            weight=(
                                ft.FontWeight.BOLD
                            ),
                            color=GRIS,
                        ),
                    ],

                    spacing=2,
                ),

                padding=16,

                bgcolor=SUPERFICIE,

                border=crear_borde(
                    AZUL
                ),

                border_radius=16,

                expand=1,
            ),

            ft.Container(

                content=ft.Column(

                    controls=[

                        ft.Text(
                            "📝",
                            size=25
                        ),

                        ft.Text(
                            str(total_actividades),
                            size=28,
                            weight=(
                                ft.FontWeight.BOLD
                            ),
                            color=BLANCO,
                        ),

                        ft.Text(
                            "ACTIVIDADES",
                            size=11,
                            weight=(
                                ft.FontWeight.BOLD
                            ),
                            color=GRIS,
                        ),
                    ],

                    spacing=2,
                ),

                padding=16,

                bgcolor=SUPERFICIE,

                border=crear_borde(
                    VERDE
                ),

                border_radius=16,

                expand=1,
            ),

            ft.Container(

                content=ft.Column(

                    controls=[

                        ft.Text(
                            "⏰",
                            size=25
                        ),

                        ft.Text(
                            str(
                                len(
                                    actividades_semana
                                )
                            ),
                            size=28,
                            weight=(
                                ft.FontWeight.BOLD
                            ),
                            color=BLANCO,
                        ),

                        ft.Text(
                            "ESTA SEMANA",
                            size=11,
                            weight=(
                                ft.FontWeight.BOLD
                            ),
                            color=GRIS,
                        ),
                    ],

                    spacing=2,
                ),

                padding=16,

                bgcolor=SUPERFICIE,

                border=crear_borde(
                    AMARILLO
                ),

                border_radius=16,

                expand=1,
            ),

            ft.Container(

                content=ft.Column(

                    controls=[

                        ft.Text(
                            "🔴",
                            size=25
                        ),

                        ft.Text(
                            str(
                                len(
                                    actividades_vencidas
                                )
                            ),
                            size=28,
                            weight=(
                                ft.FontWeight.BOLD
                            ),
                            color=BLANCO,
                        ),

                        ft.Text(
                            "EXPIRADAS",
                            size=11,
                            weight=(
                                ft.FontWeight.BOLD
                            ),
                            color=GRIS,
                        ),
                    ],

                    spacing=2,
                ),

                padding=16,

                bgcolor=SUPERFICIE,

                border=crear_borde(
                    ROJO
                ),

                border_radius=16,

                expand=1,
            ),
        ],

        spacing=12,
    )

    # =====================================================
    # MENÚ
    # =====================================================

    menu = ft.Row(

        controls=[

            crear_boton(
                "📚",
                "CURSOS",
                "Mis materias",
                AZUL,
                lambda e:
                    principal.cursos(
                        page,
                        moodle_session
                    )
            ),

            crear_boton(
                "📅",
                "ACTIVIDADES",
                "Calendario Moodle",
                VERDE,
                lambda e:
                    principal.actividades(
                        page,
                        moodle_session
                    )
            ),

            crear_boton(
                "⏰",
                "ESTA SEMANA",
                "Próximas entregas",
                AMARILLO,
                lambda e:
                    principal.seven_days(
                        page,
                        moodle_session
                    )
            ),

            crear_boton(
                "🎓",
                "ESTADO ACADÉMICO",
                "Calificaciones",
                AZUL,
                lambda e:
                    principal.estado_academico(
                        page,
                        moodle_session
                    )
            ),

            crear_boton(
                "🔴",
                "EXPIRADAS",
                "Entregas vencidas",
                ROJO,
                lambda e:
                    principal.expiradas(
                        page,
                        moodle_session
                    )
            ),
        ],

        spacing=12,
    )

    # =====================================================
    # INFORMACIÓN DE SINCRONIZACIÓN
    # =====================================================

    sincronizacion = ft.Container(

        content=ft.Row(

            controls=[

                ft.Text(
                    "↻",
                    size=20,
                    color=VERDE,
                ),

                ft.Column(

                    controls=[

                        ft.Text(
                            "DATOS ACADÉMICOS",
                            size=11,
                            weight=(
                                ft.FontWeight.BOLD
                            ),
                            color=GRIS,
                        ),

                        ft.Text(
                            f"Última sincronización: "
                            f"{ultima_actualizacion}",
                            size=12,
                            color=TEXTO,
                        ),
                    ],

                    spacing=2,

                    expand=True,
                ),

                ft.Text(
                    "CACHE LOCAL",
                    size=10,
                    weight=(
                        ft.FontWeight.BOLD
                    ),
                    color=VERDE,
                ),
            ],

            spacing=10,
        ),

        width=900,

        padding=15,

        bgcolor=SUPERFICIE_2,

        border=crear_borde(
            BORDE
        ),

        border_radius=15,
    )

    # =====================================================
    # BOTÓN SALIR
    # =====================================================

    boton_salir = ft.Container(

        content=ft.Row(

            controls=[

                ft.Text(
                    "✕",
                    size=20,
                    weight=(
                        ft.FontWeight.BOLD
                    ),
                    color=ROJO,
                ),

                ft.Text(
                    "SALIR DEL PROGRAMA",
                    size=13,
                    weight=(
                        ft.FontWeight.BOLD
                    ),
                    color=ROJO,
                ),
            ],

            alignment=(
                ft.MainAxisAlignment.CENTER
            ),

            spacing=8,
        ),

        width=250,

        padding=12,

        bgcolor=ROJO_SUAVE,

        border=crear_borde(
            ROJO
        ),

        border_radius=14,

        on_click=lambda e:
            page.window.close(),
    )

    # =====================================================
    # ARMAR PANTALLA
    # =====================================================

    page.add(

        ft.Column(

            controls=[

                encabezado,

                ft.Container(
                    content=resumen,
                    width=900,
                    margin=5,
                ),

                ft.Container(
                    content=menu,
                    width=900,
                    margin=5,
                ),

                sincronizacion,

                ft.Container(
                    content=boton_salir,
                    margin=5,
                ),
            ],

            width=900,

            horizontal_alignment=(
                ft.CrossAxisAlignment.CENTER
            ),

            spacing=12,
        )
    )

    page.update()
