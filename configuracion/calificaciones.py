
# configuracion/calificaciones.py
# UCNL MOODLE // OPS CENTER
# Obtiene, procesa y guarda las calificaciones

from configuracion import materias
from configuracion import relacion
from configuracion import base_datos


# =========================================================
# PROCESAR RESULTADOS
# =========================================================

def procesar_resultados(datos):

    resultados = []

    for curso in datos:

        nombre = curso["course"]

        filas = curso["filas"]

        nota_final = curso.get(
            "course_grade",
            "-"
        )

        actividades = []

        # =================================================
        # RELACIONAR METADATOS
        # =================================================

        metadatos_por_nombre = {}

        for metadato in curso.get(
            "metadatos",
            []
        ):

            nombre_meta = metadato.get(
                "nombre",
                ""
            )

            if nombre_meta:

                metadatos_por_nombre[
                    nombre_meta.lower()
                ] = metadato

        # =================================================
        # PROCESAR FILAS
        # =================================================

        for textos in filas:

            if not textos:
                continue

            fila_texto = " ".join(
                textos
            ).lower()

            # ---------------------------------------------
            # TOTAL DEL CURSO
            # ---------------------------------------------

            if (
                "total del curso" in fila_texto
                or "course total" in fila_texto
                or "total curso" in fila_texto
            ):

                nota_final = textos[-1]

                print(
                    f"   📊 NOTA FINAL: {nota_final}"
                )

                continue

            nombre_actividad = textos[0]

            # ---------------------------------------------
            # ENCABEZADOS
            # ---------------------------------------------

            if nombre_actividad.lower() in [
                "actividad",
                "nombre",
                "elemento de calificación",
                "ítem de calificación"
            ]:

                continue

            # ---------------------------------------------
            # CALIFICACIÓN
            # ---------------------------------------------

            nota_actividad = textos[-1]

            # ---------------------------------------------
            # METADATOS
            # ---------------------------------------------

            metadato = metadatos_por_nombre.get(
                nombre_actividad.lower(),
                {}
            )

            fecha_abre = metadato.get(
                "fecha_abre"
            )

            fecha_cierra = metadato.get(
                "fecha_cierra"
            )

            estado = metadato.get(
                "estado"
            )

            completada = metadato.get(
                "completada",
                False
            )

            # ---------------------------------------------
            # EXAMEN / CUESTIONARIO / H5P
            # ---------------------------------------------

            nombre_lower = (
                nombre_actividad.lower()
            )

            if (
                nombre_lower.startswith("examen")
                or nombre_lower.startswith("cuestionario")
                or nombre_lower.startswith("h5p")
            ):

                if nota_actividad != "-":

                    completada = True

            # ---------------------------------------------
            # GUARDAR ACTIVIDAD
            # ---------------------------------------------

            actividad = {

                "activity":
                    nombre_actividad,

                "grade":
                    nota_actividad,

                "fecha_abre":
                    fecha_abre,

                "fecha_cierra":
                    fecha_cierra,

                "estado":
                    estado,

                "completada":
                    completada

            }

            actividades.append(
                actividad
            )

            if completada:

                print(
                    f"   ✅ COMPLETADA: "
                    f"{nombre_actividad}"
                )

        # =================================================
        # GUARDAR CURSO
        # =================================================

        resultados.append({

            "course":
                nombre,

            "grade":
                nota_final,

            "activities":
                actividades

        })

        print(
            f"   ✅ Actividades detectadas: "
            f"{len(actividades)}"
        )

    return resultados


# =========================================================
# GUARDAR EN BASE DE DATOS
# =========================================================

def guardar_en_base_datos(
    datos,
    resultados
):

    print("\n======================================")
    print("💾 GUARDANDO EN BASE DE DATOS")
    print("======================================")

    base_datos.iniciar()

    resultados_por_materia = {}

    for resultado in resultados:

        resultados_por_materia[
            resultado["course"]
        ] = resultado

    # =====================================================
    # CADA CURSO
    # =====================================================

    for curso in datos:

        materia_id = curso["course_id"]

        nombre = curso["course"]

        resultado = resultados_por_materia.get(
            nombre,
            {}
        )

        calificacion = resultado.get(
            "grade",
            curso.get(
                "course_grade",
                "-"
            )
        )

        # -------------------------------------------------
        # MATERIA
        # -------------------------------------------------

        base_datos.guardar_materia(

            materia_id=materia_id,

            nombre=nombre,

            shortname=curso.get(
                "shortname",
                nombre
            ),

            url=curso.get(
                "url"
            ),

            periodo="2026-3",

            calificacion=calificacion

        )

        # -------------------------------------------------
        # ACTIVIDADES PROCESADAS
        # -------------------------------------------------

        actividades_resultado = {}

        for actividad in resultado.get(
            "activities",
            []
        ):

            actividades_resultado[
                actividad["activity"].lower()
            ] = actividad

        # -------------------------------------------------
        # METADATOS DE ACTIVIDADES
        # -------------------------------------------------

        for metadato in curso.get(
            "metadatos",
            []
        ):

            nombre_actividad = metadato.get(
                "nombre"
            )

            if not nombre_actividad:
                continue

            actividad_resultado = (
                actividades_resultado.get(
                    nombre_actividad.lower(),
                    {}
                )
            )

            grade = actividad_resultado.get(
                "grade",
                "-"
            )

            completada = actividad_resultado.get(
                "completada",
                metadato.get(
                    "completada",
                    False
                )
            )

            base_datos.guardar_actividad(

                materia_id=materia_id,

                nombre=nombre_actividad,

                calificacion=grade,

                fecha_abre=metadato.get(
                    "fecha_abre"
                ),

                fecha_cierra=metadato.get(
                    "fecha_cierra"
                ),

                estado=metadato.get(
                    "estado"
                ),

                completada=completada

            )

    print(
        "✅ Datos guardados correctamente."
    )


# =========================================================
# FUNCIÓN PRINCIPAL
# =========================================================

def todo(session):

    print("\n======================================")
    print("🎓 OBTENIENDO ESTADO ACADÉMICO")
    print("======================================")

    # =====================================================
    # ID DEL USUARIO
    # =====================================================

    user_id = relacion.get_user_id(
        session
    )

    if not user_id:

        print(
            "[-] No se pudo obtener "
            "el ID del usuario."
        )

        return []

    print(
        f"[+] Usuario detectado: {user_id}"
    )

    # =====================================================
    # MATERIAS
    # =====================================================

    cursos, sesskey = materias.get_user_courses(
        session
    )

    if not cursos:

        print(
            "[-] No se encontraron materias."
        )

        return []

    print(
        f"[+] Materias encontradas: "
        f"{len(cursos)}"
    )

    datos = []

    # =====================================================
    # PROCESAR MATERIAS
    # =====================================================

    for curso in cursos:

        course_id = curso["id"]

        nombre = curso["fullname"]

        print(
            "\n--------------------------------------"
        )

        print(
            f"📚 {nombre}"
        )

        print(
            f"   ID: {course_id}"
        )

        # -------------------------------------------------
        # CALIFICACIÓN DEL CURSO
        # -------------------------------------------------

        course_grade = (
            relacion.obtener_calificacion_curso(
                session,
                user_id,
                course_id
            )
        )

        print(
            f"   📊 Promedio del curso: "
            f"{course_grade}"
        )

        # -------------------------------------------------
        # FILAS DE CALIFICACIONES
        # -------------------------------------------------

        filas = (
            relacion.obtener_filas_calificaciones(
                session,
                user_id,
                course_id
            )
        )

        print(
            f"   📋 Filas de calificaciones: "
            f"{len(filas)}"
        )

        # -------------------------------------------------
        # ACTIVIDADES
        # -------------------------------------------------

        actividades = materias.obtener_actividades(
            session,
            user_id,
            course_id
        )

        metadatos = []

        for actividad in actividades:

            metadatos.append({

                "id_actividad":
                    actividad["id_actividad"],

                "url_actividad":
                    actividad["url"],

                "nombre":
                    actividad["textos"][0],

                "fecha_abre":
                    actividad["fecha_abre"],

                "fecha_cierra":
                    actividad["fecha_cierra"],

                "estado":
                    actividad["estado"],

                "completada":
                    actividad["completada"]

            })

            print(
                f"   🔗 ID actividad: "
                f"{actividad['id_actividad']}"
            )

            if actividad["fecha_abre"]:

                print(
                    f"   🟢 Abre: "
                    f"{actividad['fecha_abre']}"
                )

            if actividad["fecha_cierra"]:

                print(
                    f"   🔴 Cierra: "
                    f"{actividad['fecha_cierra']}"
                )

        # -------------------------------------------------
        # GUARDAR DATOS CRUDOS
        # -------------------------------------------------

        datos.append({

            "course":
                nombre,

            "course_id":
                course_id,

            "course_grade":
                course_grade,

            "shortname":
                curso.get(
                    "shortname",
                    nombre
                ),

            "url":
                curso.get(
                    "url"
                ),

            "filas":
                filas,

            "metadatos":
                metadatos

        })

    # =====================================================
    # PROCESAR
    # =====================================================

    resultados = procesar_resultados(
        datos
    )

    # =====================================================
    # SQLITE
    # =====================================================

    guardar_en_base_datos(
        datos,
        resultados
    )

    return resultados


# =========================================================
# PRUEBA DIRECTA
# =========================================================

if __name__ == "__main__":

    import requests

    session = requests.Session()

    todo(session)
