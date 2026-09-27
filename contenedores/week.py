# week.py - muestra las tareas para esta semana

import os
import datetime
import flet as ft

from contenedores import UCNL

# Importar las funciones directamente desde el archivo limit.py
from configuracion.limit import (
    obtener_fecha_limite,
    calcular_tiempo_restante,
    fecha_actual
)

def limpiar_pantalla():
    """Limpia la consola y dibuja el logo más la fecha actual."""

    os.system('clear' if os.name != 'nt' else 'cls')

    if hasattr(UCNL, 'logo_ucnl'):
        UCNL.logo_ucnl()

    hoy = fecha_actual()
    print(f"📅 Fecha de hoy: {hoy.strftime('%d/%m/%Y, %I:%M %p')}\n")


def mostrar_actividades_semanal(page: ft.Page, actividades: list):

    limpiar_pantalla()

    ahora = datetime.datetime.now()

    # 1. Filtrar próximos 7 días
    actividades_semana = []

    for act in actividades:
        limite = obtener_fecha_limite(act)
        if limite and (ahora <= limite <= ahora + datetime.timedelta(days=7)):
            actividades_semana.append(act)

    # 2. Mostrar en terminal (logs)
    print("==========================================")
    print(f"📅 ACTIVIDADES DE ESTA SEMANA ({len(actividades_semana)} encontradas)")
    print("==========================================\n")

    for act in actividades_semana:
        limite = obtener_fecha_limite(act)
        dif, estado = calcular_tiempo_restante(limite)

        print(f"📚 MATERIA: {act.get('materia', 'Sin materia')}")
        print(f"📝 TAREA: {act.get('actividad', 'Sin nombre')}")
        print(f"📅 Cierre: {act.get('fecha_cierre_str', 'Sin fecha')}")
        print(f"📊 Estado: {estado}")

        if dif and dif.total_seconds() >= 0:
            horas = int(dif.seconds // 3600)
            print(f"⏳ Margen: {dif.days} días y {horas} horas restantes")

        print("------------------------------------------")

    # 3. Dibujar la pantalla en Flet
    page.clean()
    page.title = "UCNL MOODLE // SEMANAL"

    titulo = ft.Text(
        "⏰ ACTIVIDADES DE ESTA SEMANA",
        size=28,
        weight=ft.FontWeight.BOLD
    )

    lista = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10
    )

    # 4. Construir las tarjetas de actividades
    for act in actividades_semana:
        materia = ft.Text(
            act.get("materia", "Materia no identificada"),
            size=18,
            weight=ft.FontWeight.BOLD
        )
        nombre = ft.Text(
            f"📝 {act.get('actividad', 'Sin nombre')}",
            size=15
        )
        fecha = ft.Text(
            f"📅 {act.get('fecha_cierre_str', 'Sin fecha')}",
            size=14
        )

        limite = obtener_fecha_limite(act)
        dif, estado = calcular_tiempo_restante(limite)

        estado_txt = ft.Text(f"📊 {estado}")

        margen = ""
        if dif and dif.total_seconds() >= 0:
            horas = int(dif.seconds // 3600)
            margen = f"⏳ {dif.days} días y {horas} horas restantes"

        margen_txt = ft.Text(margen, size=14)

        tarjeta = ft.Container(
            content=ft.Column(
                controls=[
                    materia,
                    nombre,
                    fecha,
                    estado_txt,
                    margen_txt
                ],
                spacing=5
            ),
            padding=15,
            width=500
        )

        lista.controls.append(tarjeta)

    # 5. Si no hay actividades
    if not actividades_semana:
        lista.controls.append(
            ft.Text(
                "🎉 ¡No tienes entregas pendientes para los próximos 7 días!",
                size=18
            )
        )

    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    page.add(
        ft.Column(
            controls=[
                titulo,
                lista
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
        )
    )

    # Nota: No olvides refrescar la vista al finalizar la renderización
    page.update()

    return actividades_semana