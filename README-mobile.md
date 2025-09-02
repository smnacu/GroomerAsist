# GroomerAsist: App móvil (Kivy)

Versión móvil basada en Kivy con UI minimalista rojo/negro, responsive (modo compacto) y flujo offline-first.

## Requisitos

- Python 3.12.x en Windows para probar local.
- Para Android: Buildozer en Linux (p.ej. WSL2 + Ubuntu). En Windows puedes ejecutar, pero el APK se construye mejor en WSL.

## Ejecutar en PC (Windows)

1. En PowerShell, dentro de `mobile_app`:

```
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

También puedes usar el lanzador: `Scripts\run_groomerasist.bat`.

## Exportar datos

- Formatos: JSON (estructurado), TXT (legible), y CSV (tabular).
- Se guarda en el directorio de datos de la app y, si es posible, se copia a Descargas.
- CSV usa separador `;` y encabezados en español para compatibilidad con Excel/LibreOffice en ES/AR.

## Android

- Permisos incluidos: CAMERA, READ_MEDIA_IMAGES, VIBRATE, WRITE/READ_EXTERNAL_STORAGE.
- En Android se solicitan permisos en runtime y hay respuesta háptica al presionar.
- UI responsive: modo compacto automático en pantallas angostas y botón "Compacto" para alternar.
- Icono/Splash: coloca `icon.png` (512x512) y `splash.png` en `mobile_app/` y descomenta sus líneas en `buildozer.spec`.

### Construir APK (WSL/Ubuntu recomendado)

1. Instalar dependencias y buildozer:
   ```bash
   sudo apt update && sudo apt install -y python3-pip python3-venv git zip unzip openjdk-17-jdk
   python3 -m pip install --upgrade pip
   python3 -m pip install buildozer cython
   ```
2. Copiar el proyecto a WSL y compilar:
   ```bash
   cp -r /mnt/c/Users/<TU_USUARIO>/Documents/GitHub/GroomerAsist/mobile_app ~/GroomerAsist_mobile
   cd ~/GroomerAsist_mobile
   buildozer -v android debug
   ```
3. Instalar el APK desde `bin/` en el dispositivo.

## Notas

- Si la ventana aparece sin UI, actualiza drivers gráficos o revisa dependencias.
