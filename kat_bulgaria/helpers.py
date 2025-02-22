"""Helper functions"""

def strtobool(value: str) -> bool:
    """Checks if string is truthy"""
    lowered = value.lower()
    if lowered in ("y", "yes", "on", "1", "true", "t"):
        return True
    return False