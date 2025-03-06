import os
import requests

# Lee las variables de entorno (asegúrate de configurarlas en producción)
OCTOPUS_API_KEY = os.environ.get("OCTOPUS_API_KEY")
OCTOPUS_LIST_ID = os.environ.get("OCTOPUS_LIST_ID")
BASE_URL = "https://api.emailoctopus.com"  # URL base correcta

def add_contact_to_octopus(data):
    """
    Agrega un contacto a la lista de EmailOctopus usando la API v2.
    
    Se espera que 'data' sea un diccionario con los siguientes campos:
      - "correo": Email address del contacto.
      - "nombre_apellido": Nombre completo, se mapea a "First name".
      - "empresa": Se mapea a "COMPANY".
      - "telefono2": Se mapea a "Phone".
      - "ruc_dni": Se mapea a "RUC".
      - "treq_requerimiento": Se mapea a "Requerimiento".
    
    Retorna el objeto response de la petición.
    """
    url = f"{BASE_URL}/lists/{OCTOPUS_LIST_ID}/contacts"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OCTOPUS_API_KEY}"
    }
    payload = {
        "email_address": data["correo"],
        "fields": {
            "First name": data["nombre_apellido"],
            "COMPANY": data["empresa"],
            "RUC": data["ruc_dni"],
            "Phone": data["telefono2"],
            "Requerimiento": data["treq_requerimiento"]
        },
        "tags": [],
        "status": "subscribed"
    }
    response = requests.post(url, headers=headers, json=payload)
    return response
