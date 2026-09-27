
# UCNL MOODLE // ACTIVIDADES PRÓXIMAS A VENCER

import flet as ft

from configuracion import limit


def main(page: ft.Page):

    page.title = "UCNL MOODLE // Actividades"
    page.bgcolor = "#111118"
    page.padding = 20

    # =====================================================
    # OBTENER ACTIVIDADES
    # =====================================================

    actividades = limit.limite()

    # =====================================================
    # TÍTULO
    # =====================================================

    titulo = ft.Text(
        "⏰ ACTIVIDADES PRÓXIMAS A VENCER",
        size=22,
        weight=ft.FontWeight.BOLD
    )

    subtitulo = ft.Text(
        f"{len(actividades)} actividad(es) dentro de los próximos 7 días",
        size=14
    )

    # =====================================================
    # CONTENEDOR
    # =====================================================

    lista = ft.Column(
        spacing=12,
        scroll=ft.ScrollMode.AUTO
    )

    # =====================================================
    # SIN ACTIVIDADES
    # =====================================================

    if not actividades:

        lista.controls.append(
            ft.Container(
                content=ft.Text(
                    "✅ No hay actividades próximas a vencer.",
                    size=16
                ),
                padding=20
            )
        )

    # =====================================================
    # MOSTRAR ACTIVIDADES
    # =====================================================

    else:

        for actividad in actividades:

            tarjeta = ft.Container(

                content=ft.Column(
                    controls=[

                        ft.Text(
                            f"📚 {actividad['course']}",
                            size=16,
                            weight=ft.FontWeight.BOLD
                        ),

                        ft.Text(
                            f"📝 {actividad['activity']}",
                            size=15
                        ),

                        ft.Text(
                            f"🔴 Cierra: "
                            f"{actividad['fecha_cierra']}",
                            size=14
                        ),

                        ft.Text(
                            f"📌 Estado: "
                            f"{actividad['estado'] or 'Pendiente'}",
                            size=14
                        )

                    ],
                    spacing=6
                ),

                padding=15,

                border_radius=10,

                bgcolor="#1c1c27"
            )

            lista.controls.append(tarjeta)

    # =====================================================
    # PANTALLA
    # =====================================================

    page.add(

        ft.Column(
            controls=[

                titulo,

                subtitulo,

                ft.Divider(),

                lista

            ],
            expand=True
        )

    )


