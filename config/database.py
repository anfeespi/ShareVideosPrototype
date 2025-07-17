import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure

MONGO_DETAILS = os.environ.get("MONGO_URI")

client: AsyncIOMotorClient = None

async def mongo_connect():
    global client
    try:
        client = AsyncIOMotorClient(MONGO_DETAILS)
        await client.admin.command('ping')
        print("Conectado a mongo!")
    except ConnectionFailure as e:
        print(f"No se pudo conectar a MongoDB: {e}")
        raise ConnectionFailure(f"No se pudo conectar a MongoDB: {e}")
    except Exception as e:
        print(f"Error inesperado {e}")
        raise Exception(f"Error inesperado {e}")


async def mongo_disconnect():
    global client
    if client:
        client.close()
        print("Conexión cerrada")

def get_database():
    return client.videos_db