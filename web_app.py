import os
from pathlib import Path

from flask import Flask, render_template, request, send_from_directory
from PIL import Image
from werkzeug.utils import secure_filename

import average_pixel
import kmeans
import morphing
import sobel_gray_scale


app = Flask(__name__)

# this is so i don't have to chase paths
UPLOAD_DIR = Path("uploads")
OUTPUT_ROOT = Path("outputs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
SOURCE_LABELS = {
    "original": "Original upload",
    "regions": "Averaged regions image",
    "sobel": "Sobel grayscale image",
}


def relative_to_outputs(path: Path) -> str:
    return path.relative_to(OUTPUT_ROOT).as_posix()


def relative_to_uploads(path: Path) -> str:
    return path.relative_to(UPLOAD_DIR).as_posix()


def pick_source_image(upload_path: Path, source_choice: str, tolerance: int):
    # this figures out whether k-means should chew on the raw upload,
    # the averaged image, or the sobeled image..
    if source_choice == "regions":
        regions_path = average_pixel.process_image(upload_path, tolerance=tolerance)
        return regions_path, SOURCE_LABELS["regions"], False, False
    if source_choice == "sobel":
        sobel_path = sobel_gray_scale.process_image(upload_path)
        return sobel_path, SOURCE_LABELS["sobel"], False, True
    return upload_path, SOURCE_LABELS["original"], True, True


@app.route("/", methods=["GET", "POST"])
def index():
    message = None
    outputs = None
    # default to regions because it usually looks nicest
    source_choice = request.form.get("kmeans_source", "regions") if request.method == "POST" else "regions"
    morph_choice = request.form.get("outline_morph", "none") if request.method == "POST" else "none"

    if request.method == "POST":
        file = request.files.get("image")
        tolerance = request.form.get("tolerance", type=int, default=18)
        k_value = request.form.get("k", type=int, default=8)
        max_iters = request.form.get("max_iters", type=int, default=25)

        if not file or not file.filename:
            message = "Need an image before I can do anything."
        else:
            filename = secure_filename(file.filename)
            upload_path = UPLOAD_DIR / filename
            file.save(upload_path)

            try:
                source_path, source_label, source_from_uploads, use_original_flag = pick_source_image(
                    upload_path, source_choice, tolerance
                )
                print(f"kmeans is chewing on: {source_label} ({source_path})")

                coloring_path, outline_path = kmeans.process_image(
                    str(source_path), k_value, max_iters, use_original=use_original_flag
                )
                outline_label = "Black & White Outline"
                outline_path = Path(outline_path)
                if morph_choice in ("opening", "closing"):
                    with Image.open(outline_path) as outline_img:
                        grayscale_outline = outline_img.convert("L")
                        if morph_choice == "opening":
                            cleaned = morphing.opening(grayscale_outline)
                            outline_label = "Outline (Opening)"
                        else:
                            cleaned = morphing.closing(grayscale_outline)
                            outline_label = "Outline (Closing)"
                    morph_name = outline_path.stem + f"_{morph_choice}.png"
                    outline_path = outline_path.with_name(morph_name)
                    cleaned.save(outline_path)
                source_path = Path(source_path)
                if source_from_uploads:
                    source_rel_path = relative_to_uploads(source_path)
                else:
                    source_rel_path = relative_to_outputs(source_path)

                # stash everything in a dict so the template knows where to pull each image.
                outputs = {
                    "source": source_rel_path,
                    "source_from_uploads": source_from_uploads,
                    "coloring": relative_to_outputs(Path(coloring_path)),
                    "outline": relative_to_outputs(Path(outline_path)),
                    "source_label": source_label,
                    "outline_label": outline_label,
                }
                message = "Okay cool, scroll down and see if it looks decent."
            except FileNotFoundError as exc:
                
                message = str(exc)

    return render_template(
        "index.html",
        message=message,
        outputs=outputs,
        selected_source=source_choice,
        selected_morph=morph_choice if request.method == "POST" else "none",
    )


@app.route("/outputs/<path:filename>")
def serve_output(filename):
    return send_from_directory(OUTPUT_ROOT, filename)


@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    return send_from_directory(UPLOAD_DIR, filename)


def get_port():
    try:
        return int(os.environ.get("PORT", "5000"))
    except ValueError:
        return 5000


if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    app.run(host=host, port=get_port())
