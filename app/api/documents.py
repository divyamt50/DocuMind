import secrets
from uuid import UUID
from fastapi import status, APIRouter, Depends, Query, HTTPException, Response
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.models.models import User, Document, DocumentChunk
from app.schemas.document import DocumentRead, DocumentListResponse, DocumentCreate, DocumentUpdate
from app.core.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_tenant_id

router = APIRouter(prefix="/documents",tags=["Documents"])


@router.post("", response_model=DocumentRead, status_code = status.HTTP_201_CREATED)
async def create_document(data:DocumentCreate, tenant_id:UUID = Depends(get_tenant_id), db:AsyncSession = Depends(get_db)):
    async with db.begin():
        document = Document(
            tenant_id=tenant_id,
            file_name=data.file_name,
            s3_key=data.s3_key
        )

        db.add(document)
        await db.flush()
        await db.commit()

        result = await db.execute(
            select(Document).options(selectinload(Document.chunks))
        .where(
            Document.id == document.id,
            Document.tenant_id == tenant_id
        ))

        document = result.scalar_one()

    return document



@router.get("", response_model=DocumentListResponse, status_code=status.HTTP_200_OK)
async def list_documents(
    limit:int = Query(default=50, ge=1, le=100),
    offset:int = Query(default=0,ge=0),
    tenant_id:UUID = Depends(get_tenant_id),
    db:AsyncSession=Depends(get_db)
):
    count_result = await db.execute(
        select(func.count()).select_from(Document).where(Document.tenant_id==tenant_id)
    )
    total = count_result.scalar_one()

    result = await db.execute(
        select(Document)
        .options(selectinload(Document.chunks))
        .where(Document.tenant_id == tenant_id)
        .order_by(Document.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    documents = result.scalars().all()

    return DocumentListResponse(
        items = documents,
        total = total,
        limit = limit,
        offset= offset
    )

@router.get("/{document_id}", response_model=DocumentRead, status_code=status.HTTP_200_OK)
async def get_document(document_id:UUID, tenant_id:UUID=Depends(get_tenant_id), db:AsyncSession=Depends(get_db)):
    result = await db.execute(select(Document).options(selectinload(Document.chunks)).where(
        Document.id == document_id,
        Document.tenant_id == tenant_id
    ))

    document = result.scalar_one_or_none()

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    return document

@router.patch("/{document_id}", response_model = DocumentRead, status_code = status.HTTP_200_OK)
async def update_document(document_id:UUID,data:DocumentUpdate, tenant_id:UUID = Depends(get_tenant_id),db:AsyncSession=Depends(get_db)):
    updates = data.model_dump(exclude_unset=True)

    if not updates or updates.get("file_name") is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Provide a valid file_name to update"
        )

    async with db.begin():
        result = await db.execute(select(Document).options(selectinload(Document.chunks)).where(Document.id==document_id, Document.tenant_id == tenant_id))

        document = result.scalar_one_or_none()

        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        for key, value in updates.items():
            setattr(document, key, value)

        await db.flush()

        await db.commit()


    return document

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id:UUID, tenant_id:UUID = Depends(get_tenant_id), db:AsyncSession = Depends(get_db)):
    async with db.begin():
        result = await db.execute(
            select(Document).
            options(
                selectinload(Document.chunks)
            ).where(Document.id == document_id, Document.tenant_id == tenant_id)
        )

        document = result.scalar_one_or_none()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail = "Document not found"
            )


        await db.delete(document)

    return Response(status_code=status.HTTP_204_NO_CONTENT)