"""
Neo4j driver connection manager for NYAYASETU.
"""
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

_driver = None


def get_neo4j_config():
    uri = getattr(settings, "NEO4J_URI", "bolt://localhost:7687")
    user = getattr(settings, "NEO4J_USERNAME", "neo4j")
    password = getattr(settings, "NEO4J_PASSWORD", "password")
    return uri, user, password


def get_neo4j_driver():
    global _driver
    if _driver is not None:
        return _driver

    try:
        from neo4j import GraphDatabase
        uri, user, password = get_neo4j_config()
        _driver = GraphDatabase.driver(uri, auth=(user, password))
        return _driver
    except Exception as e:
        logger.warning(f"Failed to initialize Neo4j driver: {e}")
        return None


def check_neo4j_connection():
    """Verify if Neo4j is reachable."""
    driver = get_neo4j_driver()
    if driver is None:
        return False, "Neo4j driver not initialized or library not installed."
    try:
        driver.verify_connectivity()
        return True, "Connected to Neo4j successfully."
    except Exception as e:
        return False, f"Cannot connect to Neo4j: {e}"


def close_driver():
    global _driver
    if _driver is not None:
        try:
            _driver.close()
        except Exception:
            pass
        _driver = None

