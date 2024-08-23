# jpcli/parsers/os_release_parser.py
def parse(os_release_output):
    """
    Parse the contents of /etc/os-release.
    """
    os_release_dict = {}
    for line in os_release_output.strip().split('\n'):
        if '=' in line:
            key, value = line.split('=', 1)
            os_release_dict[key] = value.strip('"')
    return os_release_dict
