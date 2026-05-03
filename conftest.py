import pytest
from django.db import connections


@pytest.fixture(autouse=True)
def close_db_connections_after_test():
    """
    Закриває всі відкриті з'єднання з PostgreSQL після кожного тесту,
    щоб pytest-django міг видалити тестову БД без помилок.
    """
    yield
    for conn in connections.all():
        conn.close()