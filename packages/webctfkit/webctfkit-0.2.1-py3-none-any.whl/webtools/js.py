from jsmin import jsmin

def minify(script: str):
    return jsmin(script.strip())
