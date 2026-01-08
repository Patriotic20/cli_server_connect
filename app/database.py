from sqlalchemy import create_engine, DateTime, func, CheckConstraint
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

DATABASE_URL = "sqlite:///ssh_connections.db"
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class SSHServer(Base):
    __tablename__ = "ssh_servers"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    host: Mapped[str] = mapped_column(nullable=False)
    port: Mapped[int] = mapped_column(
        CheckConstraint('port > 0 and port <= 65535'),
        nullable=False
    )
    username: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

Base.metadata.create_all(engine)