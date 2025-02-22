import cv2
import numpy as np
from PIL import Image, ImageDraw
import argparse

# Constants
SIZE = 50  # Reduce image size to fit everything
STAFF_LINES = 5
STAFF_SPACING = 7  # Reduce spacing for compactness
STAFF_Y_START = 10  # Move staff lower for better positioning
NOTE_RADIUS = 4  # Scale down the note size
NOTE_X = 33  # Adjust position closer to clef
NOTE_STEM_HEIGHT = STAFF_SPACING * 3  # Standard stem height

# Note positions for clefs
note_positions = {
    "treble": {
        "A": STAFF_Y_START + (STAFF_SPACING * 4),
        "B": STAFF_Y_START + (STAFF_SPACING * 3.5),
        "C": STAFF_Y_START + (STAFF_SPACING * 3),
        "D": STAFF_Y_START + (STAFF_SPACING * 2.5),
        "E": STAFF_Y_START + (STAFF_SPACING * 2),
        "F": STAFF_Y_START + (STAFF_SPACING * 1.5),
        "G": STAFF_Y_START + (STAFF_SPACING * 1)
    },
    "bass": {
        "A": STAFF_Y_START + (STAFF_SPACING * 2),
        "B": STAFF_Y_START + (STAFF_SPACING * 1.5),
        "C": STAFF_Y_START + (STAFF_SPACING * 1),
        "D": STAFF_Y_START,
        "E": STAFF_Y_START - (STAFF_SPACING * 1),
        "F": STAFF_Y_START - (STAFF_SPACING * 1.5),
        "G": STAFF_Y_START - (STAFF_SPACING * 2)
    }
}

# Clef selection
def draw_music_staff(clef_type, note_letter):
    clef_images = {
        "treble": ("images/treble.png", 375, 640, (-3, STAFF_Y_START - 11), 0.08, 0),
        "bass": ("images/bass.png", 549, 640, (3, STAFF_Y_START + 2), 0.04, 3)
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
        clef_path, orig_width, orig_height, position, factor, xAdj = clef_images[clef_type]
        try:
            clef_img = cv2.imread(clef_path, cv2.IMREAD_UNCHANGED)
            new_size = (int(orig_width * factor), int(orig_height * factor))
            clef_img = cv2.resize(clef_img, new_size, interpolation=cv2.INTER_AREA)
            clef_img = Image.fromarray(cv2.cvtColor(clef_img, cv2.COLOR_BGRA2RGBA))
            img.paste(clef_img, position, clef_img)  # Adjust position
        except FileNotFoundError:
            print(f"Error: {clef_path} not found. Make sure it's in the correct directory.")
    else:
        print("Invalid clef type. Use 'treble' or 'bass'.")
        return

    # Get note position
    NOTE_Y = note_positions.get(clef_type, {}).get(note_letter.upper(), STAFF_Y_START + (STAFF_SPACING * 2))
    ADJUSTED_NOTE_X = NOTE_X + xAdj

    # Determine stem direction
    if NOTE_Y < STAFF_Y_START + (STAFF_SPACING * 2):
        # Note is above middle line, stem goes down on left
        stem_x = ADJUSTED_NOTE_X - NOTE_RADIUS 
        stem_y_start = NOTE_Y 
        stem_y_end = stem_y_start + NOTE_STEM_HEIGHT
    else:
        # Note is below middle line, stem goes up on right
        stem_x = ADJUSTED_NOTE_X + NOTE_RADIUS 
        stem_y_start = NOTE_Y 
        stem_y_end = stem_y_start - NOTE_STEM_HEIGHT

    # Draw the quarter note (filled ellipse with stem)
    draw.ellipse(
        [(ADJUSTED_NOTE_X - NOTE_RADIUS, NOTE_Y - NOTE_RADIUS),
         (ADJUSTED_NOTE_X + NOTE_RADIUS, NOTE_Y + NOTE_RADIUS)], 
        fill="black", outline="black", width=1
    )
    draw.line([(stem_x, stem_y_start), (stem_x, stem_y_end)], fill="black", width=1)

    # Save and show the image
    output_path = "output/music_staff.png"
    img.save(output_path)
    img.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a music staff with a clef and note.")
    parser.add_argument("clef", choices=["treble", "bass"], help="Select the clef (treble or bass)")
    parser.add_argument("note", choices=["A", "B", "C", "D", "E", "F", "G"], help="Select the note (A-G)")
    args = parser.parse_args()
    draw_music_staff(args.clef, args.note)
