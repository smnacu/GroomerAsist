from __future__ import annotations

from pathlib import Path

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.session import ServerSession


# Simple FastMCP server exposing a tool, a resource, and a prompt
mcp = FastMCP(
    name="GroomerAsist MCP",
    instructions=(
        "Herramientas y recursos básicos para el repositorio GroomerAsist. "
        "Incluye un saludo, lectura de README y un prompt de ejemplo."
    ),
)


@mcp.tool()
def greet(name: str = "Mundo") -> str:
    """Devuelve un saludo simple."""
    return f"Hola, {name}!"


@mcp.tool()
async def server_info(ctx: Context[ServerSession, None]) -> dict[str, str | bool]:
    """Información del servidor MCP actual (nombre, modo debug, etc.)."""
    return {
        "name": ctx.fastmcp.name,
        "debug": ctx.fastmcp.settings.debug,
        "log_level": ctx.fastmcp.settings.log_level,
    }


@mcp.resource("repo://readme")
def read_repo_readme() -> str:
    """Lee el README del proyecto si existe y devuelve su contenido."""
    candidates = [
        Path("README.md"),
        Path("README-mobile.md"),
    ]
    for p in candidates:
        if p.exists() and p.is_file():
            try:
                return p.read_text(encoding="utf-8", errors="ignore")
            except Exception as e:  # pragma: no cover - fallback simple
                return f"No se pudo leer {p}: {e}"
    return "README no encontrado en el repositorio."


@mcp.prompt(title="Cita de grooming")
def cita(nombre: str, fecha: str, estilo: str = "amable") -> str:
    """Genera un prompt para confirmar una cita de grooming."""
    estilos = {
        "amable": "Redacta un mensaje cálido y breve",
        "formal": "Redacta un mensaje formal y profesional",
        "casual": "Redacta un mensaje cercano y relajado",
    }
    instruccion = estilos.get(estilo, estilos["amable"])  # fallback
    return (
        f"{instruccion} para confirmar la cita de {nombre} el día {fecha}. "
        "Incluye hora si se conoce y un recordatorio de llegar 5 minutos antes."
    )


def main() -> None:  # pragma: no cover - entrypoint
    # stdio es el transporte por defecto; suficiente para clientes como Claude.
    mcp.run()


if __name__ == "__main__":  # pragma: no cover
    main()
