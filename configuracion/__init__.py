

# configuracion/__init__.py
# UCNL MOODLE // OPS CENTER

from configuracion import calificaciones
from configuracion import materias
from configuracion import relacion
from configuracion import limit
from configuracion import base_datos

from configuracion.session import secion


def iniciar(session):

    # ==========================================
    # SESIÓN
    # ==========================================

    if not secion(session):
        return None

    # ==========================================
    # BASE DE DATOS
    # ==========================================

    base_datos.iniciar()

    # ==========================================
    # DESCARGAR, PROCESAR Y GUARDAR
    # ==========================================

    resultados = calificaciones.todo(
        session
    )

    if not resultados:
        return None

    # ==========================================
    # MATERIAS DESDE SQL
    # ==========================================

    lista_materias = materias.materias()

    # ==========================================
    # ACTIVIDADES DESDE SQL
    # ==========================================

    actividades = (
        relacion.obtener_actividades()
    )

    # ==========================================
    # FILTRO DE 7 DÍAS
    # ==========================================

    estados = limit.limite(
        actividades
    )

    # ==========================================
    # RESULTADO
    # ==========================================

    return {

        "materias":
            lista_materias,

        "actividades":
            actividades,

        "estados":
            estados

    }
