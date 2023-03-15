import json
def _load_json(file:str):
    with open(file) as file:
        return json.load(file)

def get_schema(file:str):
    js = _load_json(file)
    return dict(js)
