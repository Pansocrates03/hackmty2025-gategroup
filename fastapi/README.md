# FastAPI Service

Proyecto: API backend con FastAPI (servicios REST y lógica de negocio).

Descripción

Este servicio contiene los endpoints del backend. Suele usarse para exponer APIs consumidas por el frontend (SvelteKit) o por otras partes del sistema.

Requisitos
- Python 3.10+ (recomendado)
- pip
- Virtual environment (recomendado)

Instalación y entorno

1. Crear y activar entorno virtual (Windows PowerShell):

```powershell
cd fastapi
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Variables de entorno importantes (ejemplos):
- `SUPABASE_URL` — URL de la instancia Supabase
- `SUPABASE_KEY` — clave secreta de Supabase
- Otras claves según el proyecto

Puedes exportarlas temporalmente en PowerShell:

```powershell
$env:SUPABASE_URL = 'https://your-project.supabase.co'
$env:SUPABASE_KEY = 'your_service_role_key'
```

(Alternativamente usa un `.env` y carga con `python-dotenv` o configura el entorno en el servicio donde despliegues.)

Ejecutar localmente

Usa `uvicorn` para ejecutar el servidor en modo de desarrollo con autoreload:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Ajusta el path `app.main:app` según la estructura real del proyecto (archivo y variable `app`).

Endpoints y pruebas

- Swagger UI: `http://localhost:8000/docs`
- Revisa el archivo donde se definen las rutas (`app`/`main.py` o similar).

Depuración de variables de entorno

Si una variable como `SUPABASE_URL` no aparece en el proceso, revisa:
- Que el `.env` esté en el directorio correcto
- Que estés cargando el `.env` con `python-dotenv` (si no usas export explícito)
- Que al ejecutar `uvicorn` el proceso tenga acceso al entorno con `process`/`os.environ`

Ejemplo de carga con `python-dotenv` (opcional)

```python
from dotenv import load_dotenv
from pathlib import Path
import os

root = Path(__file__).resolve().parent.parent
load_dotenv(root / '.env')
# ahora os.getenv('SUPABASE_URL') funcionará
```

Despliegue

- En producción, define las variables de entorno en la configuración del host (Azure, AWS, Docker, systemd, etc.).
- No incluyas claves en el repositorio.

Pruebas

- Añade tests en `tests/` y ejecuta con `pytest`.

Soporte

Si quieres, puedo:
- Añadir un ejemplo de `docker-compose` para levantar la app con variables de entorno.
- Añadir verificación automática de variables faltantes al arrancar (fail-fast).
- Integrarlo con Supabase o con autenticación si lo necesitas.
