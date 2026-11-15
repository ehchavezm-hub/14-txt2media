import sys, traceback
from pathlib import Path

pdf = list(Path(__file__).parent.glob("*.pdf"))
if not pdf:
    print("ERROR: No hay PDF en esta carpeta")
    sys.exit(1)

archivo = pdf[0]
print(f"Archivo: {archivo}")
salida = Path(__file__).parent / "test_output.mp4"

print("[1] Leyendo PDF...")
try:
    from txt2media.lectores.lector_pdf import LectorPDF
    doc = LectorPDF().leer(archivo)
    print(f"    Secciones: {len(doc.secciones)}")
except Exception as e:
    print(f"ERROR al leer PDF: {e}")
    traceback.print_exc()
    sys.exit(1)

print("[2] Generando video (puede tardar minutos)...")
try:
    from txt2media.generadores.generador_video import GeneradorVideo
    gen = GeneradorVideo()
    gen.generar(doc, salida)
    print(f"VIDEO OK: {salida} ({salida.stat().st_size/1024/1024:.1f} MB)")
except Exception as e:
    print(f"ERROR al generar video: {e}")
    traceback.print_exc()
    sys.exit(1)
