import json
from pathlib import Path

from afg_province_maps.boundaries import default_boundary_path
from afg_province_maps.cli import main

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = str(ROOT / "examples" / "population_2027_ocha.csv")
REPO_BOUNDARIES = ROOT / "data" / "boundaries" / "geoBoundaries-AFG-ADM1_simplified.geojson"


def test_check_passes_on_example(capsys):
    assert main(["check", "--data", EXAMPLE, "--column", "population_2027"]) == 0
    assert "Check passed." in capsys.readouterr().out


def test_bad_column_returns_error_code(capsys):
    assert main(["check", "--data", EXAMPLE, "--column", "nope"]) == 2
    assert "not found" in capsys.readouterr().err


def test_default_boundaries_are_bundled_and_match_repository_copy():
    bundled = default_boundary_path()
    assert bundled.is_file()
    assert bundled.read_bytes() == REPO_BOUNDARIES.read_bytes()
    assert (bundled.parent / "NOTICE.md").is_file()


def test_map_uses_bundled_boundaries_and_creates_png_pdf_and_json(tmp_path):
    code = main([
        "map",
        "--data", EXAMPLE,
        "--column", "population_2027",
        "--out", str(tmp_path),
    ])

    assert code == 0
    assert (tmp_path / "population_2027.png").is_file()
    assert (tmp_path / "population_2027.pdf").is_file()

    transparent_png = tmp_path / "population_2027_transparent.png"
    assert transparent_png.is_file()

    from PIL import Image

    with Image.open(transparent_png) as image:
        assert image.mode == "RGBA"
        assert image.getchannel("A").getextrema()[0] == 0

    metadata_path = tmp_path / "population_2027.json"
    assert metadata_path.is_file()
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["boundaries_sha256"]
    assert not (tmp_path / "population_2027.html").exists()


def test_html_format_is_rejected(tmp_path, capsys):
    code = main([
        "map",
        "--data", EXAMPLE,
        "--column", "population_2027",
        "--formats", "html",
        "--out", str(tmp_path),
    ])
    assert code == 2
    assert "Choose from png, pdf" in capsys.readouterr().err


def test_check_rejects_names_that_match_no_boundary(tmp_path, capsys):
    path = tmp_path / "d.csv"
    path.write_text("province,x\nKabul,1\nNowhere,2\n", encoding="utf-8")
    assert main(["check", "--data", str(path), "--column", "x"]) == 2
    assert "Nowhere" in capsys.readouterr().err


def test_non_numeric_bins_return_error_code(tmp_path, capsys):
    code = main([
        "map",
        "--data", EXAMPLE,
        "--column", "population_2027",
        "--bins", "0,abc,1000",
        "--out", str(tmp_path),
    ])
    assert code == 2
    assert "--bins must be comma-separated numbers" in capsys.readouterr().err
