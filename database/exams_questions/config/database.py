from collections.abc import Iterator
from contextlib import contextmanager
import os
from threading import Lock
from typing import Optional

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://admin:admin_123@localhost:5434/question_system_db"
)


def get_database_url() -> str:
    """Retorna a URL de conexão com o banco de dados de exames e questões."""
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


class Base(DeclarativeBase):
    """Base declarativa para os modelos ORM do banco de exames e questões."""


class ExamsQuestionsDatabase:
    """Entrypoint Singleton responsável pelo acesso ao banco de exames e questões."""

    _instance: Optional["ExamsQuestionsDatabase"] = None
    _lock: Lock = Lock()

    def __new__(cls) -> "ExamsQuestionsDatabase":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._initialized = False
                    cls._instance = instance
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self.url: str = get_database_url()
        self.engine: Engine = create_engine(self.url, pool_pre_ping=True)
        self.session_factory: sessionmaker[Session] = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )
        self._initialized = True

    def get_session(self) -> Session:
        """Cria e retorna uma nova sessão do SQLAlchemy."""
        return self.session_factory()

    @contextmanager
    def session_scope(self) -> Iterator[Session]:
        """Fornece um escopo transacional de sessão com commit/rollback automático."""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def dispose(self) -> None:
        """Libera o pool de conexões da engine."""
        self.engine.dispose()

    @classmethod
    def reset_instance(cls) -> None:
        """Reinicia a instância Singleton (útil para testes isolados)."""
        with cls._lock:
            if cls._instance is not None:
                cls._instance.dispose()
                cls._instance = None


def get_database() -> ExamsQuestionsDatabase:
    """Entrypoint para recuperar a instância Singleton do banco de dados."""
    return ExamsQuestionsDatabase()
