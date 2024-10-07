from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 设置允许的来源（CORS）
origins = [
    "*",  # 在开发阶段，可以设置为 "*"，允许所有来源。生产环境应设置为特定的域名。
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB 连接
mongo_client = MongoClient('mongodb://localhost:27017/')
db = mongo_client['GFI-TEST1']
issue_assign_collection = db['issue_assign']

# 请求数据模型
class IssueRequest(BaseModel):
    owner: str
    name: str
    number: int

# 响应数据模型
class IssueAssignResponse(BaseModel):
    owner: str
    name: str
    number: int
    probability: List[float]
    last_updated: str
    assignee: List[str]

@app.post("/get_issue_resolvers", response_model=IssueAssignResponse)
async def get_issue_resolvers(request: IssueRequest):
    # 查询数据库
    result = issue_assign_collection.find_one({
        "owner": request.owner,
        "name": request.name,
        "number": request.number
    })

    if not result:
        raise HTTPException(status_code=404, detail="Issue assignment not found.")

    # 将 ObjectId 转换为字符串
    result['_id'] = str(result['_id'])
    # 将 datetime 转换为字符串
    result['last_updated'] = result['last_updated'].strftime('%Y-%m-%d %H:%M:%S')

    return result
