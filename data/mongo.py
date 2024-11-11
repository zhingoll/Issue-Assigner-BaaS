from pymongo import MongoClient
import pandas as pd
from pandas import DataFrame


class MyMongoLoader:
  def __init__(self,uri:str,db_name:str) -> None:
    self.mongo_client = MongoClient(uri)
    self.db = self.mongo_client[db_name]

  def to_df(self,owner:str,name:str,collection_name:str,filter) -> DataFrame:
      query = {"owner": owner, "name": name}
      contents = list(self.db[collection_name].find(query))
      contents_df = pd.DataFrame(contents)
      contents_df = contents_df[filter]
      return contents_df
  






# def load_issue_content(owner, name,db,collection_name):
#     # 加载Issue内容数据
#     query = {"owner": owner, "name": name}
#     issue_contents = list(db[collection_name].find(query))
#     issue_contents_df = pd.DataFrame(issue_contents)
#     issue_contents_df = issue_contents_df[['number', 'title', 'body']]
#     return issue_contents_df


# # 从 MongoDB 加载已解决的 Issue 数据
# def load_resolved_issues(owner, name,db,collection_name):
#     query = {"owner": owner, "name": name}
#     resolved_issues = list(db[collection_name].find(query))
#     resolved_issues_df = pd.DataFrame(resolved_issues)
#     resolved_issues_df = resolved_issues_df[['number', 'resolver']]
#     return resolved_issues_df


# def load_open_issues(owner, name,db,collection_name):
#     query = {"owner": owner, "name": name, "state": "open"}
#     open_issues = list(db[collection_name].find(query))
#     open_issues_df = pd.DataFrame(open_issues)
#     open_issues_df = open_issues_df[['number', 'title', 'body']]
#     return open_issues_df