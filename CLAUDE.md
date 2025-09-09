# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
```bash
# Production mode (requires .env file)
cd app && python run_app.py

# Development/Testing mode (uses mock credentials)
python run_server.py

# Production deployment (used by Render)
gunicorn app.main:app --timeout 120
```

### Dependencies
```bash
pip install -r requirements.txt
```

## Architecture Overview

This is a Flask-based customer feedback and survey system with modular endpoint architecture and email marketing integration.

### Core Application Structure

**Main Application (`app/main.py`)**
- Central Flask application with CORS configuration for multiple domains
- Handles customer feedback submission and rating flows (1-10 scale)
- Manages survey email sending and automatic follow-up emails for low ratings (≤3)
- Implements rating-based redirect logic and feedback-specific forms

**Modular Endpoint Architecture**
The system uses a modular approach with independent endpoints:

- **WIX Endpoint** (`/wix/records`): Receives form submissions from WIX websites, saves to database with `origen="WIX"`, and sends to EmailOctopus
- **Database Endpoint** (`/bd/records`): Independent database operations for the WIX table with configurable `origen` field for data source tracking
- **EmailOctopus Endpoint** (`/octopus/contacts`): Standalone EmailOctopus API integration for email marketing list management

### Database Integration

**Connection Management (`app/db.py`)**
- MySQL connector with environment-based configuration
- Handles both production (from .env) and development (mock) credentials

**Main Tables:**
- `envio_de_encuestas`: Customer feedback submissions with rating system
- `WIX`: Form submissions from various sources with origin tracking

### Email System

**Survey Distribution (`app/enviar_encuesta.py`)**
- Sends initial customer satisfaction surveys with unique tracking links
- Generates numbered consultation references (CONS-XXXXXX format)

**Automated Follow-up (`app/templates_email.py`)**
- Sends automatic "lamentamos" (apology) emails for ratings ≤3
- Differentiated templates for different service types (Ventas, Operaciones, Coordinación)

**EmailOctopus Integration (`app/Mailing/octopus.py`)**
- Synchronizes customer contacts to email marketing lists
- Maps form fields to EmailOctopus custom fields (COMPANY, RUC)

### Import System Architecture

The application uses a dual-import system to handle both production (Gunicorn) and development environments:

```python
try:
    # Production imports (from app package)
    from app.module import function
except ImportError:
    # Development imports (relative)
    from module import function
```

### Environment Configuration

**Required Environment Variables (Production):**
- `MYSQL_*`: Database connection parameters
- `EMAIL_*`: SMTP credentials for survey emails  
- `OCTOPUS_*`: EmailOctopus API integration

**Development Setup:**
- Create `.env` file with credentials (see `CONFIGURACION_ENV.md`)
- Use `run_app.py` for production-like environment
- Use `run_server.py` for development with mock credentials

### Blueprint Registration

All endpoints are organized as Flask blueprints with URL prefixes:
- `/wix/*`: WIX form handling
- `/octopus/*`: EmailOctopus operations  
- `/bd/*`: Direct database operations
- Authentication and admin routes (no prefix)

### CORS Configuration

Configured for specific domains:
- atusaludlicoreria.com
- kossodo.estilovisual.com  
- www.kossodo.com
- www.kossomet.com

### Rating System Flow

1. Customer receives survey email with unique tracking ID
2. Clicks rating (1-10 scale) → updates database with timestamp
3. Rating ≤3: Triggers automatic apology email + redirects to service-specific feedback form
4. Rating ≥4: Redirects to thank you page
5. Additional feedback collected through service-specific forms

### Deployment

**Production (Render):**
- Uses `app.main:app` entry point with Gunicorn
- Environment variables configured in Render dashboard
- 120-second timeout for long-running operations

**Local Development:**
- Supports both mock credentials (testing) and real credentials (.env)
- Hot reload available in development mode