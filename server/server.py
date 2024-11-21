from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
import datetime

app = FastAPI()

origins = ["*"]

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
feedback_collection = db['feedback']

# 请求数据模型
class IssueRequest(BaseModel):
    owner: str
    name: str
    number: int

# 响应数据模型
class ModelRecommendation(BaseModel):
    model: str
    assignee: List[str]
    probability: List[float]
    last_updated: str

class IssueAssignResponse(BaseModel):
    owner: str
    name: str
    number: int
    recommendations: List[ModelRecommendation]


class FeedbackRequest(BaseModel):
    user: str
    feedback: str 
    owner: str
    name: str
    number: int
    model: str  # 表示针对哪个模型的反馈

@app.post("/get_issue_resolvers", response_model=IssueAssignResponse)
async def get_issue_resolvers(request: IssueRequest):
    # 查询数据库，获取同一 Issue 下的所有模型推荐结果
    results = issue_assign_collection.find({
        "owner": request.owner,
        "name": request.name,
        "number": request.number
    })

    recommendations = []
    for result in results:
        recommendations.append({
            "model": result.get("model", "unknown"),
            "assignee": result["assignee"],
            "probability": result["probability"],
            "last_updated": result["last_updated"].strftime('%Y-%m-%d %H:%M:%S')
        })

    if not recommendations:
        raise HTTPException(status_code=404, detail="Issue assignments not found.")

    response = {
        "owner": request.owner,
        "name": request.name,
        "number": request.number,
        "recommendations": recommendations
    }

    return response

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
        "model": request.model,
        "timestamp": datetime.datetime.utcnow()
    }

    # 插入到数据库
    try:
        result = feedback_collection.insert_one(feedback_data)
    except Exception as e:
        print(f"Error inserting feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to save feedback.")

    return {"message": "Feedback submitted successfully."}
