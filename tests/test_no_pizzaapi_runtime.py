from pathlib import Path


def test_runtime_package_does_not_import_pizzaapi():
    runtime_files = Path("src/nsigii_smtp").rglob("*.py")
    for path in runtime_files:
        content = path.read_text(encoding="utf-8")
        assert "import pizzapi" not in content
        assert "from pizzapi" not in content
