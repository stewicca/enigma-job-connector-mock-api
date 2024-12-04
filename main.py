from fastapi import FastAPI, HTTPException, Depends, Header, Request
import json
from fastapi.responses import JSONResponse
from typing import Optional, Union

app = FastAPI()

# Load mock data from JSON file
def load_mock_users():
    with open("mock_users.json", "r") as file:
        return json.load(file)

def save_mock_users(data):
    with open("mock_users.json", "w") as file:
        json.dump(data, file, indent=4)

# Utility function for consistent responses
def generate_response(
    status: int,
    message: str,
    data: Optional[Union[dict, list]] = None,
    paging: Optional[dict] = None,
):
    return JSONResponse(
        status_code=status,
        content={
            "status": status,
            "message": message,
            "data": data,
            "paging": paging,
        },
    )

# Dependency to check Authorization
def check_token(authorization: str = Header(...)):
    if authorization != "Bearer mock_token":
        return generate_response(401, "Unauthorized")
    return True

# Endpoints
@app.post("/api/user", dependencies=[Depends(check_token)])
async def create_user(user: dict):
    mock_users = load_mock_users()
    mock_users.append(user)
    save_mock_users(mock_users)
    return generate_response(201, "Successfully create user")

@app.put("/api/user", dependencies=[Depends(check_token)])
async def update_user(user: dict):
    mock_users = load_mock_users()
    for u in mock_users:
        if u["id"] == user["id"]:
            u.update({k: v for k, v in user.items() if v is not None})
            save_mock_users(mock_users)
            return generate_response(200, "Successfully update user")
    return generate_response(404, "User not found")

@app.get("/api/user", dependencies=[Depends(check_token)])
async def get_user():
    mock_users = load_mock_users()
    return generate_response(
        200,
        "Successfully fetching user",
        data=mock_users,
        paging={
            "page": 1,
            "totalItem": len(mock_users),
            "totalPages": 1,
            "size": len(mock_users),
        },
    )

@app.delete("/api/user/{user_id}", dependencies=[Depends(check_token)])
async def delete_user(user_id: str):
    mock_users = load_mock_users()
    mock_users = [u for u in mock_users if u["id"] != user_id]
    save_mock_users(mock_users)
    return generate_response(200, "Successfully delete user")

@app.post("/api/auth/login")
async def login(request: dict):
    mock_users = load_mock_users()
    for user in mock_users:
        if user["username"] == request["username"] and user["password"] == request["password"]:
            return generate_response(
                200,
                "Successfully Login user",
                data={
                    "id": user["id"],
                    "accessToken": "access_token_value",
                    "refreshToken": "refresh_token_value",
                    "role": user["role"],
                },
            )
    return generate_response(400, "Invalid credential")
