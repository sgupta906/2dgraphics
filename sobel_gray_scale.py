# quick grayscale 

from pathlib import Path

from PIL import Image

OUTPUT_DIR = Path("outputs/sobel_gray_scale")


def to_grayscale(image_path: Path) -> Image.Image:
    # average rgb 
    with Image.open(image_path) as img:
        rgb = img.convert("RGB")
        width, height = rgb.size
        gray = Image.new("L", (width, height))
        gray_pixels = gray.load()
        rgb_pixels = rgb.load()

        for y in range(height):
            for x in range(width):
                # average: add the rgb values and divide by three.
                r, g, b = rgb_pixels[x, y][:3]
                gray_pixels[x, y] = (r + g + b) // 3

    return gray


def process_image(image_path: str | Path, output_dir: Path = OUTPUT_DIR) -> Path:
    # convert, save, print where it landed. done.
    image_path = Path(image_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    gray = to_grayscale(image_path)
    out_name = Path(image_path).stem + "_sobel_gray.png"
    out_path = output_dir / out_name
    # write the flattened picture so the Sobel script has something to chew on.
    gray.save(out_path)
    print(f"Saved {out_path}")
    return out_path
