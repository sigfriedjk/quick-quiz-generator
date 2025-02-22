import random
import argparse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os
from generate_music_note import draw_music_staff

# Define music note mappings (treble and bass clef)
music_notes = [
    "treble clef: C1", "treble clef: D1", "treble clef: E1", "treble clef: F1", "treble clef: G1", "treble clef: A1", "treble clef: B1",
    "treble clef: C2", "treble clef: D2", "treble clef: E2", "treble clef: F2", "treble clef: G2",
    "bass clef: C1", "bass clef: D1", "bass clef: E1", "bass clef: F1", "bass clef: G1", "bass clef: A1", "bass clef: B1",
    "bass clef: C2", "bass clef: D2", "bass clef: E2", "bass clef: F2", "bass clef: G2"
]

def generate_math_problem(problem_type, digits=2):
    """Generates a random math problem of the specified type with configurable digit length."""
    lower = 10 ** (digits - 1)
    upper = (10 ** digits) - 1
    
    if problem_type in ["addition", "subtraction"]:
        num1 = random.randint(lower, upper)
        num2 = random.randint(lower, upper)
        operator = "+" if problem_type == "addition" else "-"
    elif problem_type == "multiplication":
        num1 = random.randint(lower, upper)
        num2 = random.randint(1, 9)  # Keep second number single-digit for easier multiplication
        operator = "×"
    elif problem_type == "division":
        num2 = random.randint(1, 9)  # Keep divisor single-digit
        num1 = num2 * random.randint(lower, upper // num2)  # Ensure divisibility
        operator = "÷"
    else:
        return random.choice(music_notes)
    
    return f"{num1} {operator} {num2} = ______"

def generate_quiz(quiz_type):
    """Generates 10 quiz questions of the specified type."""
    return [generate_math_problem(quiz_type) for _ in range(10)]

def create_pdf(quiz_type, filename="quiz.pdf"):
    """Creates a PDF with 4 quizzes per page in two columns with improved spacing."""
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    margin = 50
    column_spacing = width // 2  # Midpoint for two columns
    quiz_per_page = 4
    spacing = height // (quiz_per_page // 2 + 1)  # Adjusted spacing
    question_spacing = 40  # Increased spacing between questions
    
    for i in range(4):  # 4 quizzes per page
        quiz = generate_quiz(quiz_type)
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
                    c.drawImage(img_reader, x_position + 20, y_position - (j+1) * question_spacing, width=50, height=50)
            else:
                c.drawString(x_position + 20, y_position - (j+1) * question_spacing, question)
    
    c.save()
    print(f"Quiz saved as {filepath}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a quiz PDF of a specific type.")
    parser.add_argument("type", choices=["addition", "subtraction", "multiplication", "division", "music"], help="Type of quiz to generate")
    args = parser.parse_args()
    
    create_pdf(args.type, filename=f"quiz_{args.type}.pdf")
