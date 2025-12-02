from typing import List

from sqlalchemy import case, func

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from .auth import get_current_user

router = APIRouter(
    prefix="/proposals",
    tags=["proposals"],
)


@router.post("/", response_model=schemas.ProposalOut)
def create_proposal(
    proposal_in: schemas.ProposalCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    payload = proposal_in.model_dump(mode="json")
    proposal = models.Proposal(
        **payload,
        owner_id=current_user.id,
    )
    db.add(proposal)
    db.commit()
    return proposal


@router.get("/", response_model=List[schemas.ProposalOut])
def list_proposals(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    proposals = (
        db.query(models.Proposal)
        .filter(models.Proposal.owner_id == current_user.id)
        .order_by(models.Proposal.created_at.desc())
        .all()
    )
    return proposals


@router.get("/{proposal_id}", response_model=schemas.ProposalOut)
def get_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    proposal = (
        db.query(models.Proposal)
        .filter(
            models.Proposal.id == proposal_id,
            models.Proposal.owner_id == current_user.id,
        )
        .first()
    )
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propuesta no encontrada.",
        )
    return proposal


@router.put("/{proposal_id}", response_model=schemas.ProposalOut)
def update_proposal(
    proposal_id: int,
    proposal_in: schemas.ProposalUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    proposal = (
        db.query(models.Proposal)
        .filter(
            models.Proposal.id == proposal_id,
            models.Proposal.owner_id == current_user.id,
        )
        .first()
    )
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propuesta no encontrada.",
        )

    update_data = proposal_in.model_dump(exclude_unset=True, mode="json")
    for field, value in update_data.items():
        setattr(proposal, field, value)

    db.commit()
    return proposal


@router.delete("/{proposal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    proposal = (
        db.query(models.Proposal)
        .filter(
            models.Proposal.id == proposal_id,
            models.Proposal.owner_id == current_user.id,
        )
        .first()
    )
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propuesta no encontrada.",
        )

    db.delete(proposal)
    db.commit()
    return None


@router.get("/stats/basic", response_model=dict)
def basic_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    total, accepted, rejected = (
        db.query(
            func.count(models.Proposal.id),
            func.coalesce(
                func.sum(
                    case(
                        (models.Proposal.status == schemas.ProposalStatus.ACEPTADA.value, 1),
                        else_=0,
                    )
                ),
                0,
            ),
            func.coalesce(
                func.sum(
                    case(
                        (models.Proposal.status == schemas.ProposalStatus.RECHAZADA.value, 1),
                        else_=0,
                    )
                ),
                0,
            ),
        )
        .filter(models.Proposal.owner_id == current_user.id)
        .one()
    )

    pending = max(total - accepted - rejected, 0)
    conversion = (accepted / total * 100.0) if total else 0.0

    return {
        "total": total,
        "accepted": accepted,
        "rejected": rejected,
        "pending": pending,
        "conversion_percent": round(conversion, 2),
    }
