# GroomerAsist MCP Server

Servidor MCP mínimo con FastMCP (Python) para integrarse con Claude en VS Code.

Funciones incluidas:

- Herramientas: `greet(name="Mundo")`, `server_info()`.
- Recurso: `repo://readme` para leer `README.md` o `README-mobile.md`.
- Prompt: `Cita de grooming` (`cita(nombre, fecha, estilo?)`).

## Requisitos

- Python del entorno de este repo: `Scripts/python.exe`.
- Paquete `mcp` instalado en el entorno.

## Instalación (Windows PowerShell)

```
.\Scripts\python.exe -m pip install --upgrade "mcp[cli]"
```

## Ejecutar manualmente (opcional)

```
.\Scripts\python.exe -m mcp_server
```

El servidor usa transporte stdio por defecto.

## Uso con Claude for VS Code

Ya está configurado en `.vscode/settings.json` como `groomer-asist-mcp`.

1. Instala la extensión "Claude" en VS Code.
2. Abre la vista de Claude y comienza un chat.
3. Pide listar herramientas MCP o invoca:
   - `greet` con `name="Mundo"`.
   - `server_info`.
   - Lee el recurso `repo://readme`.
   - Usa el prompt "Cita de grooming" con tus datos.

## Problemas comunes

- "No module named mcp": instala `mcp` en este entorno.
- Si cambias de intérprete, actualiza `command` en `.vscode/settings.json`.
- Para logs, puedes añadir `MCP_DEBUG=1` en `env` del settings.

## Desarrollo

Entrada principal: `mcp_server/__main__.py`.
