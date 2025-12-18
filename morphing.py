from PIL import Image
        
def erode_image(image: Image.Image) -> Image.Image:
    # Erode a binary (black & white) image by one pixel using a 3x3 square kernel.
    width, height = image.size
    input_pixels = image.load()
    output_image = Image.new("L", (width, height), 255)
    output_pixels = output_image.load()

    for y in range(height):
        for x in range(width):
            pixel = input_pixels[x, y]

            # if it's white, keep it white and go next
            if pixel == 255:
                output_pixels[x, y] = 255
                continue  

            # pixel is black → check its 3x3 neighborhood
            all_black = True
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    nx = x + dx
                    ny = y + dy

                    # skip out-of-bounds neighbors
                    if nx < 0 or nx >= width or ny < 0 or ny >= height:
                        continue

                    # if any neighbor is white, erosion should remove this pixel
                    if input_pixels[nx, ny] == 255:
                        all_black = False
                        break
                if not all_black:
                    break

            # after checking neighbors:
            if all_black:
                output_pixels[x, y] = 0   # keep black
            else:
                output_pixels[x, y] = 255 # erode to white

    return output_image

def dilate_image(image: Image.Image) -> Image.Image:
    # Dilate a binary (black & white) image by one pixel using a 3x3 square kernel.
    width, height = image.size
    input_pixels = image.load()
    output_image = Image.new("L", (width, height), 255)
    output_pixels = output_image.load()

    for y in range(height):
        for x in range(width):
            pixel = input_pixels[x, y]

            # if it's black, keep it black and set neighbors to black
            if pixel == 0:
                output_pixels[x, y] = 0  # keep black

                # set neighbors to black
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        nx = x + dx
                        ny = y + dy

                        # skip out-of-bounds neighbors
                        if nx < 0 or nx >= width or ny < 0 or ny >= height:
                            continue

                        output_pixels[nx, ny] = 0  # set neighbor to black
            else:
                # pixel is white; only set to white if not already blackened by neighbor
                if output_pixels[x, y] != 0:
                    output_pixels[x, y] = 255  # keep white

    return output_image


def opening(image: Image.Image) -> Image.Image:
    # erosion then dilation
    eroded = erode_image(image)
    opened = dilate_image(eroded)
    return opened


def closing(image: Image.Image) -> Image.Image:
    # dilation then erosion
    dilated = dilate_image(image)
    closed = erode_image(dilated)
    return closed
