
# controlador/grade.py

from controlador import explotation


def procesar_resultados(datos):

    resultados = []

    for curso in datos:

        nombre = curso["course"]
        filas = curso["filas"]

        nota_final = curso.get(
            "course_grade",
            ""
        )

        actividades = []

        for indice, textos in enumerate(filas):

            fila_texto = " ".join(textos).lower()

            # =========================================
            # IGNORAR FILA DE CÁLCULO TOTAL
            # =========================================

            if (
                "cálculo total (agregación)" in fila_texto
                and "total del curso" not in fila_texto
            ):
                continue

            # =========================================
            # NOTA FINAL DEL CURSO
            # =========================================

            if (
                "total del curso" in fila_texto
                or
                "course total" in fila_texto
                or
                "total curso" in fila_texto
            ):

                nota_final = textos[-1]

                print(
                    f"   📊 NOTA FINAL: {nota_final}"
                )

                continue

            # =========================================
            # IGNORAR ENCABEZADOS
            # =========================================

            nombre_actividad = textos[0]

            if nombre_actividad.lower() in [
                "actividad",
                "nombre",
                "elemento de calificación",
                "ítem de calificación"
            ]:
                continue

            # =========================================
            # CALIFICACIÓN
            # =========================================

            nota_actividad = textos[-1]

            # =========================================
            # METADATOS
            # =========================================

            metadatos = curso["metadatos"][indice]

            fecha_abre = metadatos.get(
                "fecha_abre"
            )

            fecha_cierra = metadatos.get(
                "fecha_cierra"
            )

            estado = metadatos.get(
                "estado"
            )

            completada = metadatos.get(
                "completada",
                False
            )

            nombre_lower = nombre_actividad.lower()

            if (
                nombre_lower.startswith("examen")
                or
                nombre_lower.startswith("cuestionario")
                or
                nombre_lower.startswith("h5p")
            ):

                if nota_actividad != "-":

                    completada = True

            # =========================================
            # ACTIVIDAD
            # =========================================

            actividad = {

                "activity": nombre_actividad,

                "grade": nota_actividad,

                "fecha_abre": fecha_abre,

                "fecha_cierra": fecha_cierra,

                "estado": estado,

                "completada": completada
            }

            actividades.append(
                actividad
            )

            if completada:

                print(
                    f"   ✅ COMPLETADA: "
                    f"{nombre_actividad}"
                )

        # =========================================
        # RESULTADO DE LA MATERIA
        # =========================================

        resultados.append(
            {
                "course": nombre,

                "grade": nota_final,

                "activities": actividades
            }
        )

        print(
            f"   ✅ Actividades detectadas: "
            f"{len(actividades)}"
        )

    # =============================================
    # RESULTADO FINAL
    # =============================================

    print("\n======================================")
    print("📊 RESULTADO FINAL")
    print("======================================")

    for resultado in resultados:

        print(
            f"📚 {resultado['course']}"
        )

        print(
            f"   Promedio: "
            f"{resultado['grade']}"
        )

        print(
            f"   Actividades: "
            f"{len(resultado['activities'])}"
        )

    return resultados


def todo(session):

    """
    Ejecuta todo el proceso.
    """

    datos = explotation.consultar_calificaciones(
        session
    )

    return procesar_resultados(
        datos
    )
