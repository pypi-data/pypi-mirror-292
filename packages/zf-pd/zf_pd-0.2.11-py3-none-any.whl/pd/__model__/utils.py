def parse_str_list_int(ctx, param, value) -> list[int]:
    if not value:
        return []
    delim: str | None = None
    if ',' in value:
        delim = ','
    elif 'x' in value:
        delim = 'x'
    elif ' ' in value:
        delim = ' '

    if not delim:
        return [int(value)]

    return [int(s) for s in value.split(delim)]