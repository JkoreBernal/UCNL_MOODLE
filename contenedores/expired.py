#expired.py
# --- Aquí se mostrarán las actividades expiradas/vencidas ---
import os
import datetime
from contenedores import UCNL
from configuracion.limit import obtener_fecha_limite, calcular_tiempo_restante, fecha_actual
import flet as ft 


def limpiar_pantalla():
    """Limpia la consola y dibuja el logo más la fecha actual."""
    os.system('clear' if os.name != 'nt' else 'cls')
    UCNL.logo_ucnl()
    
    hoy = fecha_actual()
    print(f"📅 Fecha de hoy: {hoy.strftime('%d/%m/%Y, %I:%M %p')}\n")


def mostrar_actividades_expiradas(actividades):
    """
    Limpia la pantalla y muestra únicamente las actividades cuya fecha límite 
    ya ha pasado (actividades expiradas) en la terminal.
    """
    limpiar_pantalla()
    ahora = datetime.datetime.now()
    
    actividades_expiradas = []
    for act in actividades:
        limite = obtener_fecha_limite(act)
        if limite and limite < ahora:
            actividades_expiradas.append(act)

    print("==========================================")
    print(f"⚠️ ACTIVIDADES EXPIRADAS / VENCIDAS ({len(actividades_expiradas)} encontradas)")
    print("==========================================\n")
    
    if not actividades_expiradas:
        print("🎉 ¡Excelente! No tienes actividades vencidas registradas.\n")
        return []

    for act in actividades_expiradas:
        limite = obtener_fecha_limite(act)
        dif, estado = calcular_tiempo_restante(limite)
        
        print(f"• [{act.get('tipo', 'Tarea')}] {act.get('actividad', 'Sin nombre')}")
        print(f"  ├─ Cierre: {act.get('fecha_cierre_str', 'Sin fecha')}")
        print(f"  ├─ Estado: {estado}")
        
        if dif:
            dias_pasados = abs(dif.days)
            print(f"  └─ Pasada por: {dias_pasados} {'día' if dias_pasados == 1 else 'días'}\n")
        else:
            print(f"  └─ Margen: Vencida\n")

    return actividades_expiradas


def act_vencidas(page: ft.Page, actividades):
    """
    Filtra las actividades vencidas y las renderiza en la interfaz gráfica de Flet.
    """
    limpiar_pantalla()
    ahora = datetime.datetime.now()

    # 1. Filtrar solo las vencidas (limite < ahora)
    actividades_expiradas = []
    for act in actividades:
        limite = obtener_fecha_limite(act)
        if limite and limite < ahora:
            actividades_expiradas.append(act)

    # 2. Mostrar resumen en terminal
    print("==========================================")
    print(f"⚠️ ACTIVIDADES VENCIDAS EN FLET ({len(actividades_expiradas)} encontradas)")
    print("==========================================\n")

    # 3. Cambiar vista en Flet
    page.clean()
    page.title = "UCNL MOODLE // EXPIRADAS"

    titulo = ft.Text(
        "⚠️ TAREAS EXPIRADAS / VENCIDAS",
        size=24,
        weight=ft.FontWeight.BOLD
    )

    lista = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10
    )

    # 4. Renderizar tarjetas de tareas expiradas
    for act in actividades_expiradas:
        materia = ft.Text(
            act.get("materia", act.get("modulo", "Materia no identificada")),
            size=18,
            weight=ft.FontWeight.BOLD
        )

        nombre = ft.Text(
            f"📝 {act.get('actividad', 'Sin nombre')}",
            size=15
        )

        fecha = ft.Text(
            f"📅 Cerró el: {act.get('fecha_cierre_str', 'Sin fecha')}",
            size=14
        )

        limite = obtener_fecha_limite(act)
        dif, estado = calcular_tiempo_restante(limite)

        dias_pasados = abs(dif.days) if dif else 0
        margen_txt = ft.Text(
            f"🚨 Vencida hace {dias_pasados} {'día' if dias_pasados == 1 else 'días'}",
            size=14,
            color=ft.colors.RED_400,
            weight=ft.FontWeight.BOLD
        )

        tarjeta = ft.Container(
            content=ft.Column(
                controls=[
                    materia,
                    nombre,
                    fecha,
                    ft.Text(f"📊 Estado: {estado}"),
                    margen_txt
                ],
                spacing=5
            ),
            padding=15,
            border=ft.border.all(1, ft.colors.RED_400),
            border_radius=10,
            width=500
        )

        lista.controls.append(tarjeta)

    # 5. Si no hay actividades expiradas
    if not actividades_expiradas:
        lista.controls.append(
            ft.Text(
                "🎉 ¡Excelente! No tienes actividades vencidas registradas.",
                size=16,
                weight=ft.FontWeight.BOLD
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

    return actividades_expiradas