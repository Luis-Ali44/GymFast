from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, field_validator,Field
from CONFIG.database import get_supabase

router = APIRouter()
supabase = get_supabase()

class LoginData(BaseModel):
    email: EmailStr
    password: str = Field(
        ...,
        min_length = 6,
        error_messages={
            "min_length": "La contraseña debe tener al menos 6 caracteres"
        },


    )

    @field_validator("password")
    def validate_password(cls, v):
        if not v.strip():
            raise ValueError("La contraseña no puede estar vacia")
        return v


@router.post("/login")
def login(Data: LoginData):
    try: 
        response = supabase.auth.sign_in_with_password ({
            "email": Data.email,
            "password": Data.password
        })
        
        return  {
        "access_token": response.session.access_token,
        "user": response.user.email
        }
    except Exception as e: 
        raise HTTPException(status_code= 401, detail=str(e))
    
@router.post("/logout")
def logoutn():
    supabase.auth.sign_out()
    return {"massage": "Sesion cerrada"}