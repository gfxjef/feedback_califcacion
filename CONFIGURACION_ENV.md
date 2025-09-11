# 🔐 CONFIGURACIÓN DE VARIABLES DE ENTORNO

## ✅ **CREDENCIALES HARDCODEADAS ELIMINADAS**

Se han eliminado todas las contraseñas y credenciales hardcodeadas de los siguientes archivos:

- ✅ `app/Mailing/octopus.py` - API keys de EmailOctopus 
- ✅ `app/login.py` - Credenciales de base de datos
- ✅ `app/run_app.py` - Todas las credenciales
- ✅ `test_filtro_directo.py` - Credenciales de testing

## 📋 **ARCHIVO .env REQUERIDO**

Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```env
# ==============================================
# CONFIGURACIÓN DE BASE DE DATOS MYSQL
# ==============================================
MYSQL_USER=atusalud_atusalud
MYSQL_PASSWORD=kmachin1
MYSQL_HOST=atusaludlicoreria.com
MYSQL_DATABASE=atusalud_kossomet
MYSQL_PORT=3306

# ==============================================
# CONFIGURACIÓN DE EMAIL SMTP (GMAIL)
# ==============================================
EMAIL_USER=jcamacho@kossodo.com
EMAIL_PASSWORD=jxehvsnsgwirlleq

# ==============================================
# CONFIGURACIÓN DE EMAILOCTOPUS
# ==============================================
OCTOPUS_API_KEY=eo_ebaaa54ce54b71a8f43cf0f717834982c846dca447245f0dff1cb5880f57ed46
OCTOPUS_LIST_ID=4de8d66a-71ea-11ee-b78c-d7b693f1ca1a

# ==============================================
# CONFIGURACIÓN DE NOTIFICACIONES DE LEADS
# ==============================================
LEAD_NOTIFICATION_EMAIL=encargada@kossodo.com

# ==============================================
# OTRAS CONFIGURACIONES OPCIONALES
# ==============================================
PORT=3000
FLASK_ENV=development
FLASK_DEBUG=True
```

## 🚀 **PASOS DE INSTALACIÓN**

1. **Instalar python-dotenv** (si no está instalado):
   ```bash
   pip install python-dotenv
   ```

2. **Crear archivo .env**:
   ```bash
   # Copia el contenido de arriba en un archivo llamado .env
   touch .env
   # Luego edita el archivo y pega el contenido
   ```

3. **Verificar .gitignore**:
   ```bash
   # Asegúrate de que .env esté en .gitignore para no commitear credenciales
   echo ".env" >> .gitignore
   ```

## 🔧 **ARCHIVOS MODIFICADOS**

### `app/Mailing/octopus.py`
- ❌ **ANTES**: API keys hardcodeadas
- ✅ **AHORA**: `os.environ.get('OCTOPUS_API_KEY')` y `os.environ.get('OCTOPUS_LIST_ID')`
- ✅ **VALIDACIÓN**: Error si las variables no están configuradas

### `app/login.py`  
- ❌ **ANTES**: Credenciales BD como fallback hardcodeadas
- ✅ **AHORA**: Solo `os.getenv('MYSQL_*')` sin fallbacks

### `app/run_app.py`
- ❌ **ANTES**: Todas las credenciales hardcodeadas con `setdefault()`
- ✅ **AHORA**: Carga `.env` y valida que todas las variables existan
- ✅ **VALIDACIÓN**: Error y exit si faltan variables requeridas

### `test_filtro_directo.py`
- ❌ **ANTES**: Credenciales hardcodeadas para testing
- ✅ **AHORA**: Carga `.env` y valida variables

## ⚠️ **IMPORTANTE**

1. **Nunca commitees el archivo .env** - debe estar en .gitignore
2. **Para Render (producción)**: Configura las variables directamente en el dashboard de Render
3. **Para desarrollo local**: Usa el archivo .env
4. **Todos los scripts ahora requieren el archivo .env** para funcionar

## 🧪 **TESTING**

Para probar que todo funciona:

1. **Crea el archivo .env** con las credenciales
2. **Ejecuta el servidor**:
   ```bash
   cd app
   python run_app.py
   ```
3. **Debería mostrar**:
   ```
   🚀 INICIANDO SERVIDOR FLASK DESDE /app
   ✅ Variables de entorno cargadas desde .env
   🗄️  BD: atusaludlicoreria.com/atusalud_kossomet
   📧 Email: jcamacho@kossodo.com
   ```

## 🆕 **NUEVA FUNCIONALIDAD: NOTIFICACIONES DE LEADS WIX**

### **¿Qué hace?**
- 📧 Envía email automático a la encargada cuando llega un nuevo lead desde WIX
- ⚡ Solo se ejecuta si `origen="WIX"` 
- 🔄 No afecta el flujo normal de otros orígenes
- 📋 Incluye toda la información del cliente (nombre, empresa, teléfono, email, requerimiento)

### **Configuración Requerida**
Agregar al archivo `.env`:
```env
LEAD_NOTIFICATION_EMAIL=encargada@kossodo.com
```

### **Flujo de Trabajo**
1. **Cliente llena formulario WIX** → POST `/wix/records`
2. **Sistema guarda en BD** → tabla WIX con `origen="WIX"`
3. **Sistema envía a EmailOctopus** → marketing list
4. **🆕 Sistema envía notificación** → email a encargada de leads
5. **Encargada asigna lead** → al asesor correspondiente

### **Archivos Agregados**
- `app/Mailing/lead_notification_template.py` - Template HTML profesional
- `app/Mailing/send_lead_notification.py` - Lógica de envío
- Modificado: `app/Mailing/wix.py` - Integración automática

## 🔗 **PRÓXIMOS PASOS**

Una vez configurado el `.env`:
- ✅ Sistema de feedback funcionará normalmente
- ✅ Emails de lamentamos seguirán enviándose
- ✅ Templates modificados estarán activos
- ✅ Redirect a `encuesta-gracias_final.html` funcionará
- ✅ **NUEVO**: Notificaciones automáticas de leads WIX

**¡Todo el sistema está listo para funcionar de forma segura sin credenciales hardcodeadas!** 