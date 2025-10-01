from fastapi import FastAPI
from users.routers import auth_router
from roles.routers import roles_and_permissions_route
from teams.routers import team_route
import uvicorn

app = FastAPI()

app.include_router(auth_router, tags=["Authentication endpoints"])
app.include_router(roles_and_permissions_route, tags=["Role and Permission endpoints"])
app.include_router(team_route, tags=["Teams endpoints"])




if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)