from typing import Optional

from pydantic import BaseModel


class Address(BaseModel):
    street: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone_number: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    type: Optional[str] = None
    is_client: Optional[bool] = None
    primary_address: Optional[Address] = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(ContactBase):
    pass


class ContactResponse(ContactBase):
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
