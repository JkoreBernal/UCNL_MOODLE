
# controlador/main.py

import sys
import sqlite3
from pathlib import Path
from datetime import datetime

import requests


# =========================================================
# RUTA DEL PROYECTO
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(
    0,
    str(BASE_DIR)
)


# =========================================================
# IMPORTS
# =========================================================

from controlador import material
from controlador import grade
from controlador import explotation

from configuracion.session import secion


# =========================================================
# BASE DE DATOS
# =========================================================

DB_PATH = BASE_DIR / "ucnl.db"


# =========================================================
# CREAR BASE DE DATOS
# =========================================================

def crear_base_datos():

    conexion = sqlite3.connect(DB_PATH)

    cursor = conexion.cursor()

    # =====================================================
    # ACTIVAR FOREIGN KEYS
    # =====================================================

    cursor.execute("""
        PRAGMA foreign_keys = ON
    """)

    # =====================================================
    # USUARIOS
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            moodle_id TEXT NOT NULL UNIQUE,
            fecha_extraccion TEXT NOT NULL
        )
    """)

    # =====================================================
    # MATERIAS
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            moodle_id INTEGER NOT NULL UNIQUE,

            nombre TEXT NOT NULL,

            promedio TEXT,

            fecha_extraccion TEXT NOT NULL
        )
    """)

    # =====================================================
    # ACTIVIDADES
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS actividades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            moodle_id INTEGER NOT NULL UNIQUE,

            materia_id INTEGER NOT NULL,

            nombre TEXT,

            calificacion TEXT,

            fecha_abre TEXT,

            fecha_cierra TEXT,

            estado TEXT,

            completada INTEGER,

            url TEXT,

            textos TEXT,

            fecha_extraccion TEXT NOT NULL,

            FOREIGN KEY (materia_id)
                REFERENCES materias(id)
                ON DELETE CASCADE
        )
    """)

    # =====================================================
    # METADATOS
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metadatos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            actividad_id INTEGER NOT NULL UNIQUE,

            id_actividad INTEGER,

            url_actividad TEXT,

            fecha_abre TEXT,

            fecha_cierra TEXT,

            estado TEXT,

            completada INTEGER,

            FOREIGN KEY (actividad_id)
                REFERENCES actividades(id)
                ON DELETE CASCADE
        )
    """)

    # =====================================================
    # EXTRACCIONES
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS extracciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            fecha_hora TEXT NOT NULL,

            user_id TEXT,

            materias INTEGER,

            actividades INTEGER
        )
    """)

    conexion.commit()

    conexion.close()


# =========================================================
# GUARDAR / ACTUALIZAR DATOS
# =========================================================

def guardar_datos(
    user_id,
    datos,
    resultados
):

    conexion = sqlite3.connect(DB_PATH)

    cursor = conexion.cursor()

    cursor.execute("""
        PRAGMA foreign_keys = ON
    """)

    fecha_extraccion = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # =====================================================
    # USUARIO
    # =====================================================

    cursor.execute(
        """
        INSERT INTO usuarios (
            moodle_id,
            fecha_extraccion
        )
        VALUES (?, ?)

        ON CONFLICT(moodle_id)
        DO UPDATE SET
            fecha_extraccion = excluded.fecha_extraccion
        """,
        (
            str(user_id),
            fecha_extraccion
        )
    )

    # =====================================================
    # RESULTADOS POR MATERIA
    # =====================================================

    resultados_por_materia = {}

    for resultado in resultados:

        resultados_por_materia[
            resultado["course"]
        ] = resultado

    total_actividades = 0

    # =====================================================
    # MATERIAS
    # =====================================================

    for curso in datos:

        course_id = curso["course_id"]

        nombre = curso["course"]

        resultado = resultados_por_materia.get(
            nombre,
            {}
        )

        promedio = resultado.get(
            "grade",
            ""
        )

        # =================================================
        # INSERTAR / ACTUALIZAR MATERIA
        # =================================================

        cursor.execute(
            """
            INSERT INTO materias (
                moodle_id,
                nombre,
                promedio,
                fecha_extraccion
            )
            VALUES (?, ?, ?, ?)

            ON CONFLICT(moodle_id)
            DO UPDATE SET
                nombre = excluded.nombre,
                promedio = excluded.promedio,
                fecha_extraccion = excluded.fecha_extraccion
            """,
            (
                course_id,
                nombre,
                promedio,
                fecha_extraccion
            )
        )

        # =================================================
        # OBTENER ID INTERNO DE LA MATERIA
        # =================================================

        cursor.execute(
            """
            SELECT id
            FROM materias
            WHERE moodle_id = ?
            """,
            (
                course_id,
            )
        )

        resultado_materia = cursor.fetchone()

        if not resultado_materia:

            continue

        materia_id = resultado_materia[0]

        # =================================================
        # DATOS CRUDOS
        # =================================================

        filas = curso.get(
            "filas",
            []
        )

        metadatos = curso.get(
            "metadatos",
            []
        )

        actividades_resultado = resultado.get(
            "activities",
            []
        )

        # =================================================
        # ACTIVIDADES
        # =================================================

        for indice, fila in enumerate(filas):

            # -------------------------------------------------
            # METADATOS
            # -------------------------------------------------

            metadata = {}

            if indice < len(metadatos):

                metadata = metadatos[indice]

            # -------------------------------------------------
            # RESULTADO PROCESADO
            # -------------------------------------------------

            actividad_procesada = None

            if indice < len(
                actividades_resultado
            ):

                actividad_procesada = (
                    actividades_resultado[indice]
                )

            # -------------------------------------------------
            # NOMBRE
            # -------------------------------------------------

            nombre_actividad = ""

            if actividad_procesada:

                nombre_actividad = (
                    actividad_procesada.get(
                        "activity",
                        ""
                    )
                )

            elif fila:

                nombre_actividad = fila[0]

            # -------------------------------------------------
            # CALIFICACIÓN
            # -------------------------------------------------

            calificacion = ""

            if actividad_procesada:

                calificacion = (
                    actividad_procesada.get(
                        "grade",
                        ""
                    )
                )

            # -------------------------------------------------
            # DATOS DE ACTIVIDAD
            # -------------------------------------------------

            id_actividad = metadata.get(
                "id_actividad"
            )

            url = metadata.get(
                "url_actividad"
            )

            fecha_abre = metadata.get(
                "fecha_abre"
            )

            fecha_cierra = metadata.get(
                "fecha_cierra"
            )

            estado = metadata.get(
                "estado"
            )

            completada = metadata.get(
                "completada",
                False
            )

            # -------------------------------------------------
            # SI NO HAY ID, NO PODEMOS HACER UPSERT
            # -------------------------------------------------

            if id_actividad is None:

                continue

            # -------------------------------------------------
            # GUARDAR TEXTOS ORIGINALES
            # -------------------------------------------------

            textos = " | ".join(
                fila
            )

            # =================================================
            # INSERTAR / ACTUALIZAR ACTIVIDAD
            # =================================================

            cursor.execute(
                """
                INSERT INTO actividades (
                    moodle_id,
                    materia_id,
                    nombre,
                    calificacion,
                    fecha_abre,
                    fecha_cierra,
                    estado,
                    completada,
                    url,
                    textos,
                    fecha_extraccion
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

                ON CONFLICT(moodle_id)
                DO UPDATE SET

                    materia_id =
                        excluded.materia_id,

                    nombre =
                        excluded.nombre,

                    calificacion =
                        excluded.calificacion,

                    fecha_abre =
                        excluded.fecha_abre,

                    fecha_cierra =
                        excluded.fecha_cierra,

                    estado =
                        excluded.estado,

                    completada =
                        excluded.completada,

                    url =
                        excluded.url,

                    textos =
                        excluded.textos,

                    fecha_extraccion =
                        excluded.fecha_extraccion
                """,
                (
                    id_actividad,
                    materia_id,
                    nombre_actividad,
                    calificacion,
                    fecha_abre,
                    fecha_cierra,
                    estado,
                    int(bool(completada)),
                    url,
                    textos,
                    fecha_extraccion
                )
            )

            # =================================================
            # OBTENER ID INTERNO DE ACTIVIDAD
            # =================================================

            cursor.execute(
                """
                SELECT id
                FROM actividades
                WHERE moodle_id = ?
                """,
                (
                    id_actividad,
                )
            )

            resultado_actividad = cursor.fetchone()

            if not resultado_actividad:

                continue

            actividad_id = resultado_actividad[0]

            # =================================================
            # INSERTAR / ACTUALIZAR METADATOS
            # =================================================

            cursor.execute(
                """
                INSERT INTO metadatos (
                    actividad_id,
                    id_actividad,
                    url_actividad,
                    fecha_abre,
                    fecha_cierra,
                    estado,
                    completada
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)

                ON CONFLICT(actividad_id)
                DO UPDATE SET

                    id_actividad =
                        excluded.id_actividad,

                    url_actividad =
                        excluded.url_actividad,

                    fecha_abre =
                        excluded.fecha_abre,

                    fecha_cierra =
                        excluded.fecha_cierra,

                    estado =
                        excluded.estado,

                    completada =
                        excluded.completada
                """,
                (
                    actividad_id,
                    id_actividad,
                    url,
                    fecha_abre,
                    fecha_cierra,
                    estado,
                    int(bool(completada))
                )
            )

            total_actividades += 1

    # =====================================================
    # REGISTRAR EJECUCIÓN
    # =====================================================

    cursor.execute(
        """
        INSERT INTO extracciones (
            fecha_hora,
            user_id,
            materias,
            actividades
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            fecha_extraccion,
            str(user_id),
            len(datos),
            total_actividades
        )
    )

    # =====================================================
    # GUARDAR CAMBIOS
    # =====================================================

    conexion.commit()

    conexion.close()

    # =====================================================
    # INFORMACIÓN
    # =====================================================

    print("\n======================================")
    print("💾 BASE DE DATOS")
    print("======================================")

    print(
        "✅ Base de datos actualizada."
    )

    print(
        f"📚 Materias procesadas: "
        f"{len(datos)}"
    )

    print(
        f"📝 Actividades procesadas: "
        f"{total_actividades}"
    )

    print(
        f"🕐 Actualización: "
        f"{fecha_extraccion}"
    )

    print(
        f"📁 SQLite: "
        f"{DB_PATH}"
    )


# =========================================================
# MAIN
# =========================================================

def main():

    print("\n======================================")
    print("🎓 UCNL MOODLE // PRUEBA")
    print("======================================")

    # =====================================================
    # CREAR BASE DE DATOS
    # =====================================================

    crear_base_datos()

    # =====================================================
    # CREAR SESIÓN
    # =====================================================

    session = requests.Session()

    # =====================================================
    # LOGIN
    # =====================================================

    if not secion(session):

        print(
            "\n❌ No se pudo iniciar sesión."
        )

        return

    print(
        "\n✅ Sesión iniciada correctamente."
    )

    # =====================================================
    # OBTENER ID DEL USUARIO
    # =====================================================

    user_id = explotation.get_user_id(
        session
    )

    if not user_id:

        print(
            "\n❌ No se pudo obtener "
            "el ID del usuario."
        )

        return

    # =====================================================
    # OBTENER DATOS DE MOODLE
    # =====================================================

    datos = explotation.consultar_calificaciones(
        session
    )

    if not datos:

        print(
            "\n❌ No se obtuvieron datos."
        )

        return

    # =====================================================
    # PROCESAR CALIFICACIONES
    # =====================================================

    resultados = grade.procesar_resultados(
        datos
    )

    # =====================================================
    # GUARDAR / ACTUALIZAR SQLITE
    # =====================================================

    guardar_datos(
        user_id,
        datos,
        resultados
    )

    # =====================================================
    # MOSTRAR RESULTADO FINAL
    # =====================================================

    print("\n======================================")
    print("📊 RESULTADO FINAL")
    print("======================================")

    for curso in resultados:

        print(
            "\n--------------------------------------"
        )

        print(
            f"📚 {curso['course']}"
        )

        print(
            f"📊 Promedio: "
            f"{curso['grade']}"
        )

        print(
            f"📝 Actividades: "
            f"{len(curso['activities'])}"
        )

        for actividad in curso["activities"]:

            if actividad["completada"]:

                estado = "✅ COMPLETADA"

            else:

                estado = "⏳ PENDIENTE"

            print(
                f"   {estado} | "
                f"{actividad['activity']} | "
                f"Nota: {actividad['grade']}"
            )

    # =====================================================
    # FIN
    # =====================================================

    print("\n======================================")
    print("✅ PRUEBA TERMINADA")
    print("======================================")


# =========================================================
# EJECUCIÓN
# =========================================================

if __name__ == "__main__":

    main()
