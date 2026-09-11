from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings
from app.db_models import Base
from app.main import create_app
from tests.fakes import FakeLLMAdapter

engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(engine)

app = create_app(
    settings=Settings(
        database_url="sqlite+pysqlite:///:memory:",
        frontend_origin="http://127.0.0.1:5173",
    ),
    llm_adapter=FakeLLMAdapter(),
    session_factory=sessionmaker(bind=engine, expire_on_commit=False),
)
