from typing import List, Optional

from pydantic import BaseModel, EmailStr


class EmailAddress(BaseModel):
    name: Optional[str] = "Work"
    address: EmailStr
    default_email: bool = True


class PhoneNumber(BaseModel):
    name: Optional[str] = "Work"
    number: str
    default_number: bool = True


class Address(BaseModel):
    name: Optional[str] = "Work"
    street: Optional[str]
    city: str
    province: Optional[str]
    postal_code: Optional[str]
    country: Optional[str]


class CustomFieldValue(BaseModel):
    value: str
    custom_field: dict  # {'id': int}


class ContactCreate(BaseModel):
    first_name: str
    last_name: str
    email_addresses: List[EmailAddress]
    phone_numbers: List[PhoneNumber]
    is_client: bool = False
    type: str = "Person"
    tags: Optional[List[str]] = ["Lead"]
    addresses: Optional[List[Address]]
    custom_field_values: Optional[List[CustomFieldValue]]
