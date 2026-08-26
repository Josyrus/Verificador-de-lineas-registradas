# Líneas registradas a mi CURP — consulta guiada

Herramienta multiplataforma (Windows/macOS/Linux) para recorrer el
directorio oficial de compañías telefónicas del **CRT**
(<https://portal.crt.gob.mx/plataformas-de-consulta-de-las-companias-telefonicas>)
y llevar el control de en cuáles tienes líneas registradas a tu CURP.

## Por qué no es 100% automática

Revisé varios portales (Telcel, el backend compartido de Altán Redes que
usan ~70 compañías, etc.): todos están protegidos con CAPTCHA / detección
de bots y flujos de verificación en JavaScript. Eso es intencional — son
formularios que exponen datos ligados a tu identidad (CURP), así que están
diseñados para no poder consultarse en automático ni en masa. Esta
herramienta **no intenta evadir esas protecciones**; en su lugar:

- Trae precargado el directorio completo (152 compañías) con su URL de consulta.
- Copia tu CURP al portapapeles y abre cada portal en tu navegador, uno por uno.
- Tú resuelves el CAPTCHA/formulario normalmente (unos segundos por compañía).
- Guarda el resultado que le indiques (encontrada / sin línea / error) y tus notas.
- Recuerda tu progreso entre sesiones (puedes cerrarlo y seguir después).
- Exporta un reporte final en CSV.

## Instalación

```bash
pip install PySide6          # solo si vas a usar la interfaz gráfica
```

El modo consola no necesita ninguna dependencia extra (usa la librería
estándar de Python 3).

## Uso

```bash
python main.py            # detecta automáticamente: GUI si hay entorno gráfico, si no, consola
python main.py --gui      # fuerza la interfaz gráfica
python main.py --cli      # fuerza la consola

python main.py --cli --resumen              # solo muestra tu progreso
python main.py --cli --exportar reporte.csv # exporta a CSV sin abrir nada
python main.py --cli --reiniciar            # vuelve a recorrer todas las compañías
```

El progreso se guarda en:
- Windows: `%APPDATA%\lineas-curp\progreso.json`
- macOS/Linux: `~/.config/lineas-curp/progreso.json`

## Estructura

- `carriers.py` — directorio de compañías y URLs (tomado del portal del CRT).
- `storage.py` — carga/guarda tu progreso en JSON.
- `clipboard.py` — copiar la CURP al portapapeles desde consola (pbcopy/clip/xclip/wl-copy).
- `app_gui.py` — interfaz gráfica (PySide6/Qt).
- `app_cli.py` — modo consola.
- `main.py` — punto de entrada, elige GUI o consola.

## Actualizar el directorio de compañías

La lista de compañías puede cambiar. Si el CRT agrega o quita alguna,
edita la lista `CARRIERS` en `carriers.py` (tupla `("Nombre", "URL")`).
