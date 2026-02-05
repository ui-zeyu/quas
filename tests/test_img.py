from pathlib import Path

import numpy as np
from PIL import Image


def test_extract_pixels_defaults(tmp_path: Path) -> None:
    img = Image.new("RGBA", (10, 10), color=(255, 0, 0, 255))
    arr = np.array(img)
    pixels = arr[0::1, 0::1]
    result = Image.fromarray(pixels, "RGBA")

    output_path = tmp_path / "output.png"
    result.save(output_path)

    assert output_path.exists()
    result_img = Image.open(output_path)
    assert result_img.size == (10, 10)
    assert result_img.mode == "RGBA"


def test_extract_pixels_with_step(tmp_path: Path) -> None:
    img = Image.new("RGBA", (10, 10), color=(255, 0, 0, 255))
    arr = np.array(img)
    pixels = arr[0::2, 0::2]
    result = Image.fromarray(pixels, "RGBA")

    output_path = tmp_path / "output.png"
    result.save(output_path)

    assert output_path.exists()
    result_img = Image.open(output_path)
    assert result_img.size == (5, 5)


def test_extract_pixels_with_offset(tmp_path: Path) -> None:
    img = Image.new("RGBA", (10, 10), color=(255, 0, 0, 255))
    arr = np.array(img)
    pixels = arr[3::1, 2::1]
    result = Image.fromarray(pixels, "RGBA")

    output_path = tmp_path / "output.png"
    result.save(output_path)

    assert output_path.exists()
    result_img = Image.open(output_path)
    assert result_img.size == (8, 7)


def test_extract_pixels_combined(tmp_path: Path) -> None:
    img = Image.new("RGBA", (10, 10), color=(255, 0, 0, 255))
    arr = np.array(img)
    pixels = arr[1::2, 1::3]
    result = Image.fromarray(pixels, "RGBA")

    output_path = tmp_path / "output.png"
    result.save(output_path)

    assert output_path.exists()
    result_img = Image.open(output_path)
    assert result_img.size == (3, 5)


def test_extract_pixels_color(tmp_path: Path) -> None:
    img = Image.new("RGBA", (10, 10), color=(255, 0, 0, 255))
    img.putpixel((0, 0), (100, 200, 50, 255))
    arr = np.array(img)
    pixels = arr[0::1, 0::1]
    result = Image.fromarray(pixels, "RGBA")

    output_path = tmp_path / "output.png"
    result.save(output_path)

    result_img = Image.open(output_path)
    assert result_img.getpixel((0, 0)) == (100, 200, 50, 255)


def test_inspect_pixels_defaults() -> None:
    img = Image.new("RGBA", (10, 10), color=(255, 0, 0, 255))
    arr = np.array(img)
    pixels = arr[0::1, 0::1]
    pixels = pixels.reshape(-1, 4)

    assert len(pixels) == 100
    assert np.array_equal(pixels[:10], [[255, 0, 0, 255]] * 10)


def test_inspect_pixels_with_offset() -> None:
    img = Image.new("RGBA", (10, 10), color=(255, 0, 0, 255))
    img.putpixel((5, 5), (128, 128, 128, 255))
    arr = np.array(img)
    pixels = arr[5::1, 5::1]
    pixels = pixels.reshape(-1, 4)

    assert pixels[0][0] == 128


def test_inspect_pixels_all() -> None:
    img = Image.new("RGBA", (3, 3), color=(255, 0, 0, 255))
    arr = np.array(img)
    pixels = arr[0::1, 0::1]
    pixels = pixels.reshape(-1, 4)

    assert len(pixels) == 9


def test_image_rgba_conversion(tmp_path: Path) -> None:
    rgb_img = Image.new("RGB", (5, 5), color=(255, 0, 0))
    input_path = tmp_path / "rgb.png"
    rgb_img.save(input_path)

    img = Image.open(input_path).convert("RGBA")
    arr = np.array(img)
    pixels = arr[0::1, 0::1]
    result = Image.fromarray(pixels, "RGBA")

    output_path = tmp_path / "rgba.png"
    result.save(output_path)

    result_img = Image.open(output_path)
    assert result_img.mode == "RGBA"
