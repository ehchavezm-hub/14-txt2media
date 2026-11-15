# txt2media — Instrucciones para Claude

## INICIO DE SESIÓN — hacer esto primero, siempre, sin que el usuario lo pida

```bash
cd /home/user/14-txt2media 2>/dev/null || git clone --depth 1 https://github.com/ehchavezm-hub/14-txt2media /home/user/14-txt2media && cd /home/user/14-txt2media
git pull origin main 2>/dev/null || true
pip install -e . -q 2>/dev/null || true
```

## FIN DE SESIÓN — hacer esto siempre al terminar, sin que el usuario lo pida

```bash
cd /home/user/14-txt2media
git add -A
git diff --cached --quiet || git commit -m "auto: cambios de sesión $(date +%Y-%m-%d\ %H:%M)"
git push origin main
```

## Proyecto

- **Nombre**: txt2media v1.0.1
- **Repo**: https://github.com/ehchavezm-hub/14-txt2media
- **Windows**: `D:\PST\txt2media`
- **Python**: `py -3.13`
- **Tests**: `pytest tests/ -v`

## Reglas técnicas

- Secretos SIEMPRE en keyring, NUNCA en JSON/logs
- Sin dependencias AGPL ni GPL
- Escritura atómica (tempfile + os.replace) en todos los generadores
- Voz predeterminada: `es-PE-CamilaNeural`
- Versión actual: 1.0.1
