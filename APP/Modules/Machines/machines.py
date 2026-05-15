from fastapi import APIRouter, HTTPException, Header
from CONFIG.database import get_supabase
from pydantic import BaseModel, Field
from uuid import UUID

router = APIRouter()

class Machine(BaseModel):
    machine_type_id: UUID
    cantidad: int = Field(..., ge= 0)
    estado: str = Field(..., pattern="^(activo|Descompuesto)$")

class MachineUpdate(BaseModel):
    cantidad: int | None = Field(None, ge=0)
    estado: str | None = None   

class MachineStatus(BaseModel):
    estado: str = Field(..., pattern="^(activo|Descompuesto)$")

class MachineDelet(BaseModel):
    machine_id: str


@router.get("/all")
def get_machines(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    try:
        supabase = get_supabase(token)
        response = supabase.table("gym_machines").select("*, machine_types(nombre, categoria)").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
@router.post("/registrar")
def create_machine(Data: Machine,authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    try:
        supabase = get_supabase(token)
        user = supabase.auth.get_user(token)
        gym_id = user.user.user_metadata["gym_id"]
        
        response = supabase.table("gym_machines").insert({"gym_id":gym_id, "machine_type_id": str(Data.machine_type_id), "cantidad": Data.cantidad,"estado": Data.estado}).execute()
        if response.data:
            return {"message": "Máquina registrada exitosamente"}
        else:
            raise HTTPException(status_code=400, detail="Error al registrar la máquina")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/{machine_id}")
def get_machine(machine_id: str,authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    try:
        supabase = get_supabase(token)
        response = supabase.table("gym_machines").select("*").eq("id", machine_id).execute()
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(status_code=404, detail="Máquina no encontrada")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.put("/{machine_id}")
def update_machine(machine_id: str, Data: MachineUpdate,authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    try:
        supabase = get_supabase(token)
        update_data = {}
        if Data.cantidad is not None:
            update_data["cantidad"] = Data.cantidad
        if Data.estado is not None:
            update_data["estado"] = Data.estado
        if not update_data:
            raise HTTPException(status_code=400, detail="No hay datos para actualizar")
        response = supabase.table("gym_machines").update(update_data).eq("id", machine_id).execute()
        if response.data:
            return {"message": "Máquina actualizada exitosamente"}
        else:
            raise HTTPException(status_code=404, detail="Máquina no encontrada")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.patch("/{machine_id}/status")
def update_status(machine_id: str, Data: MachineStatus, authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    try:
        supabase = get_supabase(token)
        response = supabase.table("gym_machines").update({
            "estado": Data.estado
        }).eq("id", machine_id).execute()
        if response.data:
            return {"message": "Estado actualizado exitosamente"}
        else:
            raise HTTPException(status_code=404, detail="Máquina no encontrada")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.delete ("/{machine_id}")
def eliminar_machine(machine_id: str,  authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    try:
        supabase = get_supabase(token)
        response = supabase.table("gym_machines").delete().eq("id", machine_id).execute()
        if response:
            return {"messege": "maquina eliminada"}
        else: 
            raise  HTTPException(status_code=404, detail="Máquina no encontrada")
    except HTTPException:
        raise 
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    

