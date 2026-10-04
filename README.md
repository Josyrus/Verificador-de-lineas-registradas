<<<<<<< HEAD
# Líneas registradas a mi CURP — consulta guiada

Herramienta multiplataforma (Windows/macOS/Linux) para recorrer el
directorio oficial de compañías telefónicas del **CRT**
(<https://portal.crt.gob.mx/plataformas-de-consulta-de-las-companias-telefonicas>)
y llevar el control de en cuáles tienes líneas registradas a tu CURP.

## Por qué no es 100% automática

Varios portales (Telcel, el backend compartido de Altán Redes que
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
=======
# Verificador de líneas registradas

Herramienta multiplataforma para consultar, de forma guiada, en qué compañías telefónicas existen líneas asociadas a una CURP. La aplicación abre los portales oficiales, permite resolver manualmente los CAPTCHA o verificaciones que correspondan y guarda el progreso localmente.

La automatización no intenta evadir CAPTCHA, sólo espera que el usuario las resuelva.

El objetivo no es implementar un MVC académico con muchas capas, sino mantener tres responsabilidades claras:

- **Model**: estado, reglas de negocio, persistencia y exportación.
- **View**: widgets Qt, renderizado y señales de intención del usuario.
- **Controller**: flujo de la aplicación, hilos, automatización y coordinación entre modelo y vista.

El CLI conserva acceso directo al mismo almacenamiento y al mismo `CheckerRunner`.

## Estructura

```text
.
├── main.py                         # Punto de entrada GUI/CLI
├── app_gui.py                      # Compatibilidad: arranque de GUI
├── app_cli.py                      # Interfaz de consola
├── application/
│   ├── model.py                    # Estado y reglas de negocio
│   └── services.py                 # Fachadas de servicios y cola de lote
├── controllers/
│   └── main_controller.py          # Controlador MVC de la GUI
├── views/
│   ├── main_window.py              # Ventana y renderizado Qt
│   └── widgets.py                  # Widgets auxiliares e iconos
├── checker/
│   ├── browser.py                  # Creación/configuración del WebDriver
│   ├── generic.py                  # Motor de acciones declarativas
│   ├── profiles.py                 # Detección de perfiles de navegador
│   ├── runner.py                   # Carga de configuraciones y ejecución
│   ├── worker.py                   # Worker Qt para ejecución en segundo plano
│   └── providers/
│       ├── configs/                # Configuración individual de compañías
│       └── templates/              # Flujos reutilizables
├── carriers.py                     # Directorio de compañías y alias
├── storage.py                      # Persistencia JSON
├── clipboard.py                    # Portapapeles multiplataforma
└── media/                          # Iconos, estilos y sonido
```

## Principios aplicados

### Legibilidad y nomenclatura

Se usa `snake_case` para funciones, variables y parámetros, con identificadores en inglés (`company_name`, `profile`, `destination`, `detect_profiles`). Los nombres de clases usan `PascalCase` y las constantes `UPPER_SNAKE_CASE`. Los textos de la interfaz y las claves del archivo JSON permanecen en español porque forman parte de la interfaz y las claves porque me di cuenta muy tarde lo MAL planificado que estaba mi proyecto, es un error que no volvere a repetir y tambien una razón más para volver a repasar mis apuntes de ing. de software.

La lógica que antes estaba concentrada en `app_gui.py` se separó por responsabilidad. La ventana ya no decide cómo guardar datos ni cómo ejecutar Selenium.

### KISS 

No se añadieron repositorios, patrones Factory/Strategy, contenedores de dependencias ni una jerarquía de clases de dominio innecesaria. El controlador coordina y el modelo administra el estado.

### YAGNI

Se conserva únicamente la funcionalidad que el proyecto ya necesita: consulta manual/automatizada, perfiles, progreso, filtros, historial, lotes y exportación CSV.

### DRY

La GUI y el resto de la aplicación usan `AppModel` para modificar el estado. La carga de configuraciones de automatización está centralizada en `checker.runner`. Los elementos visuales repetidos están en `views.widgets`.

## Instalación

Para GUI y automatización:

```bash
python -m pip install -r requirements.txt
```

Para utilizar solamente el CLI básico no se necesita PySide6, aunque las funciones de automatización requieren Selenium y un navegador compatible.
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)

## Uso

```bash
<<<<<<< HEAD
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
=======
python main.py
python main.py --gui
python main.py --cli
python main.py --cli --resumen
python main.py --cli --exportar reporte.csv
python main.py --cli --reiniciar
```

El progreso se guarda en:

- Windows: `%APPDATA%/lineas-curp/progreso.json`
- Linux/macOS: `$XDG_CONFIG_HOME/lineas-curp/progreso.json` o `~/.config/lineas-curp/progreso.json`

## Configuraciones de proveedores

Cada proveedor automatizable tiene un JSON en `checker/providers/configs/`. Los flujos comunes pueden extraerse a `checker/providers/templates/` mediante la propiedad `template`.

Ejemplo:

```json
{
    "nombre": "Ejemplo",
    "url": "https://ejemplo.mx/consulta",
    "template": "vinculacion"
}
```

El motor combina primero el template y después la configuración específica, permitiendo sobrescribir pasos o resultados cuando un proveedor se comporta de forma diferente.

## Validación

Antes de distribuir cambios, se puede ejecutar:

```bash
python -m compileall .
python -m unittest discover -s tests -v
```
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)
