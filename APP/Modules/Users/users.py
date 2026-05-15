from fastapi import APIRouter, HTTPException, Header
from CONFIG.database import  get_supabase
from pydantic import BaseModel, EmailStr, field_validator,Field, model_validator
from uuid import UUID


router = APIRouter()

class User(BaseModel):
    email: EmailStr
    password: str = Field(
        ...,
        min_length = 6,
    )
    confirmar_password: str = Field(
        ...,
        min_length = 6
    )
    full_name:str = Field(..., min_length=2, max_length=50)
    phone_number: str = Field(None, min_length=10, max_length=15)
    role_id: UUID
    


    @field_validator("password")
    def validate_password(cls, v):
        if not v.strip():
            raise ValueError("La contraseña no puede estar vacia")
        return v
    

    @model_validator(mode="after")
    def password_coincides(self):
        if self.password != self.confirmar_password:
            raise ValueError("Las contraseñas no coinciden")
        return self
    
class UserUpdate(BaseModel):
    full_name: str = Field(None, min_length=2, max_length=50)
    phone: str = Field(None, min_length=10, max_length=15)
    

class UserStatus(BaseModel):
    is_active: bool


@router.post("/registrar")
def registrar_usuarios(Data: User, authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    try:
        supabase = get_supabase(token)
        
        admin = supabase.auth.get_user(token)
        gym_id = admin.user.user_metadata["gym_id"]
        
        rol = supabase.table("roles").select("name").eq("id", str(Data.role_id)).execute()
        role_name = rol.data[0]["name"]
        
        response = supabase.auth.sign_up({
            "email": Data.email,
            "password": Data.password,
            "options": {
                "data": {
                    "gym_id": gym_id,
                    "role": role_name
                }
            }
        })
        if response.user:
            supabase.table("users").insert({
                "id": response.user.id,
                "full_name": Data.full_name,
                "phone": Data.phone_number,
                "gym_id": gym_id,
                "role_id": str(Data.role_id),
                "email": Data.email
            }).execute()
            return {"message": "Usuario registrado exitosamente"}
        else:
            raise HTTPException(status_code=400, detail="Error al registrar el usuario")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    


@router.get("/all")
def get_all(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    try: 
        supabase = get_supabase(token)
        response = supabase.table("users").select("*").execute()
        return response.data
    except HTTPException:
        raise
    
    except Exception as e: 
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}")
def get_pofile(user_id: str, authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    try:
        supabase = get_supabase(token)
        response = supabase.table("users").select("*").eq("id", user_id).execute()
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.put("/{user_id}")
def update_user(user_id: str, Data:UserUpdate, authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    try:
        supabase = get_supabase(token)
        update_data= {}
        if Data.full_name is not None:
            update_data["full_name"] = Data.full_name
        if Data.phone is not None:
            update_data["phone"] = Data.phone
        if not update_data:
            raise HTTPException(status_code=400, detail="No se proporcionaron datos para actualizar")
        response = supabase.table("users").update(update_data).eq("id", user_id).execute()
        if response.data:
            return {"message": "Usuario actualizado exitosamente"}
        else:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.patch("/{user_id}/status")
def patch_user(user_id: str, Data:UserStatus,authorization: str = Header(...)): 
    token = authorization.replace("Bearer ", "")
    try:
        supabase = get_supabase(token)
        response = supabase.table("users").update({"is_active": Data.is_active}).eq("id", user_id).execute()
        if response.data:
            return {"message": "Estado actualizado exitosamente"}
        else:
            raise HTTPException(status_code=404, detail="Usuarios no encontrado")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))