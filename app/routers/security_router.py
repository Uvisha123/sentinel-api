from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.blocked_ip import BlockedIP

router = APIRouter(prefix="/security", tags=["Security"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/block-ip")
def block_ip(
    ip_address: str,
    reason: str,
    db: Session = Depends(get_db),
    x_api_key: str = Header(..., alias="X-API-Key"),
):

    existing = db.query(BlockedIP).filter(BlockedIP.ip_address == ip_address).first()

    if existing:
        raise HTTPException(status_code=400, detail="IP already blocked")

    blocked = BlockedIP(
        ip_address=ip_address,
        reason=reason
    )

    db.add(blocked)
    db.commit()

    return {"message": "IP blocked successfully"}

@router.get("/blocked-ips")
def get_blocked_ips(
    db: Session = Depends(get_db),
    x_api_key: str = Header(..., alias="X-API-Key"),
):

    ips = db.query(BlockedIP).all()

    return ips

@router.delete("/unblock-ip/{ip_id}")
def unblock_ip(
    ip_id: int,
    db: Session = Depends(get_db),
    x_api_key: str = Header(..., alias="X-API-Key"),
):

    ip = db.query(BlockedIP).filter(BlockedIP.id == ip_id).first()

    if not ip:
        raise HTTPException(status_code=404, detail="IP not found")

    db.delete(ip)
    db.commit()

    return {"message": "IP unblocked"}