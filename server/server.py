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

# MongoDB Connection
mongo_client = MongoClient('mongodb://localhost:27017/')
db = mongo_client['GFI-TEST1']
issue_assign_collection = db['issue_assign']
feedback_collection = db['feedback']
developer_avg_response = db['developer_metrics']

# 数据模型定义
class IssueRequest(BaseModel):
    owner: str
    name: str
    number: int

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
    model: str

@app.post("/get_issue_resolvers", response_model=IssueAssignResponse)
async def get_issue_resolvers(request: IssueRequest):
    # 查找该issue对应的推荐结果
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
    # 检查feedback值是否合法
    if request.feedback not in ['thumbs_up', 'thumbs_down']:
        raise HTTPException(status_code=400, detail="Invalid feedback value.")

    feedback_data = {
        "user": request.user,
        "feedback": request.feedback,
        "owner": request.owner,
        "name": request.name,
        "number": request.number,
        "model": request.model,
        "timestamp": datetime.datetime.utcnow()
    }

    try:
        feedback_collection.insert_one(feedback_data)
    except Exception as e:
        print(f"Error inserting feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to save feedback.")

    return {"message": "Feedback submitted successfully."}


@app.post("/get_developer_stats")
async def get_developer_stats(data: dict):
    owner = data.get("owner")
    name = data.get("name")
    developers = data.get("developers", [])

    if not owner or not name or not developers:
        raise HTTPException(status_code=400, detail="Missing parameters")

    docs = list(developer_avg_response.find({
        "owner": owner,
        "name": name,
        "developer": {"$in": developers}
    }, {"_id":0, "owner":0, "name":0, "update_time":0}))

    found_devs = {d['developer']: d for d in docs}

    # 对没有记录的开发者用0填充（不返回avg_response_time）
    for dev in developers:
        if dev not in found_devs:
            found_devs[dev] = {
                "developer": dev,
                "avg_activity": 0,
                "community_openrank": 0,
                "global_openrank": 0
            }
        else:
            # 移除avg_response_time字段（如果有的话）
            found_devs[dev].pop("avg_response_time", None)

    result = [found_devs[dev] for dev in developers]
    return result
