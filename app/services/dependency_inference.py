from app.database.neo4j import neo4j_connection


class DependencyInferenceService:

    @staticmethod
    def infer_and_store():

        query = """
        MATCH (source:SystemEntity)-[:NETWORK_CONNECTED]->(target:SystemEntity)
        MATCH (target)-[:EXPOSES]->(service:Service)
        MATCH (service)-[:LISTENS_ON]->(endpoint:Endpoint)

        MERGE (source)-[r:DEPENDS_ON]->(target)

        SET
            r.service = service.name,
            r.protocol = endpoint.protocol,
            r.port = endpoint.port,
            r.evidence = "network_and_exposed_service",
            r.confidence = 0.40

        RETURN
            source.name AS source,
            target.name AS target,
            service.name AS service,
            endpoint.port AS port,
            r.confidence AS confidence
        """

        results = []

        with neo4j_connection.driver.session() as session:
            records = session.run(query)

            for record in records:
                results.append(dict(record))

        return results
