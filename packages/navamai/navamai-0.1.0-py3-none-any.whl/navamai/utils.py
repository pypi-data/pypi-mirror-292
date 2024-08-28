import click
import importlib.resources
import shutil
from pathlib import Path
import yaml
import os
import re

CONFIG_FILE = "navamai.yml"

def load_config(section=None):
    if not os.path.exists(CONFIG_FILE):
        return {} if section is None else {}
    
    with open(CONFIG_FILE, "r") as f:
        config = yaml.safe_load(f)
    
    if section:
        return config.get(section, {})
    return config

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(config, f)

def edit_config(keys, value):
    config = load_config()
    current = config
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value
    save_config(config)

def get_model_mapping():
    config = load_config()
    return config.get("model-mapping", {})

def resolve_model(model):
    model_mapping = get_model_mapping()
    return model_mapping.get(model, model)

