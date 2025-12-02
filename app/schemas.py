from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, HttpUrl, confloat, constr, field_validator, ConfigDict


# -------- Usuarios --------

class UserCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    password: constr(min_length=8, max_length=128)

    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        has_letter = any(ch.isalpha() for ch in value)
        has_digit = any(ch.isdigit() for ch in value)
        has_special = any(not ch.isalnum() for ch in value)
        if not (has_letter and has_digit and has_special):
            raise ValueError("La contrasena debe incluir letras, numeros y un caracter especial.")
        return value


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str


# -------- Auth / Tokens --------

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


# -------- Propuestas --------

class ProposalStatus(str, Enum):
    ENVIADA = "Enviada"
    EN_NEGOCIACION = "En negociacion"
    ACEPTADA = "Aceptada"
    RECHAZADA = "Rechazada"
    BORRADOR = "Borrador"


class ProposalBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    client_name: constr(strip_whitespace=True, min_length=1, max_length=120)
    platform: constr(strip_whitespace=True, min_length=1, max_length=80)
    project_title: constr(strip_whitespace=True, min_length=1, max_length=180)
    project_link: Optional[HttpUrl] = None
    amount: confloat(ge=0)
    currency: constr(strip_whitespace=True, min_length=1, max_length=10) = "USD"
    status: ProposalStatus = ProposalStatus.ENVIADA
    notes: Optional[constr(strip_whitespace=True, max_length=500)] = None


class ProposalCreate(ProposalBase):
    pass


class ProposalUpdate(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    client_name: Optional[constr(strip_whitespace=True, min_length=1, max_length=120)] = None
    platform: Optional[constr(strip_whitespace=True, min_length=1, max_length=80)] = None
    project_title: Optional[constr(strip_whitespace=True, min_length=1, max_length=180)] = None
    project_link: Optional[HttpUrl] = None
    amount: Optional[confloat(ge=0)] = None
    currency: Optional[constr(strip_whitespace=True, min_length=1, max_length=10)] = None
    status: Optional[ProposalStatus] = None
    notes: Optional[constr(strip_whitespace=True, max_length=500)] = None


class ProposalOut(ProposalBase):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: int
    owner_id: int
