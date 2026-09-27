# Muestra las materias disponibles

from configuracion import base_datos


def materias():

    datos = base_datos.obtener_materias()

    print("\n======================================")
    print("📚 MATERIAS")
    print("======================================")

    print(
        f"Total de materias: {len(datos)}"
    )

    for materia in datos:

        materia_id = materia[0]
        nombre = materia[1]

        print(
            f"   📘 {nombre}"
        )

    return datos


if __name__ == "__main__":

    base_datos.iniciar()

    materias()
