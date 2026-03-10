from fastapi import FastAPI
from enum import Enum
from user_service import create_user, login, get_users, delete_user, change_password

app = FastAPI(title="User Management Backend")

class UserRole(str, Enum):
    admin = "admin"
    manager = "manager"
    staff = "staff"  

@app.get("/")
def test():
    return {"status": "backend running"}

# http://127.0.0.1:8000/docs   can see all api

# ---------------- login ----------------
@app.post("/login")
def user_login(username: str, password: str):
    return login(username, password)

# ---------------- create user ----------------
@app.post("/create_user")
def user_create(username: str, password: str, role: UserRole = UserRole.staff):
    return create_user(username, password, role.value)

# ---------------- get all user ----------------
@app.get("/users")
def list_users():
    return get_users()

# ---------------- delete user ----------------
@app.delete("/delete_user")
def remove_user(requester_username: str, requester_password: str, target_username: str):
    return delete_user(requester_username, requester_password, target_username)

# ---------------- change password ----------------
@app.post("/change_password")
def modify_password(requester_username: str, requester_password: str, target_username: str, new_password: str):
    return change_password(requester_username, requester_password, target_username, new_password)