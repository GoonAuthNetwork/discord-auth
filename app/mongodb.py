from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

from app.config import db_settings


class Database:
    client: AsyncIOMotorClient = None
    engine: AIOEngine = None


db = Database()


async def get_database() -> AsyncIOMotorClient:
    return db.client


async def get_engine() -> AIOEngine:
    return db.engine


async def connect_to_mongo() -> None:
    logger.info("Connecting to database...")

    db.client = AsyncIOMotorClient(
        db_settings.connection_string(),
        maxPoolSize=db_settings.min_connections,
        minPoolSize=db_settings.max_connections,
    )
    db.engine = AIOEngine(db.client, db_settings.database_name)

    logger.info("Database connected!")

    # Configure indexes
    # UserAuthRequest.configure_index(db.engine)

    logger.info("Database indexes configured")


async def close_mongo_connection() -> None:
    logger.info("Closing database connection...")

    db.engine = None
    db.client.close()

    logger.info("Database closed!")
