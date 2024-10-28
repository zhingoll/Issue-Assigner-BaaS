from pymongo import MongoClient
import pandas as pd
from pandas import DataFrame
import torch
class MongoLoader:
  def __init__(self,uri:str,db_name:str) -> None:
    self.mongo_client = MongoClient(uri)
    self.db = self.mongo_client[db_name]

  def to_df(self,owner:str,name:str,collection_name:str,filter:list[str]) -> DataFrame:
      query = {"owner": owner, "name": name}
      contents = list(self.db[collection_name].find(query))
      contents_df = pd.DataFrame(contents)
      contents_df = contents_df[filter]
      return contents_df
  


def load_node_csv(path,index_col,encoders=None,cleaners=None,**kwargs):
    df = pd.read_csv(path, index_col=index_col, **kwargs)
    '''
    Refer to the implementation of pytorch-geometric:
    https://pytorch-geometric.readthedocs.io/en/stable/tutorial/load_csv.html
    '''
    node_mapping = {index: i for i, index in enumerate(df.index.unique())}  

    if cleaners is not None:
        for col, cleaner in cleaners.items():
            # 处理缺失值
            df[col] = df[col].fillna('')
            df[col] = df[col].apply(cleaner)
    x_vec = None

    if encoders is not None:
        x_vec = [torch.tensor(encoder(df[col]).toarray(),dtype=torch.float) for col, encoder in encoders.items()]
        x_vec = torch.cat(x_vec, dim=-1)

    return x_vec, node_mapping

def load_edge_csv(path, src_index_col, src_mapping, dst_index_col, dst_mapping,
                  encoders=None, **kwargs):
    '''
    Refer to the implementation of pytorch-geometric:
    https://pytorch-geometric.readthedocs.io/en/stable/tutorial/load_csv.html
    '''
    df = pd.read_csv(path, **kwargs)
    src = [src_mapping[index] for index in df[src_index_col]]
    dst = [dst_mapping[index] for index in df[dst_index_col]]
    edge_index = torch.tensor([src, dst])

    edge_attr = None
    if encoders is not None:
        edge_attrs = [encoder(df[col]) for col, encoder in encoders.items()]
        edge_attr = torch.cat(edge_attrs, dim=-1)

    return edge_index, edge_attr  


