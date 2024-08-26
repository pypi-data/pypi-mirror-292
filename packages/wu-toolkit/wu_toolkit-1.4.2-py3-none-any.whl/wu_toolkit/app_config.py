from platformdirs import user_config_dir
from pathlib import Path
import json

# 获取当前用户的配置目录
config_dir = Path(user_config_dir("wu_toolkit"))


# Add, modify, delete, or show variables in the configuration file
# wtk config -a var_name var_value to add
# wtk config -m var_name var_value to modify
# wtk config -d var_name to delete
# wtk config -s to show
def config_(
    action=None,
    var_name=None,
    var_value=None,
):
    config_file = config_dir / "config.json"
    if not config_file.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file.touch()
        try:
            config_file.write_text("{}")
        except Exception as e:
            print(f"Error creating config file: {e}")
            return

    with config_file.open("r", encoding="utf-8") as f:
        config_data = json.load(f)

    def check_var_name_and_value():
        if var_name is None or var_value is None:
            print(
                "Error: When adding or modifying a variable, you need to provide both the variable name and the value."
            )
            return False
        return True

    if action == "a":
        if not check_var_name_and_value():
            return
        config_data[var_name] = var_value
        print(f"Added {var_name} with value {var_value}")
    elif action == "m":
        if not check_var_name_and_value():
            return
        if var_name not in config_data:
            print(f"Error: variable {var_name} does not exist.")
            return
        config_data[var_name] = var_value
        print(f"Modified {var_name} with value {var_value}.")
    elif action == "d":
        if var_name is None:
            print(
                "Error: You need to provide a variable name when deleting a variable."
            )
            return
        if var_name not in config_data:
            print(f"Error: variable {var_name} does not exist.")
            return
        del config_data[var_name]
        print(f"Deleted {var_name}")
    elif action == "s" or action is None:
        print(json.dumps(config_data, indent=4))
    else:
        print("Error: Invalid operation. Please use -a, -m, -d, -s.")
        return

    with config_file.open("w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)
