from generate_music_note import get_note_position


def test_treble_clef_positions():
    """Test function to ensure get_note_position outputs expected values for treble clef."""
    expected_positions = {
        'G2': 13.5,
        'F2': 10,
        'E2': 6.5,
        'D2': 3.0,
        'C2': -0.5,
        'B2': -4.0,
        'A2': -7.5,
        'G1': -11.0,
        'F1': -14.5,
        'E1': -18.0,
        'D1': -21.5,
        'C1': -24.0,
        'B1': -27.5,
        'A1': -31.5,
    }

    errors = []
    
    for note, expected_value in expected_positions.items():
        result = get_note_position("treble", note)
        if result != expected_value:
            errors.append(f"Error: {note} expected {expected_value} but got {result}")
    
    if errors:
        for error in errors:
            print(error)
        return False
    else:
        print("All treble clef positions are correct!")
        return True

# Run the test function
test_treble_clef_positions()


def test_bass_clef_positions():
    """Test function to ensure get_note_position outputs expected values for bass clef."""
    expected_positions = {
        'G2': 31.0,
        'F2': 27.5,
        'E2': 24.0,
        'D2': 20.5,
        'C2': 17.0,
        'B2': 13.5,
        'A2': 10.0,
        'G1': 6.5,
        'F1': 3.0,
        'E1': -0.5,
        'D1': -4.0,
        'C1': -7.5,
        'B1': -11.0,
        'A1': -14.5
    }
    
    errors = []
    
    for note, expected_value in expected_positions.items():
        result = get_note_position("bass", note)
        if result != expected_value:
            errors.append(f"Error: {note} expected {expected_value} but got {result}")
    
    if errors:
        for error in errors:
            print(error)
        return False
    else:
        print("All bass clef positions are correct!")
        return True




def main():

    # Run the test function
    test_bass_clef_positions()

    """
    Main function to test the lambda_handler locally.
    """
    # Simulating an environment variable
    os.environ["PASSWORD"] = "nHvZtlP17pMWbMX3mUPbRZ96"

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
