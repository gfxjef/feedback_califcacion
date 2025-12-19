# API de Leads - Documentacion

**URL Base:** `https://feedback-califcacion.onrender.com`

---

## 1. Obtener Leads

```
GET /sync/leads
```

### Filtros Opcionales

| Parametro | Tipo | Ejemplo | Descripcion |
|-----------|------|---------|-------------|
| `asignado` | bool | `true` o `false` | Solo asignados o sin asignar |
| `asesor` | string | `Giovanna Ramirez` | Filtrar por asesor |
| `origen` | string | `WIX` | Filtrar por origen |
| `fecha_desde` | date | `2025-12-01` | Desde esta fecha |
| `fecha_hasta` | date | `2025-12-31` | Hasta esta fecha |
| `limit` | int | `50` | Maximo de registros (default: todos) |
| `offset` | int | `0` | Para paginacion |

### Ejemplos

```bash
# TODOS los leads (por defecto retorna todos)
curl "https://feedback-califcacion.onrender.com/sync/leads"

# Solo sin asignar
curl "https://feedback-califcacion.onrender.com/sync/leads?asignado=false"

# Solo asignados
curl "https://feedback-califcacion.onrender.com/sync/leads?asignado=true"

# Limitar a 50 resultados (opcional)
curl "https://feedback-califcacion.onrender.com/sync/leads?limit=50"
```

### Respuesta

```json
{
  "status": "success",
  "total": 329,
  "returned": 329,
  "offset": 0,
  "limit": 10000,
  "filters": {
    "asignado": null,
    "asesor": null,
    "fecha_desde": null,
    "fecha_hasta": null,
    "origen": null
  },
  "leads": [
    {
      "id": 354,
      "nombre_apellido": "July Angela Jara",
      "empresa": "MINERA CRC",
      "correo": "jjaray@mineracrc.com",
      "telefono2": "934654322",
      "ruc_dni": "20603823613",
      "origen": "WIX",
      "treq_requerimiento": "cotizacion de multiparametros hanna",
      "submission_time": "2025-12-17T19:51:17",
      "observacion": null,
      "asignado": false,
      "asesor_in": "",
      "fecha_asignacion": null,
      "siek_cliente": 1,
      "ia_cliente_doc": "20603823614",
      "ia_cliente_razon_social": "MINERA CRC S.A.C.",
      "ia_cliente_sector": "Mineria",
      "sync_status": "pendiente",
      "sync_sent_at": null,
      "sync_confirmed_at": null
    }
  ]
}
```

---

## 2. Confirmar Recepcion de Lead (Para Sistema Externo)

Este endpoint lo debe llamar el sistema externo para confirmar que recibio el lead.

```
POST /sync/confirm
```

### Body (JSON)

```json
{
  "record_id": 354,
  "external_id": "ID-EXTERNO-123"
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `record_id` | int | SI | ID del lead en nuestra BD |
| `external_id` | string | NO | ID que asigno el sistema externo |

### Respuesta Exitosa

```json
{
  "status": "success",
  "message": "Lead 354 confirmado exitosamente",
  "record_id": 354,
  "external_id": "ID-EXTERNO-123",
  "already_confirmed": false
}
```

### Respuesta Error

```json
{
  "status": "error",
  "message": "Lead 999 no encontrado"
}
```

---

## 3. Campos del Lead

### Datos del Contacto
| Campo | Descripcion |
|-------|-------------|
| `id` | ID unico del lead |
| `nombre_apellido` | Nombre completo |
| `empresa` | Nombre de la empresa |
| `correo` | Email de contacto |
| `telefono2` | Telefono |
| `ruc_dni` | RUC o DNI |
| `treq_requerimiento` | Lo que solicita el cliente |
| `origen` | De donde vino (WIX, expokossodo, etc) |
| `submission_time` | Fecha/hora de registro |
| `observacion` | Notas adicionales |

### Estado de Asignacion
| Campo | Descripcion |
|-------|-------------|
| `asignado` | `true` o `false` (campo calculado) |
| `asesor_in` | Nombre del asesor asignado |
| `fecha_asignacion` | Cuando se asigno |

### Estado de Sincronizacion
| Campo | Valor | Descripcion |
|-------|-------|-------------|
| `sync_status` | `pendiente` | Aun no procesado |
| `sync_status` | `enviado` | Enviado al sistema externo |
| `sync_status` | `confirmado` | Sistema externo confirmo recepcion |
| `sync_sent_at` | datetime | Cuando se envio |
| `sync_confirmed_at` | datetime | Cuando se confirmo |

### Datos de IA (Gemini)
| Campo | Valor | Descripcion |
|-------|-------|-------------|
| `siek_cliente` | 0 | Sin datos |
| `siek_cliente` | 1 | Datos encontrados por IA |
| `siek_cliente` | 2 | Cliente existe en SIEK |
| `ia_cliente_doc` | RUC | RUC encontrado por IA |
| `ia_cliente_sector` | Texto | Sector (Mineria, Farmaceutica, etc) |
| `ia_cliente_razon_social` | Texto | Razon social completa |

---

## 4. Estadisticas

```
GET /sync/leads/stats
```

### Respuesta

```json
{
  "status": "success",
  "statistics": {
    "total": 329,
    "asignados": 197,
    "sin_asignar": 132,
    "porcentaje_asignados": 59.9,
    "por_asesor": {
      "Jefferson Camacho": 107,
      "Azucena Chuquilin": 24
    },
    "por_origen": {
      "wix": 132,
      "expokossodo": 84
    }
  }
}
```

---

## 5. Lista de Asesores

```
GET /sync/leads/asesores
```

### Respuesta

```json
{
  "status": "success",
  "asesores": [
    "Azucena Chuquilin",
    "Giovanna Ramirez",
    "Jefferson Camacho"
  ],
  "total": 14
}
```
