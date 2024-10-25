from tools.log import Log
from time import strftime, localtime, time

class GraphBaseModel:
  def __init__(self,config,train_data,validate_data,test_data) -> None:
    print("GraphBaseModel has been Initialized")
    self.model_config = config
    self.train_data = train_data
    self.validate_data = validate_data
    self.test_data = test_data
    self.model_name = self.model_config['model_name']
    self.topk = self.model_config['topk']
    self.epoch = self.model_config['epoch']
    self.batch_size = self.model_config['batch_size']
    self.learningRate = self.model_config['learningRate']
    self.hyperparameter = self.model_config['hyperparameter']
    self.output = self.model_config['output']
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
      for k, v in self.model_config.config.items():
          print(f'{k}={v}')
          self.log.debug(f'{k}={v}') 
          
  def run(self, load_model=False):
    self.log.info('Initializing Model...')
    self.initializing_log()  
    if load_model:
        self.log.info('Loading Model...')
        self.load_model()
    self.log.info('Training Model...')
    self.train()
    self.log.info('Validating Model...')
    self.validate()
    self.log.info('Testing Model...')
    self.test()
    self.log.info('Saving Model...')
    self.save_model()