import json

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def load_jsonl(path):
    with open(path, 'r') as f:
        return [json.loads(line) for line in f]


def save_jsonl(data, path):
    with open(path, 'w') as f:
        for d in data:
            f.write(json.dumps(d) + '\n')
    return