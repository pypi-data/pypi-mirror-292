import os
import logging
from azure.cosmos import CosmosClient, exceptions

class CosmosContainerClient:
    _client_instance = None

    def __new__(cls, *args, **kwargs):
        if cls._client_instance is None:
            cls._client_instance = super(CosmosContainerClient, cls).__new__(cls)
        return cls._client_instance

    def __init__(self, connection_string: str, db_name: str, container_name: str):
        if not hasattr(self, 'initialized'):
            self.account_client = CosmosClient.from_connection_string(connection_string)
            self.db_client = self.account_client.get_database_client(db_name)
            self.container_client = self.db_client.get_container_client(container_name)
            self.initialized = True

    def set_database_and_container(self, db_name: str, container_name: str):
        """
        Set the database and container client to a different database and container.

        :param db_name: Name of the database to switch to.
        :param container_name: Name of the container to switch to.
        """
        self.db_client = self.account_client.get_database_client(db_name)
        self.container_client = self.db_client.get_container_client(container_name)

    def query_cosmosdb_container(self, query: str, partition_key=None):
        """
        Query items in the Cosmos DB container.

        :param query: SQL query string.
        :param partition_key: Optional partition key for the query.
        :return: List of documents matching the query.
        """
        try:
            if partition_key:
                documents = list(self.container_client.query_items(query=query, partition_key=partition_key))
            else:
                documents = list(self.container_client.query_items(query=query, enable_cross_partition_query=True))
            return documents
        except exceptions.CosmosHttpResponseError as e:
            logging.error(f"Error querying CosmosDB container: {e}")
            raise

    def upsert_cosmosdb_document(self, document: dict):
        """
        Insert or update a document in the Cosmos DB container.

        :param document: Document to be inserted or updated.
        """
        try:
            self.container_client.upsert_item(document)
        except exceptions.CosmosHttpResponseError as e:
            logging.error(f"Error inserting document into CosmosDB container: {e}")
            raise

# Example usage:
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    connection_string = os.getenv("COSMOS_CONNECTION_STRING")
    db_name = "your_db_name"
    container_name = "your_container_name"

    client = CosmosContainerClient(connection_string, db_name, container_name)
    
    # Query from the initial container
    query = "SELECT * FROM c"
    documents = client.query_cosmosdb_container(query)
    print(documents)
    
    # Switch to a different database and container
    new_db_name = "another_db_name"
    new_container_name = "another_container_name"
    client.set_database_and_container(new_db_name, new_container_name)
    
    # Query from the new container
    documents = client.query_cosmosdb_container(query)
    print(documents)
