from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Client, FaasFunction, Tariff
from app.schemas.function import FunctionCreate, FunctionRead

router = APIRouter(prefix="/functions", tags=["functions"])


@router.post("", response_model=FunctionRead, status_code=201)
def create_function(data: FunctionCreate, db: Session = Depends(get_db)):
    if db.get(Client, data.client_id) is None:
        raise HTTPException(404, "Client not found")
    if db.get(Tariff, data.tariff_id) is None:
        raise HTTPException(404, "Tariff not found")

    function = FaasFunction(**data.model_dump())
    db.add(function)
    db.commit()
    db.refresh(function)
    return function


@router.get("", response_model=list[FunctionRead])
def list_functions(client_id: int | None = None, db: Session = Depends(get_db)):
    query = select(FaasFunction).order_by(FaasFunction.id)
    if client_id is not None:
        query = query.where(FaasFunction.client_id == client_id)
    return db.scalars(query).all()
