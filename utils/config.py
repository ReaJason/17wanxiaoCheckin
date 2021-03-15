import os
import json5


def load_config(path):
    if path:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                try:
                    return json5.load(f)
                except Exception as e:
                    raise e.__class__(f'配置文件格式错误，请根据 {e} 检查')
    raise RuntimeError("配置文件未找到!")
