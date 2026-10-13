"""Split each transparent nine-sticker atlas into clean, reusable art tiles.

Foreground pieces are assigned to the cell containing their visual center. This
keeps a neighboring sticker's stray edges from leaking into printable cards.
"""
from pathlib import Path
from PIL import Image
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "scripts/art/raw"
OUT = ROOT / "scripts/art/crops"
WEB_OUT = ROOT / "dist/art/student-packs"

# A small, consistent set of book-matched illustrations for the weekly
# workspace and the student-pack download cards. The print PDFs use the full
# set of nine tiles; the site only needs four optimized previews per book.
WEB_PREVIEWS = {
    1: (0, 1, 2, 6),
    2: (7, 2, 5, 6),
    3: (7, 0, 2, 3),
    4: (0, 4, 5, 1),
    5: (0, 2, 4, 1),
    6: (5, 0, 3, 6),
    7: (8, 0, 4, 6),
    8: (8, 0, 2, 4),
    9: (5, 0, 2, 6),
}
WEB_ROLES = ("featured", "story-question", "picture-cards", "make-it")


def roots(parent, value):
    while parent[value] != value:
        parent[value] = parent[parent[value]]
        value = parent[value]
    return value


def build(week):
    image = Image.open(RAW / f"week-{week}.png").convert("RGBA")
    pixels = np.asarray(image)
    height, width = pixels.shape[:2]
    foreground = pixels[:, :, 3] > 18
    parent = [0]
    runs = []
    previous = []

    def join(first, second):
        first, second = roots(parent, first), roots(parent, second)
        if first != second:
            parent[max(first, second)] = min(first, second)

    for y in range(height):
        edges = np.diff(np.r_[False, foreground[y], False].astype(np.int8))
        starts = np.flatnonzero(edges == 1)
        ends = np.flatnonzero(edges == -1)
        current = []
        previous_index = 0
        for start, end in zip(starts, ends):
            while previous_index < len(previous) and previous[previous_index][1] < start - 1:
                previous_index += 1
            connected = []
            index = previous_index
            while index < len(previous) and previous[index][0] <= end:
                connected.append(previous[index][2])
                index += 1
            if connected:
                label = connected[0]
                for other in connected[1:]:
                    join(label, other)
            else:
                label = len(parent)
                parent.append(label)
            start, end = int(start), int(end)
            current.append((start, end, label))
            runs.append((y, start, end, label))
        previous = current

    stats = {}
    for y, start, end, label in runs:
        label = roots(parent, label)
        count = end - start
        item = stats.setdefault(label, [0, 0.0, 0.0])
        item[0] += count
        item[1] += (start + end - 1) * count / 2
        item[2] += y * count

    cells = {index: set() for index in range(9)}
    for label, (area, sum_x, sum_y) in stats.items():
        if area < 20:
            continue
        center_x, center_y = sum_x / area, sum_y / area
        col = min(2, int(center_x / (width / 3)))
        row = min(2, int(center_y / (height / 3)))
        cells[row * 3 + col].add(label)

    for tile_index, labels in cells.items():
        if not labels:
            raise ValueError(f"Week {week} atlas tile {tile_index} has no artwork")
        selected = [(y, x0, x1) for y, x0, x1, label in runs if roots(parent, label) in labels]
        x0 = min(start for _, start, _ in selected)
        x1 = max(end for _, _, end in selected)
        y0 = min(y for y, _, _ in selected)
        y1 = max(y + 1 for y, _, _ in selected)
        alpha = np.zeros((y1 - y0, x1 - x0), dtype=np.uint8)
        for y, start, end, label in runs:
            if roots(parent, label) in labels:
                alpha[y - y0, start - x0:end - x0] = pixels[y, start:end, 3]
        sticker = image.crop((x0, y0, x1, y1))
        sticker.putalpha(Image.fromarray(alpha))
        padded = Image.new("RGBA", (sticker.width + 24, sticker.height + 24), (0, 0, 0, 0))
        padded.alpha_composite(sticker, (12, 12))
        padded.thumbnail((480, 480), Image.Resampling.LANCZOS)
        padded.save(OUT / f"week-{week}-tile-{tile_index}.png", optimize=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    WEB_OUT.mkdir(parents=True, exist_ok=True)
    for week in range(1, 10):
        build(week)
        for role, tile_index in zip(WEB_ROLES, WEB_PREVIEWS[week]):
            image = Image.open(OUT / f"week-{week}-tile-{tile_index}.png").convert("RGBA")
            image.thumbnail((440, 440), Image.Resampling.LANCZOS)
            image.save(WEB_OUT / f"week-{week}-{role}.png", optimize=True)
    bow = Image.open(RAW / "week-1-bow.png").convert("RGBA")
    alpha = bow.getchannel("A").point(lambda value: 255 if value > 8 else 0)
    bounds = alpha.getbbox()
    if bounds:
        left, top, right, bottom = bounds
        pad = 18
        bow = bow.crop((max(0, left - pad), max(0, top - pad), min(bow.width, right + pad), min(bow.height, bottom + pad)))
    bow.thumbnail((480, 480), Image.Resampling.LANCZOS)
    bow.save(OUT / "week-1-bow.png", optimize=True)
    print("Built 81 isolated transparent student-art tiles and 36 weekly web previews.")


if __name__ == "__main__":
    main()
