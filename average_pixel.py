from collections import deque
from pathlib import Path

from PIL import Image


OUTPUT_DIR = Path("outputs/average_pixel")


def color_gap(a, b):
    # L1 math
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])


def quick_avg(total_r, total_g, total_b, count):
    # this is so i can keep track of the running rgb average.
    if count == 0:
        return None
    return (
        total_r // count,
        total_g // count,
        total_b // count,
    )


def smoosh_region(pixels, visited, start_x, start_y, width, height, tolerance):
    # this is a doodled flood fill. once a region stays within the tolerance, every pixel inside gets flattened to the same color.
    queue = deque([(start_x, start_y)])  # start from the seed pixel.
    
    coords = []  # track all pixels that end up in this blob.
    total_r = total_g = total_b = 0  

    while queue:
        x, y = queue.pop()  # grab the next pixel we want to inspect.
        
        if visited[y][x]:
            continue

        current = pixels[x, y]  # whatever color is sitting at this coordinate.
        avg_color = quick_avg(total_r, total_g, total_b, len(coords)) or current  # default to current if blob is empty.

        # if this pixel feels too different from whatever color we already averaged.
        if color_gap(current, avg_color) > tolerance:
            continue

        # mark the pixel as used so we don't double-count it later.
        visited[y][x] = True
        coords.append((x, y))
        total_r += current[0]
        total_g += current[1]
        total_b += current[2]

        # peek in every 4-connected direction and queue unvisited neighbors for later.
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < width and 0 <= ny < height and not visited[ny][nx]:
                queue.append((nx, ny))

    avg_color = quick_avg(total_r, total_g, total_b, len(coords)) or pixels[start_x, start_y]

    return coords, avg_color


def process_image(image_path, tolerance=18, output_dir=OUTPUT_DIR):
    # flatten the photo into chunky blobs. the number 18 lives here forever because
    # i scribbled it in a margin and it kept the mario screenshot from turning to mush.
    # every pixel gets visited exactly once so the output image ends up as big colored islands.
    output_dir.mkdir(parents=True, exist_ok=True)
    with Image.open(image_path) as img:
        rgb_img = img.convert("RGB")
        width, height = rgb_img.size

        pixels = rgb_img.load()
        out_img = Image.new("RGB", (width, height))
        out_pixels = out_img.load()
        visited = [[False] * width for _ in range(height)]

        for y in range(height):
            for x in range(width):
                if visited[y][x]:
                    continue  # already handled in a previous blob, skip it.
                # for each untouched pixel, build a blob and paint every coordinate with one color.
                blob_coords, blob_color = smoosh_region(pixels, visited, x, y, width, height, tolerance)
                for rx, ry in blob_coords:
                    out_pixels[rx, ry] = blob_color  # assign the averaged color from that blob.

        out_name = Path(image_path).stem + "_regions.png"
        out_path = output_dir / out_name
        # at this point the whole image is filled with flat regions, so save it off for k-means.
        out_img.save(out_path)
        print(f"{image_path} -> {out_path} (looks kinda cartoonish now)")
        return out_path
