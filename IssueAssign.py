from model.registry import ModelRegistry 

class IssueAssign:
    def __init__(self, config) -> None:
        self.config = config
        print("IssueAssign initialization completed.")

    def run(self,load_model,hetero):
        try:
            model_class = ModelRegistry.get_model(self.config['model_name'])
            model = model_class(self.config)
            model.run(load_model,hetero)
        except Exception as e:
            print(f"Error during model execution: {e}")
            raise
