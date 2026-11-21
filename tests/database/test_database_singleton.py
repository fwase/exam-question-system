from unittest.mock import MagicMock

import pytest

from database.exams_questions.config import (
    DEFAULT_DATABASE_URL,
    ExamsQuestionsDatabase,
    get_database,
    get_database_url,
)


@pytest.fixture(autouse=True)
def reset_singleton():
    ExamsQuestionsDatabase.reset_instance()
    yield
    ExamsQuestionsDatabase.reset_instance()


def test_singleton_returns_same_instance():
    db1 = ExamsQuestionsDatabase()
    db2 = ExamsQuestionsDatabase()
    db3 = get_database()

    assert db1 is db2
    assert db1 is db3
    assert db1.engine is db2.engine
    assert db1.session_factory is db2.session_factory


def test_get_database_url_default_and_env_override(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert get_database_url() == DEFAULT_DATABASE_URL

    custom_url = "postgresql+psycopg://user:pass@localhost:5435/custom_db"
    monkeypatch.setenv("DATABASE_URL", custom_url)
    assert get_database_url() == custom_url


def test_session_scope_commits_and_closes():
    db = get_database()
    mock_session = MagicMock()
    db.session_factory = MagicMock(return_value=mock_session)

    with db.session_scope() as session:
        assert session is mock_session

    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_not_called()
    mock_session.close.assert_called_once()


def test_session_scope_rolls_back_on_error():
    db = get_database()
    mock_session = MagicMock()
    db.session_factory = MagicMock(return_value=mock_session)

    with pytest.raises(RuntimeError, match="boom"):
        with db.session_scope():
            raise RuntimeError("boom")

    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_called_once()
    mock_session.close.assert_called_once()
