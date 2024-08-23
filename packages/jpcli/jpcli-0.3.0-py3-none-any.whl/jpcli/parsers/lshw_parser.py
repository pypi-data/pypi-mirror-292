def parse(command_output):
    def parse_section(lines, indent_level):
        data = {}
        current_section = {}  # Initialize as empty dictionary
        while lines:
            line = lines.pop(0)
            if line.strip() == "":
                continue  # Ignore empty lines
            indent = len(line) - len(line.lstrip())
            if indent < indent_level:
                lines.insert(0, line)
                break
            elif line.startswith('  *-'):
                if current_section:
                    yield current_section
                current_section = {'description': line.split('-')[-1].strip()}  # Initialize here
            elif indent == indent_level and line.startswith('       '):
                parts = line.strip().split(': ', 1)
                if len(parts) == 2:
                    current_section[parts[0]] = parts[1]  # Direct assignment
                elif len(parts) == 1:
                    current_section[parts[0]] = None
            elif indent > indent_level:
                if current_section:
                    if 'subsections' not in current_section:
                        current_section['subsections'] = []
                    current_section['subsections'].extend(parse_section([line] + lines, indent))
        if current_section:
            yield current_section

    lines = command_output.splitlines()
    result = list(parse_section(lines, 0))
    return result


def lshw_parser(command_output):
    lines = command_output.splitlines()
    return list(parse_section(lines, 0))
