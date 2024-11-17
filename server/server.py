from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
import datetime  # 新增

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
feedback_collection = db['feedback']  # 新增，用于存储反馈数据

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

# 新增的反馈请求数据模型
class FeedbackRequest(BaseModel):
    user: str
    feedback: str  # 'thumbs_up' 或 'thumbs_down'
    owner: str
    name: str
    number: int

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

@app.post("/submit_feedback")
async def submit_feedback(request: FeedbackRequest):
    # 验证反馈值是否有效
    if request.feedback not in ['thumbs_up', 'thumbs_down']:
        raise HTTPException(status_code=400, detail="Invalid feedback value.")

    # 构建要插入的数据
    feedback_data = {
        "user": request.user,
        "feedback": request.feedback,
        "owner": request.owner,
        "name": request.name,
        "number": request.number,
        "timestamp": datetime.datetime.utcnow()
    }

    # 插入到数据库
    try:
        result = feedback_collection.insert_one(feedback_data)
    except Exception as e:
        print(f"Error inserting feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to save feedback.")

    return {"message": "Feedback submitted successfully."}
