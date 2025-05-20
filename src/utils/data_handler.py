def process_mqtt_data(payload):
    """Process the incoming MQTT payload and return structured data."""
    try:
        data = json.loads(payload)
        # Assuming the data contains 'x' and 'y' coordinates
        return data.get('x'), data.get('y')
    except json.JSONDecodeError:
        print("Failed to decode JSON payload.")
        return None, None

def filter_data(data, criteria):
    """Filter the data based on specified criteria."""
    return [item for item in data if item meets criteria]

def format_data_for_display(data):
    """Format the data for display in the GUI."""
    return f"X: {data[0]}, Y: {data[1]}" if data else "No data available"