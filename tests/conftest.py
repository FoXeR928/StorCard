import pytest
import importlib
from unittest.mock import patch
from loguru import logger
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient


from src.database.base import Base
from src.api.app import app
import src.core.constants as constants
import src.core.config as config
import src.core.log as log


@pytest.fixture(scope="session")
def test_dirs(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp("app_test_root")
    data_dir = tmp_dir / "data"
    logs_dir = tmp_dir / "logs"
    data_dir.mkdir()
    logs_dir.mkdir()
    return {"data": data_dir, "logs": logs_dir}


@pytest.fixture(autouse=True, scope="session")
def setup_global_patches(test_dirs):
    data_path = test_dirs["data"]
    logs_path = test_dirs["logs"]
    conf_path = data_path / "config.json"

    with (
        patch("src.core.constants.DATA_DIR", data_path),
        patch("src.core.constants.LOGS_DIR", logs_path),
        patch("src.core.constants.CONFIG_FILE", conf_path),
        patch("src.core.config.DATA_DIR", data_path),
        patch("src.core.config.CONFIG_FILE", conf_path),
    ):
        importlib.reload(constants)
        importlib.reload(config)
        importlib.reload(log)
        yield


@pytest.fixture(autouse=True)
def mock_system_actions(request):
    if "test_system" in request.node.name or "unit" in str(request.node.fspath):
        yield
        return
    with (
        patch("src.core.system.reboot_server") as mock_reboot,
        patch("src.core.system.stop_server") as mock_stop,
        patch("os.execv"),
        patch("sys.exit"),
    ):
        yield mock_reboot, mock_stop


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def caplog_loguru(caplog):
    logger.remove()
    sink_id = logger.add(caplog.handler, format="{message}", level="DEBUG")
    yield caplog
    try:
        logger.remove(sink_id)
    except Exception:
        pass
