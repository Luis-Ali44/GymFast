from fastapi import FastAPI, HTTPException, Header
from Modules.Auth.auth import router as auth_router
from Modules.Users.users import router as user_router
from Modules.Machines.machines import router as machines_router
from CONFIG.database import get_supabase



app= FastAPI()
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(machines_router, prefix="/machines",tags=["machines"])


@app.get ("/")
def welcome():
    return "Ola papu :v"


@app.get("/gyms")
def get_gyms():
    supabase= get_supabase()
    try:
        response = supabase.table("gyms").select("*").execute()
        return response.data
    except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    

    
@app.get("/gymsrls")
def get_gyms(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    
    try:
        supabase= get_supabase(token)
        response = supabase.table("gyms").select("*").execute()
        return response.data
    except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    