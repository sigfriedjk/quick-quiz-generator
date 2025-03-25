from generate_quiz import create_pdf 
import json
from urllib.parse import parse_qs
import base64

# Define the required password
REQUIRED_PASSWORD = "nHvZtlP17pMWbMX3mUPbRZ96"

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
        print(f"Received event: {event}")  # Log the entire event

        # 1. Parse query parameters
        query_string = event.get('rawQueryString', '')
        query_params = parse_qs(query_string)
        print(f"Parsed query parameters: {query_params}")  # Log the query parameters

        # 2. Validate password
        password = query_params.get('password', [None])[0]
        if password != REQUIRED_PASSWORD:
            error_message = "Invalid or missing password."
            print(error_message)  # Log unauthorized access
            return {
                "statusCode": 403,
                "body": json.dumps({"error": error_message}),
                "headers": {'Content-Type': 'application/json'}
            }

        # 3. Extract quiz parameters
        quiz_type = query_params.get('type', ['addition'])[0]
        digits = int(query_params.get('digits', [1])[0])

        print(f"Quiz type: {quiz_type}, Digits: {digits}")  # Log quiz_type and digits

        # 4. Validate input
        if quiz_type not in ["addition", "subtraction", "multiplication", "division", "music"]:
            error_message = f"Invalid quiz type. Must be one of: addition, subtraction, multiplication, division, music. Received: {quiz_type}"
            print(error_message)  # Log the error
            return {
                "statusCode": 400,
                "body": json.dumps({"error": error_message}),
                "headers": {'Content-Type': 'application/json'}
            }
        if quiz_type == "music" and digits not in [1, 2, 3]:
            error_message = f"For music quizzes, digits must be 1, 2, or 3 (treble, bass, mixed). Received: {digits}"
            print(error_message)  # Log the error
            return {
                "statusCode": 400,
                "body": json.dumps({"error": error_message}),
                "headers": {'Content-Type': 'application/json'}
            }
        if quiz_type != "music" and (not isinstance(digits, int) or digits < 1):
            error_message = f"Digits must be a positive integer. Received: {digits}"
            print(error_message)  # Log the error
            return {
                "statusCode": 400,
                "body": json.dumps({"error": error_message}),
                "headers": {'Content-Type': 'application/json'}
            }

        # 5. Generate the PDF 
        print("Generating PDF...")  # Log before PDF generation
        pdf_content = create_pdf(quiz_type, digits)
        print("PDF generated.")  # Log after PDF generation

        # 6. Construct the response for download
        filename = f"quiz_{quiz_type}.pdf"
        response = {
            "statusCode": 200,
            "body": base64.b64encode(pdf_content).decode('utf-8'),  # Corrected base64 encoding
            "headers": {
                'Content-Type': 'application/pdf',
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Length': str(len(pdf_content))
            },
            "isBase64Encoded": True
        }
        print(f"Response: {response}")  # Log the response
        return response

    except Exception as e:
        # 7. Handle errors
        error_message = f"An error occurred: {str(e)}"
        print(error_message)  # Log the exception
        import traceback
        traceback.print_exc()
        return {
            "statusCode": 500,
            "body": json.dumps({"error": error_message}),
            "headers": {'Content-Type': 'application/json'}
        }

def main():
    """
    Main function to test the lambda_handler locally.
    """
    # Create a sample event and context. Adjust the event to test different quiz types and digits.
    event = {
        'rawQueryString': 'type=addition&digits=2&password=nHvZtlP17pMWbMX3mUPbRZ96',  # Example: correct password
    }
    context = {}  # You can pass an empty context for local testing

    # Call the lambda_handler
    response = lambda_handler(event, context)

    # Print the response
    print(json.dumps(response, indent=2))

if __name__ == "__main__":
    main()
