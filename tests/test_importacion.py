"""Verifica que el paquete txt2media es importable y tiene la versión correcta."""


def test_paquete_importable() -> None:
    import txt2media  # noqa: F401


def test_version_correcta() -> None:
    import txt2media

    assert txt2media.__version__ == "1.0.1"


def test_subpaquetes_importables() -> None:
    import txt2media.core  # noqa: F401
    import txt2media.lectores  # noqa: F401
    import txt2media.generadores  # noqa: F401
    import txt2media.cli  # noqa: F401
