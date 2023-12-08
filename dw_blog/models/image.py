import uuid
from typing import Optional
from datetime import datetime

from sqlmodel import Field, SQLModel, Relationship

from dw_blog.schemas.image import ImageType
from dw_blog.models.post import Post


class Image(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    title: str = Field(min_length=3, max_length=500, nullable=False)
    caption: Optional[str] = Field(min_length=5, max_length=2000, nullable=True)
    size: int = Field(nullable=False, lt=52428800)
    img_type: ImageType = Field(nullable=False)
    date_created: datetime = Field(default_factory=datetime.utcnow)
    date_modified: datetime = Field(default_factory=datetime.utcnow)
    # post: Post = Relationship(back_populates="images")
