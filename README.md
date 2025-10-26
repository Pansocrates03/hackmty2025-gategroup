# hackmty2025-gategroup

Repositorio del proyecto HackMTY 2025 — GateGroup.

Este repo contiene dos subproyectos principales: el frontend (dashboard) construido con SvelteKit y el backend construido con FastAPI.

Resumen de proyectos

1) SvelteKit (Frontend)

- Ubicación: `./sveltekit`
- Propósito: Panel administrativo para visualizar el estado de los trolleys, gestionar recursos y usar un agente de voz (Text-to-Speech) integrado con ElevenLabs.
- Dev server: normalmente en `http://localhost:5173` cuando se ejecuta con `npm run dev`.
- Variables importantes en desarrollo:
	- `ELEVENLABS_API_KEY` — clave privada de ElevenLabs (debe estar en el entorno del servidor, no en el cliente)
	- `ELEVENLABS_VOICE_ID` — id de la voz a usar
- Comandos rápidos:
	```powershell
	cd sveltekit
	npm install
	# exporta variables de entorno y arranca
	$env:ELEVENLABS_API_KEY = 'sk_xxx'
	$env:ELEVENLABS_VOICE_ID = 'voice_id'
	npm run dev
	```

Más detalles en: `./sveltekit/README.md`

2) FastAPI (Backend)

- Ubicación: `./fastapi`
- Propósito: API backend que proporciona datos, lógica y servicios (p. ej. integración con bases de datos o Supabase).
- Dev server: normalmente en `http://localhost:8000` y Swagger UI en `http://localhost:8000/docs` cuando se ejecuta con uvicorn.
- Variables importantes en desarrollo:
	- `SUPABASE_URL` — URL de Supabase
	- `SUPABASE_KEY` — clave de servicio de Supabase
- Comandos rápidos:
	```powershell
	cd fastapi
	python -m venv .venv
	.\.venv\Scripts\Activate.ps1
	pip install -r requirements.txt
	# exporta variables de entorno y arranca
	$env:SUPABASE_URL = 'https://your-project.supabase.co'
	$env:SUPABASE_KEY = 'your_key'
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
	```

Más detalles en: `./fastapi/README.md`

Acceso rápido

- Abrir frontend (si está corriendo): http://localhost:5173
- Abrir API docs (si backend corriendo): http://localhost:8000/docs

Notas importantes

- Nunca subas claves (ELEVENLABS_API_KEY, SUPABASE_KEY) al repositorio.
- En desarrollo puedes usar `.env` o exportar variables en la terminal; en producción configura las variables en el hosting/CI.

Si quieres que añadamos docker-compose, scripts de arranque o comprobaciones `fail-fast` para variables de entorno, dímelo y lo agrego.