import yaml
from telegram.ext import Updater

def read_configs(path):
    with open(path) as file:
        configs = yaml.load(file, Loader=yaml.Loader)
    return configs


def create_updater(token):
    updater = Updater(token=token, use_context=True)

    return updater