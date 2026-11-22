# Herramientas

Scripts secundarios. Para usar la app a diario basta con `txt2media.cmd` en la raíz.
Todos estos scripts se ejecutan sobre la raíz del repositorio, sin importar desde dónde se abran.

## portable/
| Archivo | Para qué |
|---|---|
| `ejecutar.bat` | Abre la app desde el ZIP portable (`txt2media_python.zip`). Instala dependencias la primera vez. |
| `lanzar.pyw` | Abre la ventana sin consola; lo usa `ejecutar.bat`. |

## compilar/
| Archivo | Para qué |
|---|---|
| `build_exe.bat` | Genera `dist\txt2media.exe` (un solo archivo) en tu PC. |
| `construir_portable.bat` | Genera la carpeta portable `dist\txt2media\` con PyInstaller. |
| `main_exe.py` | Punto de entrada del `.exe` (también lo usa GitHub Actions). |
| `txt2media.spec`, `txt2media_gui.spec`, `txt2media_onefile.spec` | Configuraciones de PyInstaller. |
| `bootstrap_installer.py` | Instalador que extrae la app y ejecuta `instalar_universal.bat`. |

## instalacion/
| Archivo | Para qué |
|---|---|
| `instalar.bat` | Configuración inicial: dependencias y tarea de auto-guardado en GitHub cada 5 minutos. |
| `instalar_universal.bat` | Instalación para equipos especiales (S Mode, 32 bits, ARM) y acceso directo. |
| `crear_acceso.py` | Crea el acceso directo en el Escritorio. |

## ventana/
Lanzadores antiguos de la ventana. Se conservan por compatibilidad; `txt2media.cmd` los reemplaza.
| Archivo | Para qué |
|---|---|
| `abrir_gui.bat` + `_lanzar_gui.py` | Abre la ventana sin consola. |
| `txt2media_gui.bat`, `txt2media_gui.vbs` | Abren la ventana sin consola. |
| `diagnostico_gui.bat` | Revisa Python, PySide6 y txt2media y muestra los errores sin cerrarse. |

## mantenimiento/
| Archivo | Para qué |
|---|---|
| `guardar.bat` | Sube a GitHub todos los cambios de la carpeta (commit + push a `main`). |
| `auto_guardar.ps1` | Lo mismo, ejecutado por la tarea programada que crea `instalar.bat`. |
| `verificar.bat` | Verifica la instalación y corre pruebas básicas. |
| `test_video.bat` + `_test_video.py` | Prueba la generación de video con un PDF de la raíz. |

> **Cuidado con `guardar.bat` y `auto_guardar.ps1`:** suben *todo* lo que haya en la carpeta del
> repositorio. No dejes documentos ni resultados de conversión dentro de ella.
