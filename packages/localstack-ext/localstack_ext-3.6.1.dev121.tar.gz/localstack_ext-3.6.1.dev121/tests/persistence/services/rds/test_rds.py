import pymysql
import pytest
from localstack.utils.strings import short_uid
from localstack.utils.sync import retry
from postgres import Postgres


def wait_until_db_cluster_available(client, cluster_id: str):
    def check_running():
        result = client.describe_db_clusters(DBClusterIdentifier=cluster_id)["DBClusters"]
        assert result[0].get("Status") == "available"

    retry(check_running, sleep=1, retries=25)


def wait_until_db_instance_available(client, instance_id: str):
    def check_running():
        result = client.describe_db_instances(DBInstanceIdentifier=instance_id)["DBInstances"]
        assert result[0].get("DBInstanceStatus") == "available"

    retry(check_running, sleep_before=3, sleep=2, retries=60)


def _wait_for_instance_and_get_port(rds_client, db_instance_id: str) -> int:
    wait_until_db_instance_available(rds_client, db_instance_id)
    port = rds_client.describe_db_instances(DBInstanceIdentifier=db_instance_id)["DBInstances"][0][
        "Endpoint"
    ]["Port"]
    return port


class TestRDS:
    db_name = "mydb"
    db_user = "hello"
    db_password = "H3lloW0rld!"
    table_name = f"test{short_uid()}"
    query = f"""
                CREATE TABLE {table_name} (id integer, test varchar(11));
                INSERT INTO {table_name}(id, test) VALUES (123, 'hello there');
            """
    query_check = f"SELECT * FROM {table_name}"
    query_assert = [{"id": 123, "test": "hello there"}]

    def _query_postgres(self, port: int, query: str):
        """Add some dummy date into the database"""
        db = Postgres(
            f"postgres://{self.db_user}:{self.db_password}@127.0.0.1:{port}/{self.db_name}"
        )

        try:
            if "select" in query.lower():
                result = db.all(query)
                for i in range(len(result)):
                    if isinstance(result[i], tuple):
                        result[i] = result[i]._asdict()
                return result
            db.run(query)
        finally:
            db.pool.clear()

    def _query_mysql(self, port: int, query: str):
        connection = pymysql.connect(
            user=self.db_user,
            password=self.db_password,
            port=port,
            database=self.db_name,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )
        try:
            with connection.cursor() as cursor:
                queries = [q for q in query.split(";") if q.strip()]
                result = None
                for query in queries:
                    cursor.execute(query)
                    result = cursor.fetchall()
                return result
        finally:
            connection.close()

    @pytest.mark.skip_snapshot_verify(
        paths=[
            "$..DBInstances..DbInstancePort",
            "$..DBInstances..Endpoint.Port",
            "$..DBInstances..DbiResourceId",
        ]
    )
    @pytest.mark.parametrize("db_type", ["mariadb", "mysql"])
    def test_rds_mariadb_and_mysql(self, persistence_validations, snapshot, db_type, aws_client):
        db_instance_id = f"rds-inst-{short_uid()}"
        instance_class = "db.t3.large"

        aws_client.rds.create_db_instance(
            DBInstanceIdentifier=db_instance_id,
            Engine=db_type,
            DBInstanceClass=instance_class,
            DBName=self.db_name,
            EngineVersion="8.0",  # this has no effect for mariadb
            MasterUsername=self.db_user,
            MasterUserPassword=self.db_password,
        )
        port = _wait_for_instance_and_get_port(aws_client.rds, db_instance_id)

        # add some dummy data into the database
        self._query_mysql(port, self.query)

        def validate():
            _port = _wait_for_instance_and_get_port(aws_client.rds, db_instance_id)
            snapshot.match(
                f"rds_describe_instance_{db_type}",
                aws_client.rds.describe_db_instances(DBInstanceIdentifier=db_instance_id),
            )
            assert self._query_mysql(_port, self.query_check) == self.query_assert

        persistence_validations.register(validate)

    @pytest.mark.skip_snapshot_verify(
        paths=["$..DBInstances..DbInstancePort", "$..DBInstances..DbiResourceId"]
    )
    def test_rds_postgres_cluster(self, persistence_validations, snapshot, aws_client):
        cluster_id = f"db-cluster-{short_uid()}"
        db_instance_id = f"rds-inst-{short_uid()}"
        db_type = "aurora-postgresql"
        instance_class = "db.t3.large"
        aws_client.rds.create_db_cluster(
            DBClusterIdentifier=cluster_id,
            Engine=db_type,
            DatabaseName=self.db_name,
            MasterUsername=self.db_user,
            MasterUserPassword=self.db_password,
        )
        instance_id = aws_client.rds.create_db_instance(
            DBClusterIdentifier=cluster_id,
            DBInstanceIdentifier=db_instance_id,
            Engine=db_type,
            DBInstanceClass=instance_class,
        )["DBInstance"]["DBInstanceIdentifier"]
        # not waiting before resetting will result in the cluster not being persisted
        wait_until_db_cluster_available(aws_client.rds, cluster_id)
        port = _wait_for_instance_and_get_port(aws_client.rds, db_instance_id)

        # add some dummy data into the database
        self._query_postgres(port, self.query)

        def validate():
            wait_until_db_cluster_available(aws_client.rds, cluster_id)
            _port = _wait_for_instance_and_get_port(aws_client.rds, db_instance_id)
            snapshot.match(
                "rds_describe_instance",
                aws_client.rds.describe_db_instances(DBInstanceIdentifier=instance_id),
            )
            assert self._query_postgres(_port, self.query_check) == self.query_assert

        persistence_validations.register(validate)
