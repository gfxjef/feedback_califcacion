import os
import requests

# Lee las variables de entorno
OCTOPUS_API_KEY = os.environ.get("OCTOPUS_API_KEY")
OCTOPUS_LIST_ID = os.environ.get("OCTOPUS_LIST_ID")
BASE_URL = "https://api.emailoctopus.com"  # URL base correcta

def add_contact_to_octopus(email, full_name):
    """
    Agrega un contacto a la lista de EmailOctopus usando la API v2.
    Usa `full_name` para el primer nombre y deja vacío el apellido.
    """
    url = f"{BASE_URL}/lists/{OCTOPUS_LIST_ID}/contacts"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OCTOPUS_API_KEY}"
    }
    payload = {
        "email_address": email,
        "fields": {
            "first_name": full_name,
            "last_name": ""
        },
        "tags": [],
        "status": "subscribed"
    }
    response = requests.post(url, headers=headers, json=payload)
    return response
