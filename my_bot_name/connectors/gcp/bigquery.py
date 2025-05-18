import asyncio
import logging
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from google.cloud import bigquery
from google.cloud.exceptions import NotFound


class GoogleBigQueryConnector:
    def __init__(
        self, project_id: Optional[str] = None, logger: Optional[logging.Logger] = None
    ):
        self.client = bigquery.Client(project=project_id)
        self.logger = logger or logging.getLogger(__name__)

    # Synchronous methods
    def execute_query(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """
        Execute a BigQuery SQL query synchronously.

        :param query: SQL query to execute
        :param params: Optional query parameters
        :return: Query results as a pandas DataFrame
        """
        self.logger.info(f"Executing BigQuery query: {query[:100]}...")

        try:
            job_config = bigquery.QueryJobConfig(query_parameters=params or [])
            query_job = self.client.query(query, job_config=job_config)
            result = query_job.to_dataframe()

            self.logger.info(
                f"Successfully executed query, returned {len(result)} rows"
            )
            return result
        except Exception as e:
            self.logger.error(f"Error executing BigQuery query: {str(e)}")
            raise

    def get_table_data(
        self, dataset_id: str, table_id: str, limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Get data from a BigQuery table synchronously.

        :param dataset_id: ID of the dataset
        :param table_id: ID of the table
        :param limit: Optional row limit
        :return: Table data as a pandas DataFrame
        """
        self.logger.info(f"Getting data from table {dataset_id}.{table_id}")

        try:
            query = f"SELECT * FROM `{dataset_id}.{table_id}`"
            if limit:
                query += f" LIMIT {limit}"

            return self.execute_query(query)
        except Exception as e:
            self.logger.error(
                f"Error getting data from table {dataset_id}.{table_id}: {str(e)}"
            )
            raise

    def table_exists(self, dataset_id: str, table_id: str) -> bool:
        """
        Check if a BigQuery table exists synchronously.

        :param dataset_id: ID of the dataset
        :param table_id: ID of the table
        :return: True if the table exists, False otherwise
        """
        self.logger.info(f"Checking if table {dataset_id}.{table_id} exists")

        try:
            table_ref = self.client.dataset(dataset_id).table(table_id)
            self.client.get_table(table_ref)
            self.logger.info(f"Table {dataset_id}.{table_id} exists")
            return True
        except NotFound:
            self.logger.info(f"Table {dataset_id}.{table_id} does not exist")
            return False
        except Exception as e:
            self.logger.error(
                f"Error checking if table {dataset_id}.{table_id} exists: {str(e)}"
            )
            raise

    def create_table(
        self, dataset_id: str, table_id: str, schema: List[bigquery.SchemaField]
    ) -> None:
        """
        Create a BigQuery table synchronously.

        :param dataset_id: ID of the dataset
        :param table_id: ID of the table
        :param schema: List of SchemaField objects defining the table schema
        """
        self.logger.info(f"Creating table {dataset_id}.{table_id}")

        try:
            table_ref = self.client.dataset(dataset_id).table(table_id)
            table = bigquery.Table(table_ref, schema=schema)
            self.client.create_table(table)
            self.logger.info(f"Successfully created table {dataset_id}.{table_id}")
        except Exception as e:
            self.logger.error(f"Error creating table {dataset_id}.{table_id}: {str(e)}")
            raise

    def upload_dataframe(
        self,
        dataset_id: str,
        table_id: str,
        dataframe: pd.DataFrame,
        write_disposition: str = "WRITE_TRUNCATE",
    ) -> None:
        """
        Upload a pandas DataFrame to a BigQuery table synchronously.

        :param dataset_id: ID of the dataset
        :param table_id: ID of the table
        :param dataframe: Pandas DataFrame to upload
        :param write_disposition: Write disposition (WRITE_TRUNCATE, WRITE_APPEND, WRITE_EMPTY)
        """
        self.logger.info(f"Uploading {len(dataframe)} rows to {dataset_id}.{table_id}")

        try:
            table_ref = self.client.dataset(dataset_id).table(table_id)
            job_config = bigquery.LoadJobConfig(
                write_disposition=write_disposition,
            )

            job = self.client.load_table_from_dataframe(
                dataframe, table_ref, job_config=job_config
            )
            job.result()  # Wait for the job to complete

            self.logger.info(f"Successfully uploaded data to {dataset_id}.{table_id}")
        except Exception as e:
            self.logger.error(
                f"Error uploading data to {dataset_id}.{table_id}: {str(e)}"
            )
            raise

    # Asynchronous methods
    async def execute_query_async(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """
        Execute a BigQuery SQL query asynchronously.

        :param query: SQL query to execute
        :param params: Optional query parameters
        :return: Query results as a pandas DataFrame
        """
        self.logger.info(f"Initiating async BigQuery query: {query[:100]}...")
        return await asyncio.to_thread(self.execute_query, query, params)

    async def get_table_data_async(
        self, dataset_id: str, table_id: str, limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Get data from a BigQuery table asynchronously.

        :param dataset_id: ID of the dataset
        :param table_id: ID of the table
        :param limit: Optional row limit
        :return: Table data as a pandas DataFrame
        """
        self.logger.info(
            f"Initiating async get data from table {dataset_id}.{table_id}"
        )
        return await asyncio.to_thread(self.get_table_data, dataset_id, table_id, limit)

    async def table_exists_async(self, dataset_id: str, table_id: str) -> bool:
        """
        Check if a BigQuery table exists asynchronously.

        :param dataset_id: ID of the dataset
        :param table_id: ID of the table
        :return: True if the table exists, False otherwise
        """
        self.logger.info(
            f"Checking if table {dataset_id}.{table_id} exists asynchronously"
        )
        return await asyncio.to_thread(self.table_exists, dataset_id, table_id)

    async def create_table_async(
        self, dataset_id: str, table_id: str, schema: List[bigquery.SchemaField]
    ) -> None:
        """
        Create a BigQuery table asynchronously.

        :param dataset_id: ID of the dataset
        :param table_id: ID of the table
        :param schema: List of SchemaField objects defining the table schema
        """
        self.logger.info(f"Initiating async creation of table {dataset_id}.{table_id}")
        await asyncio.to_thread(self.create_table, dataset_id, table_id, schema)

    async def upload_dataframe_async(
        self,
        dataset_id: str,
        table_id: str,
        dataframe: pd.DataFrame,
        write_disposition: str = "WRITE_TRUNCATE",
    ) -> None:
        """
        Upload a pandas DataFrame to a BigQuery table asynchronously.

        :param dataset_id: ID of the dataset
        :param table_id: ID of the table
        :param dataframe: Pandas DataFrame to upload
        :param write_disposition: Write disposition (WRITE_TRUNCATE, WRITE_APPEND, WRITE_EMPTY)
        """
        self.logger.info(
            f"Initiating async upload of {len(dataframe)} rows to {dataset_id}.{table_id}"
        )
        await asyncio.to_thread(
            self.upload_dataframe, dataset_id, table_id, dataframe, write_disposition
        )


# Create a singleton instance that can be imported elsewhere
bigquery_connector = GoogleBigQueryConnector()
