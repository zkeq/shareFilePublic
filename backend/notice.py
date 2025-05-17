import json
import os
from fastapi import HTTPException

NOTICE_DIR = "notice"

# Create notice directory if it doesn't exist
if not os.path.exists(NOTICE_DIR):
    os.makedirs(NOTICE_DIR)

def save_notice(vcode: str, content: str, password: str) -> dict:
    """Save a new notice for a video"""
    file_path = os.path.join(NOTICE_DIR, f"{vcode}.json")
    
    # Check if notice already exists
    if os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="Notice already exists for this video")
    
    notice_data = {
        "content": content,
        "password": password,
        "vcode": vcode
    }
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(notice_data, f, ensure_ascii=False, indent=4)
    
    return {"message": "Notice created successfully"}

def update_notice(vcode: str, content: str, password: str) -> dict:
    """Update an existing notice"""
    file_path = os.path.join(NOTICE_DIR, f"{vcode}.json")
    
    # Check if notice exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Notice not found")
    
    # Read existing notice
    with open(file_path, "r", encoding="utf-8") as f:
        existing_notice = json.load(f)
    
    # Verify password
    if existing_notice["password"] != password:
        raise HTTPException(status_code=403, detail="Invalid password")
    
    # Update content
    existing_notice["content"] = content
    
    # Save updated notice
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(existing_notice, f, ensure_ascii=False, indent=4)
    
    return {"message": "Notice updated successfully"}

def get_notice(vcode: str) -> dict:
    """Get notice for a video"""
    file_path = os.path.join(NOTICE_DIR, f"{vcode}.json")
    
    # Check if notice exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Notice not found")
    
    # Read notice
    with open(file_path, "r", encoding="utf-8") as f:
        notice_data = json.load(f)
    
    # Return notice without password
    return {
        "content": notice_data["content"],
        "vcode": notice_data["vcode"]
    } 