from pymongo import MongoClient
import pandas as pd
from pandas import DataFrame

class MongoLoader:
  def __init__(self,uri:str,db_name:str) -> None:
    self.mongo_client = MongoClient(uri)
    self.db = self.mongo_client[db_name]

  def to_df(self,query:dict,collection_name:str,filter:list[str]) -> DataFrame:
      contents = list(self.db[collection_name].find(query))
      contents_df = pd.DataFrame(contents)
      contents_df = contents_df[filter]
      return contents_df

  


