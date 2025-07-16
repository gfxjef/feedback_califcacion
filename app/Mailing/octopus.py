import requests
import os

# Configuración con datos de EmailOctopus desde variables de entorno
OCTOPUS_API_KEY = os.environ.get('OCTOPUS_API_KEY')
OCTOPUS_LIST_ID = os.environ.get('OCTOPUS_LIST_ID')
# Usamos el endpoint correcto sin /api/2.0
BASE_URL = "https://api.emailoctopus.com"

def add_contact_to_octopus(email_address, nombre_apellido, empresa, ruc_dni):
    """
    Agrega un contacto a la lista de EmailOctopus usando la API v2.
    
    Parámetros:
      - email_address (str): El email del contacto.
      - nombre_apellido (str): El nombre (se usará para "First name"; se dejará "Last name" vacío).
      - empresa (str): Se mapea al campo "COMPANY".
      - ruc_dni (str): Se mapea al campo "RUC".
    
    Retorna el objeto response de la petición.
    """
    # Validar que las credenciales estén configuradas
    if not OCTOPUS_API_KEY or not OCTOPUS_LIST_ID:
        raise ValueError("OCTOPUS_API_KEY y OCTOPUS_LIST_ID deben estar configuradas en las variables de entorno")
    
    url = f"{BASE_URL}/lists/{OCTOPUS_LIST_ID}/contacts"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OCTOPUS_API_KEY}"
    }
    payload = {
        "email_address": email_address,
        "fields": {
            "FirstName": nombre_apellido,  # Usamos el nombre completo en FirstName
            "LastName": "",                # No se separa apellido
            "COMPANY": empresa,
            "RUC": ruc_dni
        },
        "tags": [],
        "status": "subscribed"
    }
    response = requests.post(url, headers=headers, json=payload)
    return response

if __name__ == '__main__':
    # Datos de prueba
    email_address = "prueba@ejemplo.com"
    nombre_apellido = "Juan Perez"
    empresa = "Empresa Prueba"
    ruc_dni = "48052850"
    
    response = add_contact_to_octopus(email_address, nombre_apellido, empresa, ruc_dni)
    
    print("Status Code:", response.status_code)
    try:
        print("Response JSON:", response.json())
    except Exception as e:
        print("Error al parsear la respuesta:", e)
