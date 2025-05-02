from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv
import google.generativeai as genai
from utils import setup_openai, process_guided_questionnaire, process_direct_question
import jwt
from datetime import datetime, timedelta
import requests

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Project Management Chatbot API",
    description="API for the Intelligent Projects Assistant Chatbot",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize Gemini API
setup_openai()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Pydantic models for request/response
class ChatMessage(BaseModel):
    role: str
    content: str

class DirectQuestionRequest(BaseModel):
    question: str
    project_type: str = "pm"
    chat_history: Optional[List[ChatMessage]] = None

class GuidedQuestionnaireRequest(BaseModel):
    responses: Dict[str, str]
    project_type: str = "pm"

class APIResponse(BaseModel):
    response: str

class IntegrationRequest(BaseModel):
    project_id: str
    project_data: Dict[str, Any]
    integration_type: str

class IntegrationResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None

class AuthRequest(BaseModel):
    client_id: str
    client_secret: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str

# Authentication functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def verify_token(token: str = Header(...)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Authentication endpoint
@app.post("/api/auth", response_model=AuthResponse)
async def authenticate(request: AuthRequest):
    # In a real application, verify client_id and client_secret against a database
    if request.client_id == os.getenv("CLIENT_ID") and request.client_secret == os.getenv("CLIENT_SECRET"):
        access_token = create_access_token(data={"sub": request.client_id})
        return AuthResponse(access_token=access_token, token_type="bearer")
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Existing endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to the Project Management Chatbot API"}

@app.post("/api/direct-question", response_model=APIResponse)
async def ask_direct_question(request: DirectQuestionRequest, token: dict = Depends(verify_token)):
    """
    Process a direct question from the user
    """
    try:
        response = process_direct_question(
            question=request.question,
            chat_history=request.chat_history,
            project_type=request.project_type
        )
        return APIResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/guided-questionnaire", response_model=APIResponse)
async def process_questionnaire(request: GuidedQuestionnaireRequest, token: dict = Depends(verify_token)):
    """
    Process responses from the guided questionnaire
    """
    try:
        response = process_guided_questionnaire(
            responses=request.responses,
            project_type=request.project_type
        )
        return APIResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# New integration endpoints
@app.post("/api/integrate/project", response_model=IntegrationResponse)
async def integrate_project(request: IntegrationRequest, token: dict = Depends(verify_token)):
    """
    Integrate with an external project management system
    """
    try:
        # Process project data based on integration type
        if request.integration_type == "project_management":
            # Example: Process project management data
            processed_data = {
                "project_id": request.project_id,
                "status": "integrated",
                "details": request.project_data
            }
            return IntegrationResponse(
                status="success",
                message="Project successfully integrated",
                data=processed_data
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported integration type")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/integrate/status/{project_id}")
async def get_integration_status(project_id: str, token: dict = Depends(verify_token)):
    """
    Get the status of a project integration
    """
    try:
        # In a real application, this would check the actual integration status
        return {
            "project_id": project_id,
            "status": "active",
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/integrate/sync")
async def sync_projects(token: dict = Depends(verify_token)):
    """
    Synchronize project data with external systems
    """
    try:
        # In a real application, this would sync data with external systems
        return {
            "status": "success",
            "message": "Projects synchronized successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 