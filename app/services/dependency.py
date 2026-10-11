from app.database.neo4j import neo4j_connection


class DependencyService:

    @staticmethod
    def sync_entity(
        entity_id: str,
        name: str,
        entity_type: str,
        environment: str = "development",
    ):

        query = """
        MERGE (entity:SystemEntity {
            entity_id: $entity_id
        })

        SET
            entity.name = $name,
            entity.entity_type = $entity_type,
            entity.environment = $environment

        RETURN
            entity.entity_id AS entity_id,
            entity.name AS name,
            entity.entity_type AS entity_type,
            entity.environment AS environment
        """

        with neo4j_connection.driver.session() as session:

            result = session.run(
                query,
                entity_id=entity_id,
                name=name,
                entity_type=entity_type,
                environment=environment,
            )

            return result.single()


    @staticmethod
    def create_dependency(
        source_id: str,
        target_id: str,
        relationship: str,
    ):

        query = """
        MATCH (source:SystemEntity {
            entity_id: $source_id
        })

        MATCH (target:SystemEntity {
            entity_id: $target_id
        })

        MERGE (source)-[r:DEPENDS_ON {
            relationship: $relationship
        }]->(target)

        RETURN
            source.entity_id AS source,
            target.entity_id AS target,
            r.relationship AS relationship
        """

        with neo4j_connection.driver.session() as session:

            result = session.run(
                query,
                source_id=source_id,
                target_id=target_id,
                relationship=relationship,
            )

            return result.single()
