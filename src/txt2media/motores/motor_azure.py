"""Motor Azure TTS — es-PE-CamilaNeural / es-PE-AlexNeural."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from txt2media.core.base_voz import ClaveInvalidaError, CuotaAgotadaError, ErrorVoz, MotorVoz

VOZ_CAMILA = "es-PE-CamilaNeural"
VOZ_ALEX = "es-PE-AlexNeural"

_SERVICIO_KEYRING = "txt2media"
_USER_AGENT = "txt2media/1.0.1"
_REGION_DEFAULT = "eastus"


class MotorAzure(MotorVoz):
    @property
    def nombre(self) -> str:
        return "azure"

    def disponible_en_modo_local(self) -> bool:
        return False

    def disponible(self) -> bool:
        try:
            clave = self._obtener_clave()
            return bool(clave)
        except Exception:
            return False

    def sintetizar(self, texto: str, voz: str, salida: Path) -> None:
        import httpx

        from txt2media.core.modo_local import esta_activo, verificar_red_permitida

        endpoint = self._endpoint()
        if esta_activo():
            verificar_red_permitida(endpoint)

        clave = self._obtener_clave()
        if not clave:
            raise ClaveInvalidaError("Clave Azure no configurada")

        region = self._obtener_region()
        ssml = _construir_ssml(texto, voz)
        headers = {
            "Ocp-Apim-Subscription-Key": clave,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-24khz-96kbitrate-mono-mp3",
            "User-Agent": _USER_AGENT,
        }

        url = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"
        try:
            resp = httpx.post(url, headers=headers, content=ssml.encode("utf-8"), timeout=60)
        except httpx.RequestError as exc:
            raise ErrorVoz(f"Error de red Azure: {exc}") from exc

        if resp.status_code == 401:
            raise ClaveInvalidaError("Clave Azure inválida (401)")
        if resp.status_code == 429:
            raise CuotaAgotadaError("Cuota Azure agotada (429)")
        if resp.status_code != 200:
            raise ErrorVoz(f"Azure devolvió HTTP {resp.status_code}")

        salida.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(suffix=".mp3", dir=salida.parent)
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(resp.content)
            os.replace(tmp, salida)
        except Exception:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise

    def _obtener_clave(self) -> str:
        import keyring
        return keyring.get_password(_SERVICIO_KEYRING, "azure_key") or ""

    def _obtener_region(self) -> str:
        import keyring
        region = keyring.get_password(_SERVICIO_KEYRING, "azure_region")
        return region or os.environ.get("AZURE_TTS_REGION", _REGION_DEFAULT)

    def _endpoint(self) -> str:
        region = self._obtener_region()
        return f"{region}.tts.speech.microsoft.com"


def _construir_ssml(texto: str, voz: str) -> str:
    texto_escapado = (
        texto.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;")
    )
    return (
        f'<speak version="1.0" xml:lang="es-PE" '
        f'xmlns="http://www.w3.org/2001/10/synthesis">'
        f'<voice name="{voz}">{texto_escapado}</voice>'
        f"</speak>"
    )
