import pytest
from sqlalchemy.orm import Session

from app.db.database import engine


@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="module")
def chrome():
    sync_api = pytest.importorskip("playwright.sync_api")
    playwright = sync_api.sync_playwright().start()
    try:
        browser = playwright.chromium.launch(channel="chrome", headless=True)
    except Exception as error:
        playwright.stop()
        pytest.skip(f"Chrome is not available: {error}")
    yield browser
    browser.close()
    playwright.stop()


@pytest.fixture
def chrome_page(chrome):
    page = chrome.new_page()
    yield page
    page.close()
