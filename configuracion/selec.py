# Relaciona materias y actividades con SQLite

from configuracion import base_datos


def guardar_datos(resultados):

    if not resultados:
        return

    for curso in resultados:

        materia_id = curso.get("course_id")

        if materia_id is None:
            continue

        nombre = curso.get(
            "course",
            "Materia no identificada"
        )

        calificacion = curso.get(
            "grade",
            "-"
        )

        # ==========================================
        # MATERIA
        # ==========================================

        base_datos.guardar_materia(
            materia_id=materia_id,
            nombre=nombre,
            periodo="2026-3",
            calificacion=calificacion
        )

        # ==========================================
        # ACTIVIDADES
        # ==========================================

        actividades = curso.get(
            "activities",
            []
        )

        for actividad in actividades:

            base_datos.guardar_actividad(

                materia_id=materia_id,

                nombre=actividad.get(
                    "activity",
                    "Sin nombre"
                ),

                calificacion=actividad.get(
                    "grade",
                    "-"
                ),

                fecha_abre=actividad.get(
                    "fecha_abre"
                ),

                fecha_cierra=actividad.get(
                    "fecha_cierra"
                ),

                estado=actividad.get(
                    "estado"
                ),

                completada=actividad.get(
                    "completada",
                    False
                )
            )

    print("✅ Datos sincronizados con SQLite.")


def cursos():

    return base_datos.obtener_materias()


def actividades():

    return base_datos.obtener_actividades()
