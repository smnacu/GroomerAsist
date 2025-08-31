# GroomerAsist: App móvil (Kivy)

Este directorio contiene una versión móvil basada en Kivy para Android/iOS.

## Requisitos

- Python 3.12.4 en tu PC (tu global)
- Para Android: Buildozer (en Linux, p.ej. WSL2 con Ubuntu)
  - En Windows puedes probar la app, pero para empaquetar APK usa WSL/Ubuntu.

## Ejecutar en PC (Windows)

1. Abre PowerShell en `mobile_app` y ejecuta:

```
python -m pip install --upgrade pip
# Si falla en Python 3.12.4 en Windows al instalar Kivy, es normal. Kivy se soporta mejor empaquetado con Buildozer.
# Puedes omitir esta sección y construir directamente el APK en WSL.
python -m pip install -r requirements.txt
python main.py
```

Si tienes varias versiones de Python, usa la ruta de tu ejecutable (p.ej. `C:/Python313/python.exe`).

## Empaquetar para Android (opción A: WSL/Ubuntu + Buildozer)

Buildozer funciona en Linux. Desde Windows, usa WSL2 con Ubuntu:

1. Instala WSL2 y Ubuntu desde Microsoft Store.
2. En Ubuntu, instala dependencias y buildozer:
   ```bash
   sudo apt update && sudo apt install -y python3-pip python3-venv git zip unzip openjdk-17-jdk
   python3 -m pip install --upgrade pip
   python3 -m pip install buildozer cython
   ```
3. Copia el proyecto a WSL (o clónalo):
   ```bash
   cp -r /mnt/c/Users/<TU_USUARIO>/Documents/GitHub/GroomerAsist/mobile_app ~/GroomerAsist_mobile
   cd ~/GroomerAsist_mobile
   buildozer init
   ```
4. Edita `buildozer.spec` (ya hay uno de ejemplo en `mobile_app/`):
   - `requirements = python3,kivy==2.3.0`
   - `package.domain = org.tu.organizacion`
   - `package.name = GroomerAsist`
   - `orientation = portrait`
   - Opcional: `android.minapi = 24`
5. Compila y genera APK:
   ```bash
   buildozer -v android debug
   ```
6. El APK queda en `bin/`. Instálalo en tu Android o usa `buildozer android deploy run` si tienes el móvil conectado por USB con depuración.

## Empaquetar para Android (opción B: BeeWare / Briefcase)

BeeWare permite empaquetar con interfaz nativa. Este proyecto está hecho con Kivy, por lo que la ruta natural es Buildozer. Si prefieres BeeWare, habría que crear una versión con Toga (framework de BeeWare) en lugar de Kivy.

## Notas

- Kivy en Windows requiere SDL2. La instalación via pip lo gestiona automáticamente.
- Si aparece una ventana negra sin UI, actualiza drivers de video y asegúrate de tener las dependencias correctas.

## Próximos pasos

- Persistencia (JSON/SQLite) y listado de registros.
- Iconos, splash y permisos Android.
- Formularios con Dropdowns (Spinner) para evitar texto libre.
