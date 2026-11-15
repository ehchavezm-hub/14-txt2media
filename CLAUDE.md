# txt2media — Instrucciones para Claude

## Al iniciar cualquier sesión

1. Hacer pull para obtener los últimos cambios:
   ```bash
   git -C /home/user/14-txt2media pull origin main 2>/dev/null || true
   ```
2. El proyecto está en `/home/user/14-txt2media` (en la nube) y en `D:\PST\txt2media` (Windows del usuario).
3. Instalar dependencias si es necesario: `pip install -e .`

## Al terminar cualquier sesión o tarea

Siempre hacer commit + push automático con todos los cambios:
```bash
cd /home/user/14-txt2media
git add -A
git diff --cached --quiet || git commit -m "auto: cambios de sesión $(date +%Y-%m-%d)"
git push origin main
```

## Proyecto

- **Nombre**: txt2media v1.0.1
- **Repositorio**: https://github.com/ehchavezm-hub/14-txt2media
- **Descripción**: Convierte EPUB/PDF/DOCX/MD → PPTX/DOCX/XLSX/Audio MP3/Video MP4
- **Python**: 3.12 o 3.13 (`py -3.13` en Windows)
- **Tests**: `pytest tests/ -v`

## Reglas importantes

- Secretos SIEMPRE en keyring, NUNCA en archivos JSON o logs
- Sin dependencias AGPL ni GPL
- Escritura atómica (tempfile + os.replace) en todos los generadores
- Voz predeterminada: `es-PE-CamilaNeural`
