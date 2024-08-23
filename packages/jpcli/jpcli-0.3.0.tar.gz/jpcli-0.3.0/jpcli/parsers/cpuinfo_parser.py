# cpuinfo_parser.py

def parse(command_output):
    """
    Parses the output of the 'cat /proc/cpuinfo' command into a list of dictionaries,
    where each dictionary contains information about one processor core.

    Args:
    command_output (str): The string output from the 'cat /proc/cpuinfo' command.

    Returns:
    list: A list of dictionaries, each representing a CPU core's information.
    """
    processors = []
    current_processor = {}
    lines = command_output.splitlines()
    for line in lines:
        line = line.strip()  # Remove leading and trailing whitespace
        if line:
            key_value_pair = line.split(':', 1)  # Split only on the first colon
            if len(key_value_pair) == 2:
                key, value = key_value_pair
                key = key.strip()
                value = value.strip()
                current_processor[key] = value
        else:
            # Handle new processor block (empty line)
            if current_processor:
                processors.append(current_processor)
                current_processor = {}
    if current_processor:
        processors.append(current_processor)
    return processors
