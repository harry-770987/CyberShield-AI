import asyncio
import os
import sys

# Add parent to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.config import settings
from core.database import Base
import models.user  # import to register
import models.alert

async def seed():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    from core.security import get_password_hash
    from models.user import User

    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with AsyncSessionLocal() as session:
        # Create default admin user
        hashed = get_password_hash("admin")
        admin = User(email="admin@cybershield.ai", username="admin", hashed_password=hashed)
        session.add(admin)
        await session.commit()
    print("Database seeded with default admin:admin user.")

if __name__ == "__main__":
    asyncio.run(seed())
