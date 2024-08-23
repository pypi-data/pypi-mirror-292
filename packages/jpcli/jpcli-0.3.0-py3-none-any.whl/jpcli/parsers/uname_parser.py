# jpcli/parsers/uname_parser.py
def parse(uname_output):
    """
    Parse the output of the `uname` command.
    """
    uname_info = uname_output.strip().split()
    keys = ['sysname', 'nodename', 'release', 'version', 'machine', 'processor', 'hardware_platform', 'os']
    return dict(zip(keys, uname_info))
