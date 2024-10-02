import token
from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from auth import authenticate_user, create_access_token, get_current_user, fake_users_db, ACCESS_TOKEN_EXPIRE_MINUTES
from models import Token
from datetime import timedelta
import os
import detection
import asyncio

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    # print(f"Generated Token: {access_token}")  # Debugging line
    return {"token": access_token, "token_type": "bearer"}

@app.post("/verify-token")
async def verify_token(token: str = Depends(oauth2_scheme)):
    user = await get_current_user(token)
    return {"username": user["username"]}

@app.post("/upload")
async def upload_image(file: UploadFile = File(...), user: str = Depends(get_current_user)):
    try:
        content = await file.read()
        file_path = f'uploads/frame.jpg'
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Call detection asynchronously without blocking the upload
        asyncio.create_task(detection.detect_people(file_path))

        return {"message": "Image uploaded successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to upload image")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
