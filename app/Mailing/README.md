# 📧 Mailing Module - Endpoints Documentation

Este módulo contiene los endpoints de marketing por email y manejo de contactos. Incluye integraciones con WIX y EmailOctopus.

## 🏗️ Arquitectura

El módulo utiliza una **arquitectura modular independiente** donde cada endpoint tiene una responsabilidad específica:

- **WIX Endpoint**: Recibe datos de formularios WIX → Guarda en BD + Envía a EmailOctopus
- **EmailOctopus Endpoint**: Maneja contactos directamente con EmailOctopus API
- **Función Octopus**: Lógica core para integración con EmailOctopus

## 📋 Endpoints Disponibles

### 1. WIX Records (`/wix/records`)

#### `GET /wix/records`
Obtiene todos los registros de la tabla WIX.

**Respuesta:**
```json
{
  "status": "success",
  "records": [
    {
      "id": 95,
      "nombre_apellido": "Juan Pérez",
      "empresa": "Mi Empresa SAC",
      "telefono2": "999888777",
      "ruc_dni": "20123456789",
      "correo": "juan@miempresa.com",
      "treq_requerimiento": "Cotización de equipos",
      "origen": "WIX",
      "submission_time": "2025-09-09T14:04:27Z"
    }
  ]
}
```

#### `POST /wix/records`
Inserta un nuevo registro desde WIX. **Guarda en BD con origen="WIX" y envía automáticamente a EmailOctopus.**

**Request Body:**
```json
{
  "nombre_apellido": "Juan Pérez",
  "empresa": "Mi Empresa SAC", 
  "telefono2": "999888777",
  "ruc_dni": "20123456789",
  "correo": "juan@miempresa.com",
  "treq_requerimiento": "Cotización de equipos"
}
```

**Respuesta Éxito:**
```json
{
  "status": "success",
  "message": "Registro insertado correctamente."
}
```

---

### 2. BD Records (`/bd/records`)

#### `GET /bd/records` 
Obtiene todos los registros de la base de datos (tabla WIX) incluyendo todos los orígenes.

**Respuesta:**
```json
{
  "status": "success", 
  "records": [
    {
      "id": 94,
      "origen": "TEST",
      "nombre_apellido": "Test Modular",
      "empresa": "Test Modular Company"
    },
    {
      "id": 95, 
      "origen": "WIX",
      "nombre_apellido": "Test WIX Fixed", 
      "empresa": "Test WIX Fixed Company"
    }
  ]
}
```

#### `POST /bd/records`
Inserta un registro en base de datos desde cualquier fuente. **Envía automáticamente a EmailOctopus y notifica condicionalmente.**

**CAMPOS OBLIGATORIOS:**
- `nombre_apellido` (string)
- `empresa` (string)
- `telefono2` (string)
- `correo` (string)

**CAMPOS OPCIONALES:**
- `ruc_dni` (string, puede ser null)
- `treq_requerimiento` (string, puede ser null)
- `origen` (string, default: "UNKNOWN")
- `asesor_tecnico` (string, se mapea a asesor_in en BD)
- `observacion` (string, puede ser null)
- `submission_time` (string ISO format, default: NOW())

**Request Body:**
```json
{
  "nombre_apellido": "Ana García",
  "empresa": "Tech Solutions SAC",
  "telefono2": "987654321",
  "correo": "ana@techsolutions.com",
  "ruc_dni": "20987654321",
  "treq_requerimiento": "Consulta sobre servicios",
  "origen": "MOBILE_APP",
  "asesor_tecnico": "Vanessa",
  "observacion": "Lead importante",
  "submission_time": "2025-09-09T14:04:27Z"
}
```

**Respuesta Éxito:**
```json
{
  "status": "success",
  "message": "Registro insertado correctamente en BD.",
  "record_id": 96,
  "origen": "MOBILE_APP",
  "notification_sent": true
}
```

**Ejemplos de Orígenes:**
- `"WIX"` - Formularios WIX (usado automáticamente por /wix/records)
- `"MOBILE_APP"` - Aplicación móvil
- `"API"` - Integración API externa
- `"MANUAL"` - Entrada manual por admin
- `"IMPORT_CSV"` - Importación masiva
- `"WEBSITE"` - Formulario web directo
- `"CRM"` - Sistema CRM integrado

---

### 3. EmailOctopus Contacts (`/octopus/contacts`)

#### `POST /octopus/contacts`
Envía un contacto directamente a EmailOctopus **sin tocar la base de datos.**

**Request Body:**
```json
{
  "correo": "juan@miempresa.com",
  "nombre_apellido": "Juan Pérez",
  "empresa": "Mi Empresa SAC",
  "ruc_dni": "20123456789"
}
```

**Respuesta Éxito:**
```json
{
  "status": "success",
  "message": "Contacto enviado exitosamente a EmailOctopus.",
  "octopus_status": 201,
  "octopus_response": {
    "id": "da3767b2-8da4-11f0-8208-495e1f264369",
    "email_address": "juan@miempresa.com",
    "fields": {
      "FirstName": "Juan Pérez",
      "COMPANY": "Mi Empresa SAC",
      "RUC": "20123456789"
    },
    "status": "subscribed"
  }
}
```

**Respuesta Error:**
```json
{
  "status": "warning",
  "message": "Error al enviar contacto a EmailOctopus.",
  "octopus_status": 400,
  "octopus_error": "Email already exists"
}
```

#### `GET /octopus/status`
Verifica el estado de la configuración de EmailOctopus.

**Respuesta:**
```json
{
  "status": "success",
  "octopus_config": {
    "api_key_configured": true,
    "list_id_configured": true,
    "ready": true
  }
}
```

---

## 🔧 Configuración

### Variables de Entorno Requeridas

```env
# EmailOctopus API
OCTOPUS_API_KEY=eo_ebaaa54ce54b71a8f43cf0f717834982c846dca447245f0dff1cb5880f57ed46
OCTOPUS_LIST_ID=4de8d66a-71ea-11ee-b78c-d7b693f1ca1a

# Base de Datos MySQL
MYSQL_USER=tu_usuario
MYSQL_PASSWORD=tu_contraseña  
MYSQL_HOST=tu_host
MYSQL_DATABASE=tu_database
```

## 🚀 Casos de Uso

### Caso 1: Formulario WIX (Recomendado)
Usar cuando los datos vienen directamente de un formulario WIX y quieres **guardar Y enviar a EmailOctopus**.

```bash
POST /wix/records
# Automáticamente: BD (origen="WIX") + EmailOctopus
```

### Caso 2: Otras Fuentes → BD + EmailOctopus + Notificación
Usar cuando tienes datos de **cualquier fuente** (app móvil, API, CSV, etc.) y quieres **guardar en BD + enviar a EmailOctopus + notificar condicionalmente**.

```bash
POST /bd/records
{
  "origen": "MOBILE_APP",  # Especifica la fuente
  "nombre_apellido": "...",
  "treq_requerimiento": "...",  # Si tiene contenido → envía notificación
  # ... otros campos
}
# BD + EmailOctopus + Notificación (si treq_requerimiento tiene contenido)
```

### Caso 3: Solo Marketing Email
Usar cuando solo quieres agregar un contacto a EmailOctopus **sin guardar en BD**.

```bash
POST /octopus/contacts  
# Solo EmailOctopus
```

### Caso 4: Verificar Configuración
Verificar que EmailOctopus esté configurado correctamente.

```bash
GET /octopus/status
```

### Caso 5: Flujo Completo Automático (Recomendado)
Para la mayoría de casos, usar el endpoint BD que ahora incluye todo:

```bash
# Un solo endpoint para todo el flujo
POST /bd/records
{
  "origen": "CRM",
  "treq_requerimiento": "Consulta importante",  # → Activa notificación
  "asesor_tecnico": "Juan",  # → Se asigna en BD
  # ... otros campos
}
# Resultado: BD + EmailOctopus + Notificación automática
```

### Caso 6: Solo EmailOctopus (Sin BD)
Si necesitas enviar solo a EmailOctopus sin guardar en BD:

```bash
POST /octopus/contacts {...}
```

## 📊 Mapeo de Campos

### WIX → Base de Datos (automático)
```
nombre_apellido → nombre_apellido
empresa → empresa
telefono2 → telefono2
ruc_dni → ruc_dni  
correo → correo
treq_requerimiento → treq_requerimiento
"WIX" → origen (automático)
NOW() → submission_time (automático)
```

### Cualquier Fuente → Base de Datos (manual)
```
# CAMPOS OBLIGATORIOS
nombre_apellido → nombre_apellido
empresa → empresa
telefono2 → telefono2
correo → correo

# CAMPOS OPCIONALES
ruc_dni → ruc_dni (puede ser null)
treq_requerimiento → treq_requerimiento (puede ser null)
asesor_tecnico → asesor_in (campo en BD)
observacion → observacion (puede ser null)
data["origen"] → origen (default: "UNKNOWN")
data["submission_time"] → submission_time (default: NOW())

# FUNCIONALIDADES AUTOMÁTICAS
→ Envío a EmailOctopus (siempre)
→ Notificación de lead (solo si treq_requerimiento tiene contenido)
```

### Cualquier Fuente → EmailOctopus
```
correo → email_address
nombre_apellido → fields.FirstName
empresa → fields.COMPANY
ruc_dni → fields.RUC
```

## ⚡ URLs de Producción

Base URL: `https://feedback-califcacion.onrender.com`

- `GET /wix/records` - Obtener registros WIX
- `POST /wix/records` - Enviar desde WIX (BD + EmailOctopus)
- `GET /bd/records` - Obtener todos los registros BD
- `POST /bd/records` - Guardar desde cualquier fuente (BD + EmailOctopus + Notificación)
- `POST /octopus/contacts` - Solo EmailOctopus
- `GET /octopus/status` - Estado EmailOctopus

## 🔍 Troubleshooting

### Error: "No se pudo conectar a la base de datos"
- Verificar variables `MYSQL_*` en `.env`
- Comprobar conectividad a la base de datos

### Error: "OCTOPUS_API_KEY y OCTOPUS_LIST_ID deben estar configuradas"  
- Verificar variables `OCTOPUS_*` en `.env`
- Usar `GET /octopus/status` para diagnóstico

### Timeout en WIX endpoint
- El endpoint WIX ahora usa llamadas directas (no HTTP requests internos)
- Si persiste, revisar conectividad de BD y EmailOctopus

## 📝 Notas de Desarrollo

- **Dual Import System**: Soporta tanto desarrollo (`from Mailing.octopus`) como producción (`from app.Mailing.octopus`)
- **Error Handling**: EmailOctopus failures no afectan el guardado en BD
- **Origen Tracking**: Campo `origen` permite rastrear la fuente de los datos
- **Independent Endpoints**: Cada endpoint puede usarse independientemente según necesidades

## ✨ Nuevas Funcionalidades (v2.0)

### 🚀 Endpoint BD Potenciado
El endpoint `/bd/records` ahora incluye funcionalidades completas:
- ✅ **Campos obligatorios reducidos**: Solo 4 campos esenciales
- ✅ **Soporte para asesor técnico**: Campo `asesor_tecnico` → `asesor_in` en BD
- ✅ **EmailOctopus automático**: Envío automático después de insertar en BD
- ✅ **Notificaciones condicionales**: Solo envía si `treq_requerimiento` tiene contenido
- ✅ **Submission time personalizable**: Acepta timestamp específico o usa NOW()
- ✅ **Campo observación**: Para notas adicionales del lead

### 📧 Sistema de Notificaciones Inteligente
- **Condicional**: Solo notifica si el lead tiene requerimientos específicos
- **Automático**: Se integra sin configuración adicional
- **Robusto**: Errores de notificación no afectan el flujo principal

### 🎯 Casos de Uso Recomendados
- **WIX**: Usar `/wix/records` (sin cambios, mantiene compatibilidad)
- **Otras fuentes**: Usar `/bd/records` (funcionalidad completa)
- **Solo marketing**: Usar `/octopus/contacts` (independiente)

### 🔄 Migración de Datos
- **Script incluido**: `pruebas/migrate_expoesca.py` para migrar datos de ExpoEsca
- **Mapeo automático**: Transforma campos automáticamente según origen
- **Manejo de errores**: Logging completo y recuperación ante fallos