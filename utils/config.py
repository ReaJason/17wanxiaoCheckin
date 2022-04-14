import os
import json5


def load_config(path):
    if path and os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json5.load(f)
