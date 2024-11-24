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

# Request data model
class IssueRequest(BaseModel):
    owner: str
    name: str
    number: int

# Response Data Model
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
    model: str  # Feedback on which model

@app.post("/get_issue_resolvers", response_model=IssueAssignResponse)
async def get_issue_resolvers(request: IssueRequest):
    # Query the database to obtain all model recommendation results under the same issue
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
    # Verify if the feedback value is valid
    if request.feedback not in ['thumbs_up', 'thumbs_down']:
        raise HTTPException(status_code=400, detail="Invalid feedback value.")

    # Build the data to be inserted
    feedback_data = {
        "user": request.user,
        "feedback": request.feedback,
        "owner": request.owner,
        "name": request.name,
        "number": request.number,
        "model": request.model,
        "timestamp": datetime.datetime.utcnow()
    }

    # Insert into database
    try:
        result = feedback_collection.insert_one(feedback_data)
    except Exception as e:
        print(f"Error inserting feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to save feedback.")

    return {"message": "Feedback submitted successfully."}
