COMMA_DELIM = ','
SEMICOLON_DELIM = ';'


def detect_delimiter(file_content):
    first_line = file_content.splitlines()[0]
    if SEMICOLON_DELIM in first_line:
        return SEMICOLON_DELIM
    else:
        return COMMA_DELIM
