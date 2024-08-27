import logging

def uno():
    """
    Returns the integer 1.

    :return: The integer 1
    :rtype: int
    """
    return 1

def dos():
    """
    Returns the integer 2. If an exception occurs, logs the exception with the message "Beh!".

    :return: The integer 2
    :rtype: int
    """
    try:
        return 2
    except Exception:
        logging.exception("Beh!")

def tres():
    """
    Returns the integer 3.

    :return: The integer 3
    :rtype: int
    """
    return 3