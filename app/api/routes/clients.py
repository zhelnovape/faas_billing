from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Client
from app.schemas.client import ClientCreate, ClientRead

router = APIRouter(prefix="/clients", tags=["clients"])


@router.post("", response_model=ClientRead, status_code=201)
def create_client(data: ClientCreate, db: Session = Depends(get_db)):
    client = Client(name=data.name)
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.get("", response_model=list[ClientRead])
def list_clients(db: Session = Depends(get_db)):
    return db.scalars(select(Client).order_by(Client.id)).all()
