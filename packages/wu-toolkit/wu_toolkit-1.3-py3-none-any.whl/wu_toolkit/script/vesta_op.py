from wu_toolkit.app_config import config_dir
from pathlib import Path
import json
import os


def vesta_(file_path):
    # 获取变量
    config_file = config_dir / "config.json"
    if not config_file.exists():
        print("Error: config file does not exist.")
        return

    with config_file.open("r", encoding="utf-8") as f:
        config_data = json.load(f)

    # 使用变量
    VESTA_path = config_data.get(
        "VESTA_path",
        "VESTA_path not found, please set 'wtk config -a VESTA_path /path/to/VESTA'",
    )
    os.system(f"{VESTA_path} {file_path}")