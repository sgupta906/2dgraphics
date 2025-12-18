import random
from pathlib import Path

from PIL import Image

# k-means

AVERAGE_PIXEL_OUTPUT = Path("outputs/average_pixel")
KMEANS_OUTPUT = Path("outputs/kmeans")


def sloppy_distance(a, b):
    # just squared l2 
    dr = a[0] - b[0]
    dg = a[1] - b[1]
    db = a[2] - b[2]
    return dr * dr + dg * dg + db * db


def pick_starters(pixels, k):
    # trying to keep the seeds spread out
    picks = [random.choice(pixels)]
    while len(picks) < k:
        farthest = None
        farthest_score = -1
        for color in pixels:
            score = min(sloppy_distance(color, chosen) for chosen in picks)
            if score > farthest_score:
                farthest = color
                farthest_score = score
        if farthest is None:
            break
        picks.append(farthest)
    while len(picks) < k:
        picks.append(random.choice(pixels))
    return picks


def toss_pixels_into_buckets(pixels, centroids):
    # closest centroid wins.
    groups = []
    for color in pixels:
        best_idx = 0
        best_score = sloppy_distance(color, centroids[0])
        for idx in range(1, len(centroids)):
            score = sloppy_distance(color, centroids[idx])
            if score < best_score:
                best_idx = idx
                best_score = score
        # remembering which centroid we picked so recoloring is easy later.
        groups.append(best_idx)
    return groups


def nudge_centroids(pixels, groups, k):
    # average everything 
    totals = [[0, 0, 0] for _ in range(k)]
    counts = [0] * k
    for color, idx in zip(pixels, groups):
        # accumulate rgb totals per cluster so we can average them all at once.
        totals[idx][0] += color[0]
        totals[idx][1] += color[1]
        totals[idx][2] += color[2]
        counts[idx] += 1

    new_centroids = []
    for idx in range(k):
        if counts[idx] == 0:
            new_centroids.append(random.choice(pixels))
        else:
            new_centroids.append(
                (
                    totals[idx][0] // counts[idx],
                    totals[idx][1] // counts[idx],
                    totals[idx][2] // counts[idx],
                )
            )
    return new_centroids, counts


def draw_outline(groups, width, height):
    # if two neighbors disagree, drop a black pixel.
    outline = Image.new("L", (width, height), 255)
    pixels = outline.load()
    for y in range(height):
        for x in range(width):
            idx = y * width + x
            here = groups[idx]
            neighbors = []
            # poke in four directions; whenever any neighbor differs we color black.
            if x + 1 < width:
                neighbors.append(groups[idx + 1])
            if y + 1 < height:
                neighbors.append(groups[idx + width])
            if x - 1 >= 0:
                neighbors.append(groups[idx - 1])
            if y - 1 >= 0:
                neighbors.append(groups[idx - width])
            if any(n != here for n in neighbors):
                pixels[x, y] = 0
    return outline


def run_kmeans(pixels, k, max_iterations):
    # assign -> average -> repeat until nothing changes or i run out 
    centroids = pick_starters(pixels, k)
    groups = toss_pixels_into_buckets(pixels, centroids)
    for _ in range(max_iterations):
        centroids, _ = nudge_centroids(pixels, groups, k)
        new_groups = toss_pixels_into_buckets(pixels, centroids)
        if new_groups == groups:
            # if the assignments didn't change, we're basically converged, so stop looping.
            break
        groups = new_groups
    return centroids, groups


def load_pixels(image_path):
    # just give me width/height/data so i can crunch it elsewhere.
    with Image.open(image_path) as img:
        rgb = img.convert("RGB")
        width, height = rgb.size
        return width, height, list(rgb.getdata())


def find_regions_path(arg):
    # accepts "pikachu" or "pikachu_regions.png" because i kept forgetting which one i had
    path = Path(arg)
    if not path.suffix:
        path = path.with_suffix(".png")

    if path.name.endswith("_regions.png") and path.exists():
        return path

    base = path.stem
    if not base.endswith("_regions"):
        path = path.with_name(f"{base}_regions.png")

    if path.exists():
        return path

    alt = AVERAGE_PIXEL_OUTPUT / path.name
    if alt.exists():
        return alt

    raise FileNotFoundError(f"Could not find regions image at {path}")


def resolve_input_path(arg, use_original):
    # use_original=True skips all the averaging junk
    if use_original:
        path = Path(arg)
        if not path.exists():
            raise FileNotFoundError(f"Original image not found at {path}")
        return path
    return find_regions_path(arg)


def save_coloring(groups, centroids, width, height, image_path, k):
    # writes both files 
    KMEANS_OUTPUT.mkdir(parents=True, exist_ok=True)
    recolored = [centroids[idx] for idx in groups]
    out_img = Image.new("RGB", (width, height))
    out_img.putdata(recolored)

    stem = Path(image_path).stem
    if stem.endswith("_regions"):
        stem = stem[:-8]

    color_path = KMEANS_OUTPUT / f"{stem}_coloring_{k}.png"
    out_img.save(color_path)

    outline = draw_outline(groups, width, height)
    outline_path = color_path.with_name(color_path.stem + "_outline.png")
    outline.save(outline_path)

    return color_path, outline_path


def process_image(image_arg, k, max_iterations, use_original=False):
    # load pixels, toss them through run_kmeans, spit out files. that's it.
    input_path = resolve_input_path(image_arg, use_original)
    width, height, pixels = load_pixels(input_path)
    centroids, groups = run_kmeans(pixels, k, max_iterations)
    color_path, outline_path = save_coloring(groups, centroids, width, height, input_path, k)
    return color_path, outline_path
