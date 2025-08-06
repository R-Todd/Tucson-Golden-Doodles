# tests/conftest.py

import pytest
import threading
from werkzeug.serving import make_server
from app import create_app, db as _db
from config import TestingConfig
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class LiveServer:
    """A simple live server implementation that runs in a thread."""
    def __init__(self, app, host='127.0.0.1', port=5000):
        self._app = app
        self._host = host
        self._port = port
        self._server = make_server(self._host, self._port, self._app)
        self._thread = threading.Thread(target=self._server.serve_forever)
        self._thread.daemon = True

    def start(self):
        self._thread.start()

    def stop(self):
        self._server.shutdown()
        self._thread.join()

    @property
    def url(self):
        return f"http://{self._host}:{self._port}"

@pytest.fixture(scope='session')
def app():
    """Session-wide test Flask application."""
    app = create_app(TestingConfig)
    app_context = app.app_context()
    app_context.push()
    yield app
    app_context.pop()

@pytest.fixture(scope='session')
def db(app):
    """Session-wide database."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()

@pytest.fixture(scope='function')
def session(db):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()
    db.session.begin_nested()
    yield db.session
    db.session.rollback()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope='function')
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='session')
def chrome_driver():
    """Initializes a headless Chrome WebDriver instance."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

@pytest.fixture(scope='session')
def live_server(app):
    """Fixture to run the application in a live server thread."""
    server = LiveServer(app)
    server.start()
    yield server
    server.stop()