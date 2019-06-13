"""
Utility methods
"""

def right_pad(message, pad_to=20, pad_with=' '):
    """Pad a string with chars on the right until it reaches a certain width

    Useful for aligning columns in console outputs.
    """
    message = str(message)
    while len(message) < pad_to:
        message = message + pad_with
    return message
