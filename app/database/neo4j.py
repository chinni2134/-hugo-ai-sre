from neo4j import GraphDatabase

from app.core.config import settings


class Neo4jConnection:

    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(
                settings.neo4j_user,
                settings.neo4j_password,
            ),
        )

    def verify(self):
        self.driver.verify_connectivity()

    def close(self):
        self.driver.close()


neo4j_connection = Neo4jConnection()
