from pathlib import Path


def test_core_modules_do_not_use_print_statements():
    root = Path(__file__).resolve().parents[1]
    targets = [
        root / "src" / "core" / "analyzer.py",
        root / "src" / "core" / "data_extractor.py",
        root / "src" / "core" / "report_generator.py",
    ]

    for path in targets:
        assert "print(" not in path.read_text(encoding="utf-8")
