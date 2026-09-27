# contenedores/status.py
import flet as ft
from configuracion.calificaciones import get_grades_overview


def mostrar_estado_general(
    page: ft.Page,
    actividades,
    moodle_session,
    calificaciones=None
):
    page.clean()

    # Contenedor dinámico donde se inyectarán las materias o el spinner
    lista_contenedor = ft.Column(spacing=8)

    # Estructura visual base de la pantalla
    contenido = ft.Column(
        controls=[
            ft.Text("🎓 ESTADO ACADÉMICO", size=26, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Container(
                content=ft.ListView(
                    controls=[lista_contenedor],
                    height=450,
                    spacing=8,
                    auto_scroll=False
                ),
                padding=10,
                border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=10
            ),
            ft.Divider(),
            ft.OutlinedButton(
                "⬅️ Regresar",
                on_click=lambda e: volver(e, page, moodle_session)
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=15
    )

    page.add(contenido)

    # Función interna que renderiza la lista de calificaciones recibidas
    def renderizar_calificaciones(datos):
        lista_contenedor.controls.clear()

        if datos:
            for cal in datos:
                course = cal.get("course", "Curso")
                grade = cal.get("grade", "N/A")
                actividades_materia = cal.get("activities", [])

                sub_items = []
                if actividades_materia:
                    for sub in actividades_materia:
                        sub_items.append(
                            ft.ListTile(
                                dense=True,
                                leading=ft.Icon(
                                    ft.Icons.ASSIGNMENT_OUTLINED,
                                    size=18,
                                    color=ft.Colors.BLUE_400
                                ),
                                title=ft.Text(sub.get("activity"), size=14),
                                trailing=ft.Text(
                                    sub.get("grade"),
                                    size=14,
                                    weight=ft.FontWeight.BOLD
                                )
                            )
                        )
                else:
                    sub_items.append(
                        ft.Padding(
                            padding=10,
                            content=ft.Text(
                                "Sin actividades registradas.",
                                size=13,
                                color=ft.Colors.GREY_500
                            )
                        )
                    )

                lista_contenedor.controls.append(
                    ft.ExpansionTile(
                        title=ft.Text(course, weight=ft.FontWeight.W_500, size=16),
                        subtitle=ft.Text(
                            f"Promedio Materia: {grade}",
                            color=ft.Colors.GREEN_400,
                            size=13
                        ),
                        leading=ft.Icon(ft.Icons.SCHOOL, color=ft.Colors.AMBER_600),
                        controls=sub_items
                    )
                )
        else:
            lista_contenedor.controls.append(
                ft.Text(
                    "❌ No se pudo cargar la información de calificaciones.",
                    color=ft.Colors.RED_400,
                    size=14
                )
            )

        page.update()

    # Si ya tenemos los datos cargados previamente los mostramos directamente
    if calificaciones is not None:
        renderizar_calificaciones(calificaciones)
    elif moodle_session:
        # Mostrar indicador de carga mientras scraping se ejecuta en segundo plano
        lista_contenedor.controls.append(
            ft.Column(
                controls=[
                    ft.ProgressRing(),
                    ft.Text("Obteniendo calificaciones de Moodle UCNL...", size=13)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                height=300
            )
        )
        page.update()

        # Tarea en hilo secundario para no congelar la UI
        def cargar_datos_hilo():
            res = get_grades_overview(moodle_session)
            renderizar_calificaciones(res)

        page.run_thread(cargar_datos_hilo)
    else:
        lista_contenedor.controls.append(
            ft.Text(
                "⚠️ Sesión no válida. Inicie sesión nuevamente.",
                color=ft.Colors.AMBER_600
            )
        )
        page.update()


def volver(e, page, moodle_session):
    from extras import principal
    principal.mostrar(page, moodle_session)