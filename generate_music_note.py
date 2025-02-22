from PIL import Image, ImageDraw
import sys

# Constants
SIZE = 50  # Reduce image size to fit everything
STAFF_LINES = 5
STAFF_SPACING = 5  # Reduce spacing for compactness
STAFF_Y_START = 20  # Move staff lower for better positioning
WHOLE_NOTE_RADIUS = 3  # Scale down the note size
NOTE_X = 25  # Adjust position closer to clef
NOTE_Y = STAFF_Y_START + (STAFF_SPACING * 2)  # Third line placement

# Clef selection
clef_type = sys.argv[1] if len(sys.argv) > 1 else "treble"
clef_images = {
    "treble": ("images/treble.png", 375, 640, (5, STAFF_Y_START - 10)),
    "bass": ("images/bass.png", 549, 640, (5, STAFF_Y_START))
}

# Create a blank square image with a white background
img = Image.new("RGB", (SIZE, SIZE), "white")
draw = ImageDraw.Draw(img)

# Draw the staff lines
for i in range(STAFF_LINES):
    y = STAFF_Y_START + (i * STAFF_SPACING)
    draw.line([(5, y), (SIZE - 5, y)], fill="black", width=1)

# Load and paste the clef image
if clef_type in clef_images:
    clef_path, orig_width, orig_height, position = clef_images[clef_type]
    try:
        clef_img = Image.open(clef_path).convert("RGBA")
        clef_img = clef_img.resize((int(orig_width * 0.05), int(orig_height * 0.05)))  # Scale proportionally
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
img.save("music_staff.png")
img.show()
