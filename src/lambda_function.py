import os
import json
import base64
from generate_quiz import create_pdf

# Load the required password from an environment variable
REQUIRED_PASSWORD = os.getenv("PASSWORD")

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
        quiz_type = query_params.get("type", "addition")
        digits = query_params.get("digits", "1")  # Default to "1", then convert to int safely

        try:
            digits = int(digits)
        except ValueError:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Digits must be a valid positive integer."}),
                "headers": {'Content-Type': 'application/json'}
            }

        print(f"Quiz type: {quiz_type}, Digits: {digits}")  # Log quiz_type and digits

        # 4. Validate input
        valid_quiz_types = ["addition", "subtraction", "multiplication", "division", "music"]
        if quiz_type not in valid_quiz_types:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"Invalid quiz type. Must be one of: {', '.join(valid_quiz_types)}."}),
                "headers": {'Content-Type': 'application/json'}
            }

        if quiz_type == "music" and digits not in [1, 2, 3]:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "For music quizzes, digits must be 1, 2, or 3 (treble, bass, mixed)."}),
                "headers": {'Content-Type': 'application/json'}
            }
        if quiz_type != "music" and digits < 1:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Digits must be a positive integer."}),
                "headers": {'Content-Type': 'application/json'}
            }

        # 5. Generate the PDF 
        print("Generating PDF...")  # Log before PDF generation
        pdf_content = create_pdf(quiz_type, digits)

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
