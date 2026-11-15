"""Tests de versión."""
import txt2media


def test_version_correcta():
    assert txt2media.__version__ == "1.0.1"


def test_autor():
    assert txt2media.__author__ == "COSAPI"
