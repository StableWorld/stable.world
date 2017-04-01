import re
from functools import wraps


def get_indent(lines):
    matches = [re.match('^([^\w\-]+)', l) for l in lines if l]
    spaces = {m.group() for m in matches if m}
    return min(spaces, key=len)


def get_section(lines, section_name, indent=''):
    header = '{}{}:'.format(indent, section_name)
    section = [(i, line) for i, line in enumerate(lines) if line.startswith(header)]

    if not section:
        return None, None, None

    section_start = section[0][0] + 1

    section_lines = [
        (i, line) for i, line
        in enumerate(lines[section_start:], section_start)
        if re.match('^{}[\w\-]'.format(indent), line)
    ]

    if not section_lines:
        section_end = len(lines)
    else:
        section_end = section_lines[0][0]

    section_indent = get_indent(lines[section_start: section_end])
    return section_start, section_end, section_indent


def add_newline(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        result = func(*args, **kwargs)
        if not result.endswith('\n'):
            result += '\n'
        return result

    return decorator


@add_newline
def yaml_add_lines_to_machine_pre(text, add_lines):

    lines = text.splitlines()
    machine_start, machine_stop, machine_indent = get_section(lines, 'machine')

    if machine_start is None:
        for line in add_lines[::-1]:
            lines.insert(0, '    - {}'.format(line))
        lines.insert(0, '  pre:')
        lines.insert(0, 'machine:')
        return '\n'.join(lines)
    pre_start, pre_stop, pre_indent = get_section(lines[machine_start:machine_stop], 'pre', machine_indent)

    if pre_start is None:
        for line in add_lines[::-1]:
            lines.insert(machine_start, '{}  - {}'.format(machine_indent, line))
        lines.insert(machine_start, machine_indent + 'pre:')
        return '\n'.join(lines)

    index = machine_start + pre_start
    for line in add_lines[::-1]:
        lines.insert(index, '{}- {}'.format(pre_indent, line))
    return '\n'.join(lines)
