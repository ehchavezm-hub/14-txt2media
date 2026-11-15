"""Tests para MotorResumenLocal."""

from txt2media.core.resumen_local import MotorResumenLocal
from txt2media.core.modelo import Documento, Seccion, Bloque, TipoBloque


def _doc_con_texto() -> Documento:
    return Documento(
        titulo="Informe",
        secciones=[Seccion(nivel=1, titulo="Cap 1", bloques=[
            Bloque(tipo=TipoBloque.PARRAFO,
                   contenido="El proyecto avanza correctamente. Se cumplieron las metas."),
            Bloque(tipo=TipoBloque.PARRAFO,
                   contenido="Los indicadores muestran un avance del 78 por ciento."),
        ])]
    )


def test_motor_instancia() -> None:
    motor = MotorResumenLocal()
    assert motor is not None


def test_resumir_devuelve_texto() -> None:
    motor = MotorResumenLocal()
    doc = _doc_con_texto()
    resultado = motor.resumir(doc)
    assert isinstance(resultado, str)
    assert len(resultado) > 0


def test_resumir_es_mas_corto_que_original() -> None:
    motor = MotorResumenLocal()
    # Documento con muchos párrafos para que el resumen seleccione solo algunos
    secciones = [Seccion(nivel=1, titulo=f"Cap {i}", bloques=[
        Bloque(tipo=TipoBloque.PARRAFO,
               contenido=f"Oración número {i} del documento de prueba."),
    ]) for i in range(1, 15)]
    doc = Documento(titulo="Informe largo", secciones=secciones)
    texto_total = " ".join(
        b.contenido for s in doc.secciones for b in s.bloques
        if b.tipo == TipoBloque.PARRAFO
    )
    resultado = motor.resumir(doc)
    assert isinstance(resultado, str)
    assert len(resultado) > 0
    # Con 14 secciones, el resumen debe ser más corto que el texto completo
    assert len(resultado) < len(texto_total)
