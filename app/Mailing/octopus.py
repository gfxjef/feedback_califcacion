import os
import requests

# Lee las variables de entorno
OCTOPUS_API_KEY = os.environ.get("OCTOPUS_API_KEY")
OCTOPUS_LIST_ID = os.environ.get("OCTOPUS_LIST_ID")
BASE_URL = "https://api.emailoctopus.com"  # URL base correcta

def add_contact_to_octopus(data):
    """
    Recibe un diccionario 'data' con:
      data["correo"]
      data["nombre_apellido"]
      data["empresa"]
      data["telefono2"]
      data["ruc_dni"]
      data["treq_requerimiento"]

    Y los mapea a los campos de EmailOctopus.
    """
    url = f"{BASE_URL}/lists/{OCTOPUS_LIST_ID}/contacts"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OCTOPUS_API_KEY}"
    }
    payload = {
        "email_address": data["correo"],
        "fields": {
            # Ajusta los nombres según los tags definidos en tu lista
            "first_name": data["nombre_apellido"],
            "COMPANY": data["empresa"],
            "RUC": data["ruc_dni"],
            "telefono": data["telefono2"],
            "REQUIREMENT": data["treq_requerimiento"]
        },
        "tags": [],
        "status": "subscribed"
    }
    response = requests.post(url, headers=headers, json=payload)
    return response
