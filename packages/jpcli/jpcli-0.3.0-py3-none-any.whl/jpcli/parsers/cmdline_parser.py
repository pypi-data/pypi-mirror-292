def parse(cmdline_output):
    """
    Parse the contents of /proc/cmdline.
    """
    cmdline_dict = {}
    for item in cmdline_output.strip().split():
        if '=' in item:
            key, value = item.split('=', 1)
            cmdline_dict[key] = value
        else:
            cmdline_dict[item] = None
    return cmdline_dict
