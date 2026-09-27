
# configuracion/limit.py
# Filtra actividades próximas a vencer
# usando base_datos.db

import sqlite3
from datetime import datetime, timedelta


# =========================================================
# BASE DE DATOS
# =========================================================

DB_PATH = "/home/kore/Proyectos/UCNL/base_datos.db"


# =========================================================
# MESES
# =========================================================

MESES = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12
}


# =========================================================
# CONVERTIR FECHA
# =========================================================

def convertir_fecha(fecha):

    if not fecha:
        return None

    try:

        # Ejemplo:
        # lunes, 27 de septiembre de 2026, 23:59

        partes = fecha.lower().replace(",", "").split()

        dia = int(partes[1])

        mes = MESES[partes[3]]

        año = int(partes[5])

        hora = partes[6]

        return datetime.strptime(
            f"{dia}/{mes}/{año} {hora}",
            "%d/%m/%Y %H:%M"
        )

    except (
        ValueError,
        IndexError,
        KeyError
    ):

        return None


# =========================================================
# OBTENER ACTIVIDADES
# =========================================================

def obtener_actividades():

    conexion = sqlite3.connect(DB_PATH)

    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            actividades.id,
            actividades.nombre,
            actividades.calificacion,
            actividades.fecha_abre,
            actividades.fecha_cierra,
            actividades.estado,
            actividades.completada,
            materias.nombre
        FROM actividades
        INNER JOIN materias
            ON actividades.materia_id = materias.id
        ORDER BY actividades.fecha_cierra
    """)

    filas = cursor.fetchall()

    conexion.close()

    actividades = []

    for fila in filas:

        (
            id_actividad,
            nombre,
            calificacion,
            fecha_abre,
            fecha_cierra,
            estado,
            completada,
            materia
        ) = fila

        actividades.append({
            "id_actividad": id_actividad,
            "activity": nombre,
            "grade": calificacion,
            "fecha_abre": fecha_abre,
            "fecha_cierra": fecha_cierra,
            "estado": estado,
            "completada": bool(completada),
            "course": materia
        })

    return actividades


# =========================================================
# FILTRAR ACTIVIDADES
# =========================================================

def limite(actividades=None):

    if actividades is None:
        actividades = obtener_actividades()

    ahora = datetime.now()

    limite_fecha = ahora + timedelta(days=7)

    resultado = []

    for actividad in actividades:

        if actividad.get("completada") is True:
            continue

        fecha = convertir_fecha(
            actividad.get("fecha_cierra")
        )

        if fecha is None:
            continue

        if fecha < ahora:
            continue

        if fecha > limite_fecha:
            continue

        resultado.append(actividad)

    return resultado


# =========================================================
# PRUEBA DIRECTA
# =========================================================

if __name__ == "__main__":

    actividades = limite()

    print("\n======================================")
    print("⏰ ACTIVIDADES PRÓXIMAS A VENCER")
    print("======================================")

    if not actividades:

        print("✅ No hay actividades próximas a vencer.")

    else:

        for actividad in actividades:

            print("\n--------------------------------------")

            print(
                f"📚 Materia: "
                f"{actividad['course']}"
            )

            print(
                f"📝 Actividad: "
                f"{actividad['activity']}"
            )

            print(
                f"🔴 Cierra: "
                f"{actividad['fecha_cierra']}"
            )

            print(
                f"📌 Estado: "
                f"{actividad['estado'] or 'Pendiente'}"
            )
