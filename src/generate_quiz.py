import random
import argparse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
from generate_music_note import draw_music_staff

# Define music note mappings (treble and bass clef)
music_notes = {
    1: ["treble clef: C1", "treble clef: D1", "treble clef: E1", "treble clef: F1", "treble clef: G1",
        "treble clef: C2", "treble clef: D2", "treble clef: E2", "treble clef: F2", "treble clef: G2"],
    2: ["bass clef: C1", "bass clef: D1", "bass clef: E1", "bass clef: F1", "bass clef: G1",
        "bass clef: C2", "bass clef: D2", "bass clef: E2", "bass clef: F2", "bass clef: G2"],
    3: ["treble clef: C1", "treble clef: D1", "treble clef: E1", "treble clef: F1", "treble clef: G1",
        "treble clef: C2", "treble clef: D2", "treble clef: E2", "treble clef: F2", "treble clef: G2",
        "bass clef: C1", "bass clef: D1", "bass clef: E1", "bass clef: F1", "bass clef: G1",
        "bass clef: C2", "bass clef: D2", "bass clef: E2", "bass clef: F2", "bass clef: G2"]
}

def generate_math_problem(problem_type, digits_first=2, digits_second=None):
    """Generates a random math problem using configurable digit lengths for each number."""
    digits_second = digits_first if digits_second is None else digits_second

    def digit_bounds(digits):
        lower = 10 ** (digits - 1)
        upper = (10 ** digits) - 1
        return lower, upper

    lower_first, upper_first = digit_bounds(digits_first)
    lower_second, upper_second = digit_bounds(digits_second)

    if problem_type in ["addition", "subtraction"]:
        num1 = random.randint(lower_first, upper_first)
        num2 = random.randint(lower_second, upper_second)
        operator = "+" if problem_type == "addition" else "-"
    elif problem_type == "multiplication":
        num1 = random.randint(lower_first, upper_first)
        num2 = random.randint(lower_second, upper_second)
        operator = "×"
    elif problem_type == "division":
        if digits_second > digits_first:
            raise ValueError("digits_second cannot be greater than digits_first for division problems.")

        num1 = None
        for _ in range(1000):
            num2 = random.randint(lower_second, upper_second)
            if num2 == 0:
                continue

            min_multiplier = max((lower_first + num2 - 1) // num2, 1)
            max_multiplier = upper_first // num2

            if min_multiplier > max_multiplier:
                continue

            candidate = num2 * random.randint(min_multiplier, max_multiplier)
            if lower_first <= candidate <= upper_first:
                num1 = candidate
                break

        if num1 is None:
            raise ValueError("Unable to generate division problem with the provided digit lengths.")

        operator = "÷"
    else:
        raise ValueError(f"Unsupported problem type: {problem_type}")

    return f"{num1} {operator} {num2} = ______"

def generate_quiz(quiz_type, digits_first, digits_second=None):
    """Generates 10 quiz questions of the specified type."""
    if quiz_type == "music":
        notes = music_notes.get(digits_first, music_notes[3])
        return [random.choice(notes) for _ in range(10)]

    return [
        generate_math_problem(quiz_type, digits_first, digits_second)
        for _ in range(10)
    ]

def create_pdf(quiz_type, digits_first, digits_second=None):
    """Creates a PDF in memory with 4 quizzes per page in two columns with improved spacing."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 50
    column_spacing = width // 2  # Midpoint for two columns
    quiz_per_page = 4
    spacing = height // (quiz_per_page // 2 + 1)  # Adjusted spacing
    math_question_spacing = 30  # Increased spacing between questions
    music_question_spacing = 50  # Increased spacing between questions
    image_column_offset = 120  # Space images into a second column within each quiz
    
    for i in range(4):  # 4 quizzes per page
        quiz = generate_quiz(quiz_type, digits_first, digits_second)
        x_position = margin if i % 2 == 0 else column_spacing + margin
        y_position = height - margin - ((i // 2) * spacing)  # Keep first row unchanged
        if i >= 2:
            y_position -= 80  # Offset second row downward only
        
        c.drawString(x_position, y_position, f"{quiz_type.capitalize()} Quiz")
        for j, question in enumerate(quiz):
            if quiz_type == "music":
                clef, note = question.split(" clef: ")
                music_image = draw_music_staff(clef.lower(), note)  # Generate the image dynamically
                if music_image:
                    img_reader = ImageReader(music_image)
                    img_x_position = x_position + 20 if j % 2 == 0 else x_position + 20 + image_column_offset
                    c.drawImage(img_reader, img_x_position, y_position - 20 - (j//2 + 1) * music_question_spacing, width=50, height=50)
            else:
                c.drawString(x_position + 20, y_position - (j+1) * math_question_spacing, question)
    
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a quiz PDF of a specific type.")
    parser.add_argument("type", choices=["addition", "subtraction", "multiplication", "division", "music"], help="Type of quiz to generate")
    parser.add_argument("digits", type=int, nargs="?", help="Default number of digits for both operands, or clef selection for music (1=treble, 2=bass, 3=mixed)")
    parser.add_argument("--digits-first", "-d1", dest="digits_first", type=int, help="Number of digits for the first operand")
    parser.add_argument("--digits-second", "-d2", dest="digits_second", type=int, help="Number of digits for the second operand")
    args = parser.parse_args()

    if args.type == "music":
        clef_selection = args.digits if args.digits is not None else (args.digits_first if args.digits_first is not None else 3)
        if clef_selection not in [1, 2, 3]:
            parser.error("For music quizzes, digits must be 1, 2, or 3 (treble, bass, mixed).")
        try:
            pdf_data = create_pdf(args.type, clef_selection)
        except ValueError as exc:
            parser.error(str(exc))
    else:
        digits_first = args.digits_first if args.digits_first is not None else (args.digits if args.digits is not None else 2)
        digits_second = args.digits_second if args.digits_second is not None else (args.digits if args.digits is not None else None)

        if digits_first < 1 or (digits_second is not None and digits_second < 1):
            parser.error("Digits must be positive integers for math quizzes.")

        try:
            pdf_data = create_pdf(args.type, digits_first, digits_second)
        except ValueError as exc:
            parser.error(str(exc))
    filename = f"quiz_{args.type}.pdf"
    
    with open(filename, "wb") as f:
        f.write(pdf_data)
        
    print(f"Quiz saved as {filename}")
