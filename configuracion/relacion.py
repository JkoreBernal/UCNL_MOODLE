# Relaciona actividades con sus materias

from configuracion import base_datos


def obtener_actividades():

    datos = base_datos.obtener_actividades()

    actividades = []

    for fila in datos:

        (
            actividad_id,
            materia_id,
            materia,
            shortname,
            url,
            nombre,
            calificacion,
            fecha_abre,
            fecha_cierra,
            estado,
            completada
        ) = fila

        actividades.append({

            "materia_id": materia_id,

            "materia": materia,

            "actividad_id": actividad_id,

            "actividad": nombre,

            "calificacion": calificacion,

            "fecha_abre": fecha_abre,

            "fecha_cierra": fecha_cierra,

            "estado": estado,

            "completada": bool(completada)
        })

    return actividades
