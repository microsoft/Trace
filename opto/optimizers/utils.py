def print_color(message, color=None, logger=None):
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
    }
    print(
        f"{colors.get(color, '')}{message}\033[0m"
    )  # Default to no color if invalid color is provided

    if logger is not None:
        logger.log(message)
