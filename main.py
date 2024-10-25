import os
from IssueAssign import IssueAssign
from model.registry import ModelRegistry
from config.config import ModelConf

def get_model_name(available_models):
    model_name = input("Please enter the model you want to run: ")
    while model_name not in available_models:
        print('Wrong model name!')
        model_name = input("Please enter the model you want to run: ")
    return model_name

def load_configuration(model_name):
    config_path = os.path.join('config', model_name + '.conf')
    if not os.path.exists(config_path):
        print(f"Configuration file {config_path} does not exist.")
        exit(-1)
    return ModelConf(config_path)

def get_load_model_decision():
    load = input('Do you want to load:')
    return load.lower() == "load"

def print_divider(title, width):
    print("\n" + "=" * width)
    print(f"{title.center(width)}")
    print("=" * width)

if __name__ == '__main__':
    available_models = list(ModelRegistry.registry.keys())
    title = "Issue-Assign Tool"
    print_divider(title,88)
    print("The existing model is as follows:")
    print('  '.join(available_models))
    print('='*88)

    model_name = get_model_name(available_models)
    config = load_configuration(model_name)
    load_model = get_load_model_decision()
    model = IssueAssign(config)
    model.run(load_model)
