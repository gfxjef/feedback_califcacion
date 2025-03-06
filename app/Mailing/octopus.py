import os
import requests

# Lee las variables de entorno
OCTOPUS_API_KEY = os.environ.get("OCTOPUS_API_KEY")
OCTOPUS_LIST_ID = os.environ.get("OCTOPUS_LIST_ID")
BASE_URL = "https://api.emailoctopus.com"  # URL base correcta

def add_contact_to_octopus(email_address, first_name, last_name, empresa, ruc_dni):
    """
    Agrega un contacto a la lista de EmailOctopus usando la API v2.

    Parámetros:
      - email_address (str): Correo electrónico del contacto.
      - first_name (str): Nombre (se asigna al campo "FirstName").
      - last_name (str): Apellido (se asigna al campo "LastName").
      - empresa (str): Nombre de la empresa (se asigna al campo "COMPANY").
      - ruc_dni (str): RUC o DNI (se asigna al campo "RUC").

    Retorna el objeto response de la petición.
    """
    url = f"{BASE_URL}/lists/{OCTOPUS_LIST_ID}/contacts"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OCTOPUS_API_KEY}"
    }
    payload = {
        "email_address": email_address,
        "fields": {
            "FirstName": first_name,
            "LastName": last_name,
            "COMPANY": empresa,
            "RUC": ruc_dni
        },
        "tags": [],
        "status": "subscribed"
    }
    response = requests.post(url, headers=headers, json=payload)
    return response
