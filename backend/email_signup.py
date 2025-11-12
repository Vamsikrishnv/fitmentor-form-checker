# backend/email_signup.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import requests
import os

router = APIRouter()

class SignupRequest(BaseModel):
    email: EmailStr
    name: str

@router.post("/api/signup", tags=["Waitlist"])
async def signup_to_waitlist(data: SignupRequest):
    """
    Add user to EmailOctopus waitlist.
    This endpoint acts as a proxy to avoid CORS issues.
    """

    API_KEY = os.getenv("EMAIL_OCTOPUS_API_KEY")
    LIST_ID = os.getenv("EMAIL_OCTOPUS_LIST_ID")

    if not API_KEY or not LIST_ID:
        raise HTTPException(
            status_code=500,
            detail="Email service configuration missing. Please contact administrator."
        )
    
    try:
        response = requests.post(
            f"https://emailoctopus.com/api/1.6/lists/{LIST_ID}/contacts",
            json={
                "api_key": API_KEY,
                "email_address": data.email,
                "fields": {
                    "FirstName": data.name
                },
                "status": "SUBSCRIBED"
            },
            timeout=10
        )
        
        response_data = response.json()
        
        if response.status_code == 200:
            return {
                "success": True, 
                "message": "Successfully joined the waitlist!"
            }
        elif response.status_code == 409 or (
            response_data.get("error", {}).get("code") == "MEMBER_EXISTS_WITH_EMAIL_ADDRESS"
        ):
            return {
                "success": True,
                "message": "You're already on the list! 🎉"
            }
        else:
            error_msg = response_data.get("error", {}).get("message", "Signup failed")
            raise HTTPException(status_code=400, detail=error_msg)
            
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="Request timed out. Please try again."
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Network error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )
