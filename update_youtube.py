import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def update_broadcast_metadata():
    # Environment variables ကနေ အချက်အလက်များရယူခြင်း
    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")
    broadcast_id = os.environ.get("YOUTUBE_BROADCAST_ID")
    
    next_id = os.environ.get("NEXT_ID")
    
    # work/main.json ကိုဖတ်ပြီး သက်ဆိုင်ရာ ID ရဲ့ Data တွေကို ရှာမည်
    with open("work/main.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    video_item = None
    for item in data:
        if str(item.get("id")) == str(next_id):
            video_item = item
            break
            
    if not video_item:
        print(f"Error: ID {next_id} not found in main.json")
        exit(1)
        
    title = video_item.get("title")
    description = video_item.get("description")
    tags = video_item.get("video_tags", [])
    
    print(f"Updating YouTube Broadcast ID: {broadcast_id}")
    print(f"Title: {title}")

    # Google Credentials တည်ဆောက်ခြင်း
    creds = Credentials(
        None,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        token_uri="https://oauth2.googleapis.com/token"
    )
    
    youtube = build("youtube", "v3", credentials=creds)
    
    # 1. Broadcast Details (Title, Description) ကို Update လုပ်ခြင်း
    update_request = youtube.liveBroadcasts().update(
        part="snippet",
        body={
            "id": broadcast_id,
            "snippet": {
                "title": title,
                "description": description,
                "scheduledStartTime": "2026-01-01T00:00:00Z" # လိုအပ်ပါက ထည့်ရန် (သို့မဟုတ် လက်ရှိအချိန်သုံးရန်)
            }
        }
    )
    update_response = update_request.execute()
    print("Broadcast metadata updated successfully.")
    
    # 2. Tags များကို Video resource ပေါ်တွင် Update လုပ်ခြင်း (Broadcast ID ကိုယ်တိုင်က Video ID လည်း ဖြစ်ပါတယ်)
    try:
        video_update = youtube.videos().update(
            part="snippet",
            body={
                "id": broadcast_id,
                "snippet": {
                    "title": title,
                    "description": description,
                    "categoryId": "24", # Entertainment Category (သင့်တော်သလိုပြောင်းနိုင်သည်)
                    "tags": tags
                }
            }
        )
        video_update.execute()
        print("Video tags updated successfully.")
    except Exception as e:
        print(f"Warning: Could not update video tags: {e}")

    # 3. Thumbnail တင်ခြင်း
    padded_id = f"{int(next_id):05d}"
    thumb_path = f"work/{padded_id}.jpg"
    
    if os.path.exists(thumb_path):
        print(f"Uploading thumbnail: {thumb_path}")
        thumbnail_request = youtube.thumbnails().set(
            videoId=broadcast_id,
            media_body=MediaFileUpload(thumb_path)
        )
        thumbnail_request.execute()
        print("Thumbnail uploaded successfully.")
    else:
        print(f"Warning: Thumbnail file {thumb_path} not found.")

if __name__ == "__main__":
    update_broadcast_metadata()
