def parse(journalctl_output):
    """
    Parse the contents of journalctl output.
    """
    try:
        journalctl_lines = journalctl_output.strip().split('\n')
        journalctl_list = []
        for line in journalctl_lines:
            journalctl_list.append(line)
        return journalctl_list
    except Exception as e:
        return {"error": str(e), "message": "Failed to parse journalctl output"}
