from tools.file import FileIO
from model.registry import ModelRegistry 

class IssueAssign:
    def __init__(self, config) -> None:
        self.config = config
        self.train_data = FileIO.read_interact_file(config['train_data'])
        self.test_data = FileIO.read_interact_file(config['test_data'])
        print("IssueAssign initialization completed.")

    def run(self, load_model):
        try:
            model_class = ModelRegistry.get_model(self.config['model_name'])
            model = model_class(self.config, self.train_data, self.test_data)
            model.run(load_model)
        except Exception as e:
            print(f"Error during model execution: {e}")
            raise
