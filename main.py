import asyncio
import pandas as pd
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from models.models import SQLModel, Product
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional
from httpx import AsyncClient, Response
from pymongo.results import InsertOneResult, DeleteResult, InsertManyResult, UpdateResult

client = AsyncIOMotorClient("mongodb://admin123:admin123@172.22.88.91:27017/")
async_engine = create_async_engine("postgresql+asyncpg://admin123:admin123@172.22.88.91:5432/admin123", echo=True,
                                   future=True)

api_lab_dados = 'https://labdados.com/produtos'


async def init_db():
    async with async_engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.drop_all)
        await connection.run_sync(SQLModel.metadata.create_all)


async def add_into_database_postgres(content: list[Product]):
    async_session = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        for item in content:
            session.add(item)
            await session.commit()


def get_database():
    return client.get_database('database_products')


def get_collection(name: str):
    return get_database().get_collection(name)


async def crete_document(entity: dict, collection_name: Optional[str] = 'products') -> InsertOneResult:
    return await get_collection(collection_name).insert_one(entity)


async def crete_many_document(entities: list[dict], collection_name: Optional[str] = 'products') -> InsertManyResult:
    return await get_collection(collection_name).insert_many(entities)


async def delete_many_documents(collection_name: Optional[str] = 'products') -> DeleteResult:
    return await get_collection(collection_name).delete_many({})


async def update_many_documents(collection_name: Optional[str] = 'products', filter_param=None) -> UpdateResult:
    if filter_param is None:
        filter_param = {}
    return await get_collection(collection_name).update_many({}, filter_param)


async def find_many_documents(collection_name: Optional[str] = 'products', filter_param=None):
    if filter_param is None:
        filter_param = {}
    cursor = get_collection(collection_name).find(filter=filter_param)
    return await cursor.to_list(length=None)


async def distinct_documents(collection_name: Optional[str] = 'products', key: str = "") -> list:
    return await get_collection(collection_name).distinct(key)


async def modify_all_keys():
    document = await get_collection('products').find_one()
    for k, v in document.items():
        if k != "_id":
            str_key: str = k
            str_key = str_key.lower()
            str_key = str_key.replace(" ", "_")

            await update_many_documents(filter_param={"$rename": {
                k: str_key,
            }})


async def main():
    """ Entrypoint """
    print("starting, cleaning the database")
    await asyncio.sleep(2)

    deleted = await delete_many_documents()
    print(f"deleted {deleted.deleted_count} documents")

    async_client = AsyncClient()
    response: Response = await async_client.get('https://labdados.com/produtos')

    content_response = response.json()

    await async_client.aclose()

    result = await crete_many_document(content_response)

    print(f"added into database {len(result.inserted_ids)} new docs")

    print("Modifying documents...")

    await asyncio.sleep(3)

    result = await update_many_documents(filter_param={"$rename": {
        "lat": "Latitude",
        "lon": "Longitude"
    }})

    await modify_all_keys()

    print(f"documents modified: {result.modified_count}")

    print("distincting documents...")

    await asyncio.sleep(3)

    result = await distinct_documents(key="categoria_do_produto")

    print("distincted docs: ", result)

    documents = await find_many_documents(filter_param={
        "data_da_compra": {
            "$regex": "/202[1-9]"
        }
    })

    print("getting from CSV...")
    df_docs = pd.DataFrame(documents)

    df_docs['data_da_compra'] = pd.to_datetime(df_docs['data_da_compra'], format="%d/%m/%Y")

    print(df_docs.info())

    df_docs.to_csv("./data/csv_documents.csv")
    print("saved csv on project")

    client.close()

    keys = ['_id', 'produto', 'categoria_do_produto', 'preço', 'frete', 'data_da_compra', 'vendedor', 'local_da_compra',
            'avaliação_da_compra',
            'tipo_de_pagamento',
            'quantidade_de_parcelas',
            'latitude',
            'longitude']

    documents: list[dict] = []
    product_objects: list[Product] = []

    print("Parsing all content from csv to array of products...")

    for index, row in df_docs.iterrows():
        document = {}
        split_data = tuple(row)
        for item in split_data:
            i = split_data.index(item)
            document[keys[i]] = split_data[i]
        document.pop('_id')
        documents.append(document)

    product_objects.extend(Product(**document) for document in documents)
    print("Initialyzing relational database...")
    await init_db()
    await asyncio.sleep(3)
    await add_into_database_postgres(product_objects)
    print("adding all products into postgres...")
    await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(main())
