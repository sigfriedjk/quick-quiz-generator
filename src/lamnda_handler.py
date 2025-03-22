from generate_quiz import create_pdf 
import json
from urllib.parse import parse_qs
from io import BytesIO

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
        # 1. Parse query parameters
        query_string = event.get('rawQueryString', '')
        query_params = parse_qs(query_string)
        quiz_type = query_params.get('type', ['addition'])[0]
        digits = int(query_params.get('digits', [2])[0])

        # 2. Validate input
        if quiz_type not in ["addition", "subtraction", "multiplication", "division", "music"]:
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {"error": "Invalid quiz type. Must be one of: addition, subtraction, multiplication, division, music"}),
                "headers": {'Content-Type': 'application/json'}
            }
        if quiz_type == "music" and digits not in [1, 2, 3]:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "For music quizzes, digits must be 1, 2, or 3 (treble, bass, mixed)"}),
                "headers": {'Content-Type': 'application/json'}
            }
        if quiz_type != "music" and (not isinstance(digits, int) or digits < 1):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Digits must be a positive integer"}),
                "headers": {'Content-Type': 'application/json'}
            }

        # 3. Generate the PDF 
        pdf_content = create_pdf(quiz_type, digits)


        # 4. Construct the response for download
        filename = f"quiz_{quiz_type}.pdf"
        response = {
            "statusCode": 200,
            "body": pdf_content.decode('latin-1'),
            "headers": {
                'Content-Type': 'application/pdf',
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Length': len(pdf_content)
            },
            "isBase64Encoded": True
        }
        return response

    except Exception as e:
        # 5. Handle errors
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": error_message}),
            "headers": {'Content-Type': 'application/json'}
        }

def main():
    """
    Main function to test the lambda_handler locally.
    """
    # Create a sample event and context.  Adjust the event to test different quiz types and digits.
    event = {
        'rawQueryString': 'type=addition&digits=2',  # Example: addition quiz, 2 digits
        # 'queryString': {'type': 'music', 'digits': '1'} #Example for music quiz
    }
    context = {}  # You can pass an empty context for local testing

    # Call the lambda_handler
    response = lambda_handler(event, context)

    # Print the response
    print(json.dumps(response))

if __name__ == "__main__":
    main()