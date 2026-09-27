#display.py-calendario

import requests
from configuracion.relacion import obtener_sesskey, obtener_eventos_api, procesar_eventos_moodle

def mostrar_actividades_calendario(session, base_url):
    """
    Coordina la obtención del sesskey, la llamada a la API y el despliegue
    ordenado de todas las entregas pendientes en la consola.
    """
    print("\n🔍 Autenticando solicitud y obteniendo sesskey...")
    sesskey = obtener_sesskey(session, base_url)
    
    if not sesskey:
        print("❌ No se pudo extraer el 'sesskey'. Verifica la sesión en Moodle.")
        return []

    print("📅 Consultando el endpoint AJAX del calendario de Moodle...")
    eventos_raw = obtener_eventos_api(session, base_url, sesskey)
    
    if not eventos_raw:
        print("⚠️ No se encontraron actividades o entregas próximas en el calendario.")
        return []

    actividades = procesar_eventos_moodle(eventos_raw)
    
    # Ordenar por timestamp de cierre (las más próximas primero)
    actividades.sort(key=lambda x: x['timestamp_cierre'] if x['timestamp_cierre'] else 0)

    print(f"\n=======================================================")
    print(f"📌 ACTIVIDADES Y FECHAS DE ENTREGA ({len(actividades)} encontradas)")
    print(f"=======================================================\n")

    for act in actividades:
        print(f"• [{act['tipo']}] {act['actividad']}")
        print(f"  ├─ Fecha Límite: {act['fecha_cierre_str']}")
        print(f"  ├─ Módulo:       {act['modulo']}")
        print(f"  └─ URL:          {act['url']}\n")

    return actividades