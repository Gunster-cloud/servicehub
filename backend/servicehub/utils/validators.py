"""
Custom validators for ServiceHub.
"""

from pydantic import BaseModel, field_validator, EmailStr
from typing import Optional
from decimal import Decimal
import re


class ClientValidator(BaseModel):
    """Validator for Client data."""
    
    name: str
    email: EmailStr
    phone: str
    document: str
    type: str
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Nome deve ter pelo menos 3 caracteres')
        return v.strip()
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        # Remove non-digit characters
        clean_phone = re.sub(r'\D', '', v)
        if len(clean_phone) < 10:
            raise ValueError('Telefone inválido')
        return v
    
    @field_validator('document')
    @classmethod
    def validate_document(cls, v):
        # Remove non-digit characters
        clean_doc = re.sub(r'\D', '', v)
        if len(clean_doc) not in [11, 14]:
            raise ValueError('CPF/CNPJ inválido')
        return v
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        if v not in ['individual', 'company']:
            raise ValueError('Tipo deve ser "individual" ou "company"')
        return v


class QuoteValidator(BaseModel):
    """Validator for Quote data."""
    
    title: str
    subtotal: Decimal
    discount: Decimal
    tax: Decimal
    total: Decimal
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v or len(v.strip()) < 5:
            raise ValueError('Título deve ter pelo menos 5 caracteres')
        return v.strip()
    
    @field_validator('subtotal', 'discount', 'tax', 'total')
    @classmethod
    def validate_amounts(cls, v):
        if v < 0:
            raise ValueError('Valores não podem ser negativos')
        return v
    
    @field_validator('total')
    @classmethod
    def validate_total(cls, v, info):
        if 'subtotal' in info.data:
            subtotal = info.data['subtotal']
            discount = info.data.get('discount', 0)
            tax = info.data.get('tax', 0)
            expected_total = subtotal - discount + tax
            if abs(v - expected_total) > 0.01:
                raise ValueError(f'Total deve ser {expected_total}')
        return v


class ServiceValidator(BaseModel):
    """Validator for Service data."""
    
    name: str
    base_price: Decimal
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Nome deve ter pelo menos 3 caracteres')
        return v.strip()
    
    @field_validator('base_price')
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Preço deve ser maior que zero')
        return v


class UserValidator(BaseModel):
    """Validator for User data."""
    
    username: str
    email: EmailStr
    password: Optional[str] = None
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Username deve ter pelo menos 3 caracteres')
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username pode conter apenas letras, números, hífen e underscore')
        return v.strip()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if v and len(v) < 8:
            raise ValueError('Senha deve ter pelo menos 8 caracteres')
        return v

