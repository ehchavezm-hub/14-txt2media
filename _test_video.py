import sys, traceback, time
from pathlib import Path

HERE = Path(__file__).parent
pdf = list(HERE.glob("*.pdf"))
if not pdf:
    print("ERROR: No hay PDF en esta carpeta")
    sys.exit(1)

archivo = pdf[0]
salida = HERE / "test_output.mp4"
print(f"Archivo: {archivo}")
print()

# --- Paso 1: leer PDF ---
print("[1/3] Leyendo PDF...", flush=True)
t0 = time.time()
try:
    from txt2media.lectores.lector_pdf import LectorPDF
    doc = LectorPDF().leer(archivo)
    print(f"      OK — {len(doc.secciones)} secciones, {sum(len(s.texto) for s in doc.secciones)} chars  ({time.time()-t0:.1f}s)", flush=True)
except Exception as e:
    print(f"      ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)

# --- Paso 2: renderizar diapositivas ---
print(f"[2/3] Renderizando {len(doc.secciones)+1} diapositivas PNG...", flush=True)
t0 = time.time()
import tempfile
from txt2media.core.renderizador import RenderizadorDiapositiva
tmp = Path(tempfile.mkdtemp())
renderer = RenderizadorDiapositiva()
imagenes = []
portada = renderer.render_portada(doc.titulo)
portada.save(str(tmp / "slide_000.png"))
imagenes.append(tmp / "slide_000.png")
for i, sec in enumerate(doc.secciones, 1):
    img = renderer.render_seccion(sec)
    p = tmp / f"slide_{i:03d}.png"
    img.save(str(p))
    imagenes.append(p)
    print(f"      slide {i}/{len(doc.secciones)}  ({time.time()-t0:.1f}s)", flush=True)
print(f"      OK — {len(imagenes)} imagenes  ({time.time()-t0:.1f}s)", flush=True)

# --- Paso 3: sintetizar audio ---
print("[3a/3] Sintetizando audio TTS...", flush=True)
t0 = time.time()
audio_path = tmp / "naracion.mp3"
try:
    from txt2media.generadores.generador_audio import GeneradorAudio
    GeneradorAudio().generar(doc, audio_path)
    print(f"       OK — {audio_path.stat().st_size/1024:.0f} KB  ({time.time()-t0:.1f}s)", flush=True)
except Exception as e:
    print(f"       ADVERTENCIA audio: {e} — continuando sin audio", flush=True)
    audio_path = None

# --- Paso 4: combinar con ffmpeg ---
print("[3b/3] Combinando con ffmpeg...", flush=True)
t0 = time.time()
import shutil, subprocess
ffmpeg = shutil.which("ffmpeg")
if not ffmpeg:
    print("ERROR: ffmpeg no encontrado en PATH")
    sys.exit(1)

lista_txt = tmp / "frames.txt"
with lista_txt.open("w", encoding="utf-8") as f:
    for img in imagenes:
        f.write(f"file '{img}'\nduration 5\n")
    f.write(f"file '{imagenes[-1]}'\n")

cmd = [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(lista_txt)]
if audio_path and audio_path.exists():
    cmd += ["-i", str(audio_path), "-shortest"]
cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "24", "-crf", "23"]
if audio_path and audio_path.exists():
    cmd += ["-c:a", "aac", "-b:a", "128k"]
cmd.append(str(salida))

result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
if result.returncode != 0:
    print(f"ERROR ffmpeg:\n{result.stderr[-1000:]}")
    sys.exit(1)

print(f"      OK  ({time.time()-t0:.1f}s)", flush=True)
print()
print(f"=== VIDEO GENERADO: {salida}")
print(f"    Tamanio: {salida.stat().st_size/1024/1024:.1f} MB")
