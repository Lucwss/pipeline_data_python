from datetime import datetime

from sqlmodel import SQLModel, Field


class ProductBase(SQLModel):
    produto: str
    categoria_do_produto: str
    preço: float
    frete: float
    data_da_compra: datetime
    vendedor: str
    local_da_compra: str
    avaliação_da_compra: int
    tipo_de_pagamento: str
    quantidade_de_parcelas: int = Field(default=None, nullable=True)
    latitude: int
    longitude: int


class Product(ProductBase, table=True):
    id: int = Field(default=None, nullable=False, primary_key=True)
