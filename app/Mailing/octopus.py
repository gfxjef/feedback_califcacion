import os
import requests

# Lee las variables de entorno (asegúrate de configurarlas en tu entorno de despliegue)
OCTOPUS_API_KEY = os.environ.get("OCTOPUS_API_KEY")
OCTOPUS_LIST_ID = os.environ.get("OCTOPUS_LIST_ID")
OCTOPUS_BASE_URL = "https://emailoctopus.com/api/2.0"

def add_contact_to_octopus(email, full_name):
    """
    Agrega un contacto a la lista de EmailOctopus usando la API v2.
    Usa `full_name` para el primer nombre y deja vacío el apellido.
    """
    url = f"{OCTOPUS_BASE_URL}/lists/{OCTOPUS_LIST_ID}/contacts"
    headers = {
        "Content-Type": "application/json",
        "X-EmailOctopus-ApiKey": OCTOPUS_API_KEY
    }
    payload = {
        "email_address": email,
        "first_name": full_name,
        "last_name": "",
        "consents_to_track": True
    }
    response = requests.post(url, json=payload, headers=headers)
    return response
