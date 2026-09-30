from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..crud import create_stock, delete_stock, get_stock, get_stocks, update_stock
from ..database import get_db
from ..models import User
from ..schemas import StockCreate, StockResponse
from ..security import get_current_user


router = APIRouter()

DUPLICATE_STOCK_DETAIL = "Stock already exists in your watchlist"


@router.post("/stocks", response_model=StockResponse, status_code=201)
def add_stock(
    stock: StockCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_stock(db, stock, current_user.id)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=DUPLICATE_STOCK_DETAIL)


@router.get("/stocks", response_model=list[StockResponse])
def get_all_stocks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_stocks(db, current_user.id)


@router.get("/stocks/{stock_id}", response_model=StockResponse)
def get_single_stock(
    stock_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stock = get_stock(db, stock_id, current_user.id)
    if stock is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock


@router.put("/stocks/{stock_id}", response_model=StockResponse)
def update_stocks(
    stock_id: int,
    stock_data: StockCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        stock = update_stock(db, stock_id, stock_data, current_user.id)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=DUPLICATE_STOCK_DETAIL)

    if stock is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock


@router.delete("/stocks/{stock_id}", response_model=StockResponse)
def delete_stocks(
    stock_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stock = delete_stock(db, stock_id, current_user.id)
    if stock is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock
