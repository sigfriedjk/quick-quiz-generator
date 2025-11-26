import os
import json
import base64
from generate_quiz import create_pdf

# Load the required password from an environment variable
REQUIRED_PASSWORD = os.getenv("PASSWORD")


def parameter_help(message=None):
    """Build a response describing the accepted parameters."""

    details = {
        "type": {
            "description": "Quiz category to generate.",
            "allowed_values": ["addition", "subtraction", "multiplication", "division", "music"],
            "default": "addition"
        },
        "digits": {
            "description": "Shortcut to set both digits1 and digits2 for math quizzes. For music, selects the clef.",
            "allowed_values": "Positive integers for math. For music use 1 (treble), 2 (bass), or 3 (mixed).",
            "default": "2 for math, 3 for music"
        },
        "digits1 / digits_first": {
            "description": "Number of digits for the first operand in math quizzes.",
            "allowed_values": "Positive integers.",
            "default": "2 (or value from digits if provided)"
        },
        "digits2 / digits_second": {
            "description": "Number of digits for the second operand in math quizzes.",
            "allowed_values": "Positive integers. For division, cannot exceed digits1.",
            "default": "Matches digits1 unless digits is provided"
        }
    }

    response_body = {"parameters": details}
    if message:
        response_body["message"] = message

    return {
        "statusCode": 400,
        "body": json.dumps(response_body),
        "headers": {'Content-Type': 'application/json'}
    }

def lambda_handler(event, context):
    """
    Handles requests to generate a quiz PDF and returns it as a download.

    Args:
        event (dict): The event data passed to the Lambda function.
        context (object): The Lambda context object.

    Returns:
        dict: A dictionary containing the response with the PDF as a download.
    """
    try:
        print(f"Received event: {json.dumps(event, indent=2)}")  # Log the entire event for debugging

        # 1. Parse query parameters correctly
        query_params = event.get("queryStringParameters", {}) or {}  # Ensure it is a dictionary

        print(f"Parsed query parameters: {query_params}")  # Log the query parameters

        # 2. Validate password
        password = query_params.get("password")

        if not REQUIRED_PASSWORD:
            print("Environment variable PASSWORD is not set.")
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "Server misconfiguration: PASSWORD is not set."}),
                "headers": {'Content-Type': 'application/json'}
            }

        if password != REQUIRED_PASSWORD:
            error_message = "Invalid or missing password."
            print(error_message)  # Log unauthorized access
            return {
                "statusCode": 403,
                "body": json.dumps({"error": error_message}),
                "headers": {'Content-Type': 'application/json'}
            }

        # 3. Extract quiz parameters
        quiz_type = query_params.get("type")
        raw_digits = query_params.get("digits")
        raw_digits_first = query_params.get("digits1") or query_params.get("digits_first") or raw_digits
        raw_digits_second = query_params.get("digits2") or query_params.get("digits_second")
        if raw_digits_second is None and raw_digits is not None:
            raw_digits_second = raw_digits

        if not any([quiz_type, raw_digits, raw_digits_first, raw_digits_second]):
            return parameter_help("No quiz parameters provided. Include at least one of the documented parameters.")

        quiz_type = quiz_type or "addition"

        def parse_int(value, field_name):
            if value is None:
                return None
            try:
                return int(value)
            except (TypeError, ValueError):
                raise ValueError(f"{field_name} must be a valid integer.")

        try:
            digits_first = parse_int(raw_digits_first, "digits1")
            digits_second = parse_int(raw_digits_second, "digits2")
        except ValueError as exc:
            return parameter_help(str(exc))

        print(f"Quiz type: {quiz_type}, digits_first: {digits_first}, digits_second: {digits_second}")  # Log quiz_type and digits

        # 4. Validate input
        valid_quiz_types = ["addition", "subtraction", "multiplication", "division", "music"]
        if quiz_type not in valid_quiz_types:
            return parameter_help(f"Invalid quiz type. Must be one of: {', '.join(valid_quiz_types)}.")

        if quiz_type == "music":
            clef_selection = digits_first if digits_first is not None else 3
            if clef_selection not in [1, 2, 3]:
                return parameter_help("For music quizzes, digits must be 1, 2, or 3 (treble, bass, mixed).")
            digits_first = clef_selection
            digits_second = None
        else:
            digits_first = digits_first if digits_first is not None else 2
            digits_second = digits_second if digits_second is not None else digits_first

            if digits_first < 1 or digits_second < 1:
                return parameter_help("Digits must be positive integers for math quizzes.")

        # 5. Generate the PDF
        print("Generating PDF...")  # Log before PDF generation
        try:
            pdf_content = create_pdf(quiz_type, digits_first, digits_second)
        except ValueError as exc:
            return parameter_help(str(exc))

        if not pdf_content:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "PDF generation failed."}),
                "headers": {'Content-Type': 'application/json'}
            }

        if hasattr(pdf_content, "read"):  # If it's a file-like object
            pdf_content = pdf_content.read()

        print("PDF generated.")  # Log after PDF generation

        # 6. Construct the response for download
        filename = f"quiz_{quiz_type}.pdf"
        response = {
            "statusCode": 200,
            "body": base64.b64encode(pdf_content).decode("utf-8"),  # Ensure correct base64 encoding
            "headers": {
                "Content-Type": "application/pdf",
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length": str(len(pdf_content))
            },
            "isBase64Encoded": True
        }

        print(f"Response prepared successfully.")  # Log response
        return response

    except Exception as e:
        # 7. Handle errors
        import traceback
        traceback.print_exc()
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"An error occurred: {str(e)}"}),
            "headers": {'Content-Type': 'application/json'}
        }
