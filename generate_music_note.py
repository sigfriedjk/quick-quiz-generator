import cv2
import numpy as np
from PIL import Image, ImageDraw
import sys

# Constants
SIZE = 50  # Reduce image size to fit everything
STAFF_LINES = 5
STAFF_SPACING = 7  # Reduce spacing for compactness
STAFF_Y_START = 10  # Move staff lower for better positioning
WHOLE_NOTE_RADIUS = 5  # Scale down the note size
NOTE_X = 27  # Adjust position closer to clef
note_positions = {
    "A": STAFF_Y_START + (STAFF_SPACING * 4),
    "B": STAFF_Y_START + (STAFF_SPACING * 3.5),
    "C": STAFF_Y_START + (STAFF_SPACING * 3),
    "D": STAFF_Y_START + (STAFF_SPACING * 2.5),
    "E": STAFF_Y_START + (STAFF_SPACING * 2),
    "F": STAFF_Y_START + (STAFF_SPACING * 1.5),
    "G": STAFF_Y_START + (STAFF_SPACING * 1)
}
note_letter = sys.argv[2] if len(sys.argv) > 2 else "C"
NOTE_Y = note_positions.get(note_letter.upper(), STAFF_Y_START + (STAFF_SPACING * 2))  # Third line placement

# Clef selection
clef_type = sys.argv[1] if len(sys.argv) > 1 else "treble"
clef_images = {
    "treble": ("images/treble.png", 375, 640, (-3, STAFF_Y_START - 11), 0.08),
    "bass": ("images/bass.png", 549, 640, (3, STAFF_Y_START +2 ), 0.04)
}

# Create a blank square image with a white background
img = Image.new("RGB", (SIZE, SIZE), "white")
draw = ImageDraw.Draw(img)

# Draw the staff lines
for i in range(STAFF_LINES):
    y = STAFF_Y_START + (i * STAFF_SPACING)
    draw.line([(0, y), (SIZE, y)], fill="black", width=1)

# Load and paste the clef image
if clef_type in clef_images:
    clef_path, orig_width, orig_height, position, factor = clef_images[clef_type]
    try:
        clef_img = cv2.imread(clef_path, cv2.IMREAD_UNCHANGED)
        scale_factor = factor
        new_size = (int(orig_width * scale_factor), int(orig_height * scale_factor))
        clef_img = cv2.resize(clef_img, new_size, interpolation=cv2.INTER_AREA)
        clef_img = Image.fromarray(cv2.cvtColor(clef_img, cv2.COLOR_BGRA2RGBA))
        img.paste(clef_img, position, clef_img)  # Adjust position
    except FileNotFoundError:
        print(f"Error: {clef_path} not found. Make sure it's in the correct directory.")
else:
    print("Invalid clef type. Use 'treble' or 'bass'.")
    sys.exit(1)

# Draw the whole note (ellipse)
draw.ellipse(
    [(NOTE_X - WHOLE_NOTE_RADIUS, NOTE_Y - WHOLE_NOTE_RADIUS),
     (NOTE_X + WHOLE_NOTE_RADIUS * 1.5, NOTE_Y + WHOLE_NOTE_RADIUS)], 
    outline="black", width=1
)

# Save and show the image
output_path = "output/music_staff.png"
img.save(output_path)
img.show()
