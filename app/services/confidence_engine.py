from app.database.neo4j import neo4j_connection


class ConfidenceEngine:

    @staticmethod
    def calculate():

        query = """
        MATCH (source:SystemEntity)-[r:DEPENDS_ON]->(target:SystemEntity)

        OPTIONAL MATCH (source)-[o:OBSERVED_CONNECTIVITY]->(target)

        SET
            r.confidence =
                CASE
                    WHEN o IS NOT NULL THEN 0.85
                    ELSE 0.40
                END,

            r.evidence =
                CASE
                    WHEN o IS NOT NULL
                    THEN "network_and_observed_tcp_connectivity"
                    ELSE "network_and_exposed_service"
                END

        RETURN
            source.name AS source,
            target.name AS target,
            r.service AS service,
            r.port AS port,
            r.confidence AS confidence,
            r.evidence AS evidence
        """

        results = []

        with neo4j_connection.driver.session() as session:

            for record in session.run(query):
                results.append(dict(record))

        return results
