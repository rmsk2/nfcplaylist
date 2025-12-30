import sys
import os
from nfcplaylistconsts import *
import cli_tools
import json


class ConfigHelper:
    def __init__(self, config_path):
        self._config_path = config_path

    def load(self):
        try:
            with(open(self._config_path, "r") as f):
                all_data = json.load(f)
        except:
            print("Unable to load config file")
            sys.exit(42)

        return all_data

    def save(self, config_data):
        try:
            with(open(self._config_path, "wb") as f):
                f.write(config_data.encode("utf-8"))
        except:
            print("Unable to save config file")
            sys.exit(42)


def assign_cards(config_path, event_insert):
    conf = ConfigHelper(config_path)
    config_data = conf.load()
    
    print("Assign function card ids")
    print("========================")
    print()

    for id in config_data["ids"]:
        sys.stdout.write(f"Place '{id}' card on reader: ")
        sys.stdout.flush()
        new_val = cli_tools.wait_for_card(event_insert)        
        config_data["ids"][id] = new_val
        print(new_val)
    
    print()

    new_config = json.dumps(config_data, indent=4)

    decision = input("Overwrite existing config (yes/no)? ")
    if decision.lower() == "yes":
        conf.save(new_config)
    else:
        print(new_config)


if __name__ == "__main__":
    os.system(CLEAR_COMMAND)
    config_name = "ui_config"

    if len(sys.argv) >= 2:
        config_name = sys.argv[1]
    else:
        print("Loading default config 'ui_config'")
        print("use python func_cards.py <config_name> to specify another config file")
        print()

    cli_tools.main(lambda x: assign_cards(config_name, x))