import uuid
from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, DateTime, Integer, Text, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from typing import List, Optional
from pgvector.sqlalchemy import Vector

class Base(DeclarativeBase):
    id:Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda:datetime.now(timezone.utc))
    modified_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda:datetime.now(timezone.utc),
                                                 onupdate=lambda:datetime.now(timezone.utc))
    pass

class Tenant(Base):
    __tablename__ = "tenants"
    
    #id:Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name:Mapped[str] = mapped_column(String(255), nullable=False)
    api_key:Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    #created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    documents:Mapped[List["Document"]] = relationship("Document", back_populates="tenant", cascade="all, delete-orphan")
    users:Mapped[List["User"]] = relationship("User", back_populates="tenant", cascade="all, delete-orphan")

class Document(Base):
    __tablename__ = "documents"

    #id:Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id:Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    file_name:Mapped[str] = mapped_column(String(255), nullable=False)
    s3_key:Mapped[str] = mapped_column(String(255), nullable=False)
    status:Mapped[str] = mapped_column(String(255), default="Pending", nullable=False)
    #created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda:datetime.now(timezone.utc))

    tenant:Mapped["Tenant"] = relationship("Tenant", back_populates="documents")
    chunks:Mapped[List["DocumentChunk"]] = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    #id:Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id:Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id:Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index:Mapped[int] = mapped_column(Integer, nullable=False)
    content:Mapped[str] = mapped_column(Text, nullable=False)

    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(1536), nullable=True)

    document:Mapped["Document"] = relationship("Document", back_populates="chunks")

    # __table_args__ = (
    #     Index("idx_chunks_tenant_id", "tenant_id"),
    # )

class User(Base):
    __tablename__ = "users"

    name:Mapped[str] = mapped_column(String(255), nullable=False)
    tenant_id:Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    email:Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password_hash:Mapped[str] = mapped_column(String(255), nullable=False)

    tenant:Mapped["Tenant"] = relationship("Tenant", back_populates="users")