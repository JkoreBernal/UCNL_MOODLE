
# base_datos.py
# Base de datos de UCNL MOODLE // OPS CENTER

import sqlite3


BASE_DATOS = "base_datos.db"


# ==========================================
# CONEXIÓN
# ==========================================

def conectar():

    return sqlite3.connect(BASE_DATOS)


# ==========================================
# CREAR BASE DE DATOS
# ==========================================

def crear_base_datos():

    conexion = conectar()
    cursor = conexion.cursor()

    # ==========================================
    # TABLA DE MATERIAS
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materias (

            id INTEGER PRIMARY KEY,

            nombre TEXT NOT NULL,

            shortname TEXT,

            url TEXT,

            periodo TEXT,

            calificacion TEXT

        )
    """)

    # ==========================================
    # TABLA DE ACTIVIDADES
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS actividades (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            materia_id INTEGER NOT NULL,

            nombre TEXT NOT NULL,

            calificacion TEXT,

            fecha_abre TEXT,

            fecha_cierra TEXT,

            estado TEXT,

            completada INTEGER DEFAULT 0,

            UNIQUE(materia_id, nombre),

            FOREIGN KEY (materia_id)
                REFERENCES materias(id)

        )
    """)

    # ==========================================
    # MIGRACIONES
    # ==========================================

    cursor.execute("""
        PRAGMA table_info(materias)
    """)

    columnas_materias = [
        columna[1]
        for columna in cursor.fetchall()
    ]

    # ------------------------------------------
    # shortname
    # ------------------------------------------

    if "shortname" not in columnas_materias:

        cursor.execute("""
            ALTER TABLE materias
            ADD COLUMN shortname TEXT
        """)

    # ------------------------------------------
    # url
    # ------------------------------------------

    if "url" not in columnas_materias:

        cursor.execute("""
            ALTER TABLE materias
            ADD COLUMN url TEXT
        """)

    # ------------------------------------------
    # periodo
    # ------------------------------------------

    if "periodo" not in columnas_materias:

        cursor.execute("""
            ALTER TABLE materias
            ADD COLUMN periodo TEXT
        """)

    # ------------------------------------------
    # calificacion
    # ------------------------------------------

    if "calificacion" not in columnas_materias:

        cursor.execute("""
            ALTER TABLE materias
            ADD COLUMN calificacion TEXT
        """)

    # ==========================================
    # MIGRACIÓN ACTIVIDADES
    # ==========================================

    cursor.execute("""
        PRAGMA table_info(actividades)
    """)

    columnas_actividades = [
        columna[1]
        for columna in cursor.fetchall()
    ]

    if "completada" not in columnas_actividades:

        cursor.execute("""
            ALTER TABLE actividades
            ADD COLUMN completada INTEGER DEFAULT 0
        """)

    # ==========================================
    # GUARDAR
    # ==========================================

    conexion.commit()
    conexion.close()

    print("✅ Base de datos creada correctamente.")


# ==========================================
# GUARDAR MATERIA
# ==========================================

def guardar_materia(
    materia_id,
    nombre,
    shortname=None,
    url=None,
    periodo=None,
    calificacion=None
):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO materias
        (
            id,
            nombre,
            shortname,
            url,
            periodo,
            calificacion
        )

        VALUES (?, ?, ?, ?, ?, ?)

        ON CONFLICT(id)
        DO UPDATE SET

            nombre = excluded.nombre,

            shortname = excluded.shortname,

            url = excluded.url,

            periodo = excluded.periodo,

            calificacion = excluded.calificacion
    """, (
        materia_id,
        nombre,
        shortname,
        url,
        periodo,
        calificacion
    ))

    conexion.commit()
    conexion.close()


# ==========================================
# GUARDAR ACTIVIDAD
# ==========================================

def guardar_actividad(
    materia_id,
    nombre,
    calificacion=None,
    fecha_abre=None,
    fecha_cierra=None,
    estado=None,
    completada=False
):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO actividades
        (
            materia_id,
            nombre,
            calificacion,
            fecha_abre,
            fecha_cierra,
            estado,
            completada
        )

        VALUES (?, ?, ?, ?, ?, ?, ?)

        ON CONFLICT(materia_id, nombre)

        DO UPDATE SET

            calificacion = excluded.calificacion,

            fecha_abre = excluded.fecha_abre,

            fecha_cierra = excluded.fecha_cierra,

            estado = excluded.estado,

            completada = excluded.completada
    """, (
        materia_id,
        nombre,
        calificacion,
        fecha_abre,
        fecha_cierra,
        estado,
        1 if completada else 0
    ))

    conexion.commit()
    conexion.close()


# ==========================================
# OBTENER MATERIAS
# ==========================================

def obtener_materias():

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            nombre,
            shortname,
            url,
            periodo,
            calificacion

        FROM materias

        ORDER BY nombre
    """)

    datos = cursor.fetchall()

    conexion.close()

    return datos


# ==========================================
# OBTENER ACTIVIDADES
# ==========================================

def obtener_actividades():

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT

            actividades.id,

            actividades.materia_id,

            materias.nombre,

            materias.shortname,

            materias.url,

            actividades.nombre,

            actividades.calificacion,

            actividades.fecha_abre,

            actividades.fecha_cierra,

            actividades.estado,

            actividades.completada

        FROM actividades

        INNER JOIN materias

            ON actividades.materia_id = materias.id

        ORDER BY

            materias.nombre,

            actividades.nombre
    """)

    datos = cursor.fetchall()

    conexion.close()

    return datos


# ==========================================
# OBTENER ACTIVIDADES DE UNA MATERIA
# ==========================================

def obtener_actividades_materia(materia_id):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT

            id,

            materia_id,

            nombre,

            calificacion,

            fecha_abre,

            fecha_cierra,

            estado,

            completada

        FROM actividades

        WHERE materia_id = ?

        ORDER BY nombre
    """, (
        materia_id,
    ))

    datos = cursor.fetchall()

    conexion.close()

    return datos


# ==========================================
# OBTENER ACTIVIDADES PENDIENTES
# ==========================================

def obtener_actividades_pendientes():

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT

            actividades.id,

            actividades.materia_id,

            materias.nombre,

            actividades.nombre,

            actividades.calificacion,

            actividades.fecha_abre,

            actividades.fecha_cierra,

            actividades.estado,

            actividades.completada

        FROM actividades

        INNER JOIN materias

            ON actividades.materia_id = materias.id

        WHERE actividades.completada = 0

        ORDER BY actividades.fecha_cierra
    """)

    datos = cursor.fetchall()

    conexion.close()

    return datos


# ==========================================
# LIMPIAR ACTIVIDADES
# ==========================================

def limpiar_actividades():

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        DELETE FROM actividades
    """)

    conexion.commit()
    conexion.close()


# ==========================================
# INICIAR
# ==========================================

def iniciar():

    crear_base_datos()


# ==========================================
# EJECUCIÓN DIRECTA
# ==========================================

if __name__ == "__main__":

    iniciar()
