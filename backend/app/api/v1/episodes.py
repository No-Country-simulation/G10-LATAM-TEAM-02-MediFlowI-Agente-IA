
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/episodes", tags=["Episodios Clínicos"])

class EpisodeCreate(BaseModel):
    patient_id: str
    motivo_consulta: str
    canal_origen: str

class EpisodeResponse(EpisodeCreate):
    episode_id: str
    estado: str = "activo"

@router.post("/", response_model=EpisodeResponse, status_code=status.HTTP_201_CREATED)
def create_episode(episode: EpisodeCreate):
    return EpisodeResponse(
        episode_id="EP-001",
        patient_id=episode.patient_id,
        motivo_consulta=episode.motivo_consulta,
        canal_origen=episode.canal_origen,
        estado="activo"
    )

@router.get("/", response_model=list[EpisodeResponse])
def list_episodes():
    return []

@router.get("/{episode_id}", response_model=EpisodeResponse)
def get_episode(episode_id: str):
    if episode_id == "not-found":
        raise HTTPException(status_code=404, detail="Episodio no encontrado")
    return EpisodeResponse(
        episode_id=episode_id,
        patient_id="PAT-001",
        motivo_consulta="Control general",
        canal_origen="Consulta_Externa",
        estado="activo"
    )