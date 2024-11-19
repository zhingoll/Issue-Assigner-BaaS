from tools.log import Log
from time import strftime, localtime, time
from data.mongo import MyMongoLoader
from dataset.issueassigndataset import dataset_to_graph
from data.loader import split_dataset,dataset_to_batch
class GraphBaseModel:
  def __init__(self,config) -> None:
    print("GraphBaseModel has been Initialized")
    self.config = config
    self.model_name = self.config['model_name']
    self.topk = self.config['topk']
    self.epoch = int(self.config['epoch'])
    self.batch_size = int(self.config['batch_size'])
    self.learningRate = float(self.config['learningRate'])
    self.hyperparameter = self.config['hyperparameter']
    self.output = self.config['output']
    self.owner = self.config['owner']
    self.name = self.config['name']
    current_time = strftime("%Y-%m-%d-%H-%M-%S", localtime(time()))
    self.log = Log(self.model_name, self.model_name + '_' + current_time)
        
  def train(self):
    pass

  def validate(self):
    pass



  def test(self):
    pass

  def save_model(self):
    pass

  def load_model(self):
    pass

  def initializing_log(self):
      # 日志文件中记录，控制台显示
      print('### Model Configuration ###')
      self.log.debug('### Model Configuration ###')     
      for k, v in self.config.config.items():
          print(f'{k}={v}')
          self.log.debug(f'{k}={v}') 
          
  def connect_mongo(self):
        db = self.config['db']
        uri = self.config['uri']
        mongo_client = MyMongoLoader(uri,db)
        self.issue_assign_collection = mongo_client.db['issue_assign']

  def load_data(self,hetero):
      self.data,self.user_mapping,self.issue_mapping = dataset_to_graph(self.config['dataset_name'],hetero)
      print("self.data",self.data) 
      self.num_users = self.data.num_nodes
      self.num_issues = self.data.num_nodes
      self.train_data,self.val_data = split_dataset(self.data,hetero)
      self.train_loader,self.val_loader,self.test_loader = dataset_to_batch(self.data,self.train_data,self.val_data,self.config['batch_size'],hetero)

  def run(self, load_model=False,hetero=True,test_model=False):
    self.log.info('Initializing Model...')
    self.initializing_log()

    if load_model:
            self.log.info('Loading Model...')
            self.load_model()

    self.log.info(f"Loading {self.config['dataset_name']} Data...")
    self.load_data(hetero)

    self.log.info('Training Model...')
    self.train()

    self.log.info('Validating Model...')
    self.validate()

    test_model = input('Do you want to test model?:')
    if test_model.lower() == "test":
        self.log.info('Testing Model...')
        self.log.info('Connecting MongoDB...')
        self.connect_mongo()
        self.test()

    self.log.info('Saving Model...')
    self.save_model()