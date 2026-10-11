import asyncio
import uuid

from app.core.db import AsyncSessionLocal
from app.models.models import Tenant, User


async def main():
    async with AsyncSessionLocal() as session:
        # 1. Create and save Tenant
        tenant = Tenant(
            name="Acme Corp",
            api_key=f"acme_{uuid.uuid4().hex[:8]}",
        )
        session.add(tenant)
        await session.flush()

        print(f"Created Tenant: {tenant.name} -> ID: {tenant.id}")

        # 2. Create and save User linked to Tenant
        user = User(
            name="Alice",
            tenant_id=tenant.id,
        )
        session.add(user)
        await session.commit()

        print(f"Created User: {user.name} -> ID: {user.id}")


if __name__ == "__main__":
    asyncio.run(main())
