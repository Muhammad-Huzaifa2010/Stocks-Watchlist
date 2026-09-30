from sqlalchemy.orm import Session

from .models import Stock
from .schemas import StockCreate


def create_stock(db: Session, stock: StockCreate, user_id: int) -> Stock:
    new_stock = Stock(
        symbol=stock.symbol,
        company_name=stock.company_name,
        market=stock.market,
        sector=stock.sector,
        notes=stock.notes,
        user_id=user_id,
    )
    db.add(new_stock)
    db.commit()
    db.refresh(new_stock)
    return new_stock


def get_stocks(db: Session, user_id: int) -> list[Stock]:
    return (
        db.query(Stock)
        .filter(Stock.user_id == user_id)
        .order_by(Stock.id)
        .all()
    )


def get_stock(db: Session, stock_id: int, user_id: int) -> Stock | None:
    return (
        db.query(Stock)
        .filter(Stock.id == stock_id, Stock.user_id == user_id)
        .first()
    )


def update_stock(
    db: Session,
    stock_id: int,
    stock_data: StockCreate,
    user_id: int,
) -> Stock | None:
    stock = get_stock(db, stock_id, user_id)
    if stock is None:
        return None

    stock.symbol = stock_data.symbol
    stock.company_name = stock_data.company_name
    stock.market = stock_data.market
    stock.sector = stock_data.sector
    stock.notes = stock_data.notes
    db.commit()
    db.refresh(stock)
    return stock


def delete_stock(db: Session, stock_id: int, user_id: int) -> Stock | None:
    stock = get_stock(db, stock_id, user_id)
    if stock is None:
        return None

    db.delete(stock)
    db.commit()
    return stock
