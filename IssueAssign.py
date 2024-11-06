from model.registry import ModelRegistry 
from dataset.issueassigndataset import dataset_to_graph
from data.loader import split_dataset,dataset_to_batch

class IssueAssign:
    def __init__(self, config) -> None:
        self.config = config
        self.train_data,self.validate_data,self.num_users,self.num_issues = self.load_data(self.config['dataset_name'],self.config['batch_size'])
        self.test_data = None
        print("IssueAssign initialization completed.")

    def load_data(self,dataset_name,batch_size):
        data,num_users,num_issues = dataset_to_graph(dataset_name)
        train_data, val_data = split_dataset(data)
        train_loader,val_loader = dataset_to_batch(train_data, val_data,batch_size)

        return train_loader,val_loader,num_users,num_issues


    def run(self, load_model):
        try:
            model_class = ModelRegistry.get_model(self.config['model_name'])
            model = model_class(self.config,self.train_data,self.validate_data,self.test_data,self.num_users,self.num_issues)
            model.run(load_model)
        except Exception as e:
            print(f"Error during model execution: {e}")
            raise
