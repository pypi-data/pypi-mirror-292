# Import necessary modules
from __future__ import annotations

import json
import linecache
import logging
import os
import sys
from datetime import datetime
from urllib.parse import urlunsplit

import yaml
from elasticsearch import Elasticsearch

from transfer_agents.commons import setupLogging
from transfer_agents.db_functions import dbData

# Import setup logging function
# Import functions from db_functions.py


class EsData:
    """
    Class to manage Elasticsearch queries and connections.
    """

    _config = None

    def __init__(
        self,
        default_path="../config/sample.yaml",
        es_body="../config/es_body.json",
    ):
        """
        Constructor for EsData class.
        Loads the config file and sets the Elasticsearch query body.

        Parameters:
        default_path (str): Path to the configuration YAML file.
        es_body (str): Path to the Elasticsearch query body JSON file.
        """

        DEFAULT_CONFIG_FILE = "../config/sample.yaml"

        if default_path != DEFAULT_CONFIG_FILE:
            if os.path.exists(default_path):
                with open(default_path) as f:
                    self.config = yaml.safe_load(f)
                    f.close()
                    if "elasticsearch" not in self.config:
                        raise ValueError(
                            "'elasticsearch' not found in the configuration file",
                        )
            else:
                print(
                    f"Configuration file '{default_path}' not found. Using default configuration file.",
                )
                with open(DEFAULT_CONFIG_FILE) as f:
                    self.config = yaml.safe_load(f)
                    f.close()
        else:
            with open(DEFAULT_CONFIG_FILE) as f:
                self.config = yaml.safe_load(f)
                f.close()

        # Set up logging for the program
        setupLogging(default_path)
        self.logger = logging.getLogger("es_query")
        # Opening JSON file
        self.es_body = es_body

        # Dictionary to store the status of PostgreSQL queries
        # self.psql_status = self.config['elasticsearch']['status_changes']
        # import functions from es_functions.py
        self.db = dbData(default_path)

    # properties

    @property
    def root_elements(self):
        """
        Property to get the root elements.

        Returns:
        Query object containing the root elements.
        """
        return (
            object_session(self)
            .query(MetaData)
            .filter_by(project=self, parent=None)
            .order_by(MetaData.name)
        )

    @property
    def templatesection(self):
        """
        Property to get the Elasticsearch section of the config file.

        Returns:
        Dictionary containing the Elasticsearch config.
        """
        return self.config["elasticsearch"]

    # Property to return if update states transfer with for Elasticsearch
    @property
    def es_enabled(self):
        """
        Property to get if Elasticsearch is enabled or not.

        Returns:
        Boolean containing for Elasticsearch.
        """
        # return self.templatesection["enabled"]
        return self.templatesection.get("enabled", False)

    # Property to return the username for Elasticsearch
    @property
    def es_user(self):
        """
        Property to get the username for Elasticsearch.

        Returns:
        String containing the username for Elasticsearch.
        """
        return self.templatesection["user"]

    # Property to return the password for Elasticsearch
    @property
    def es_passwd(self):
        """
        Property to get the password for Elasticsearch.

        Returns:
        String containing the password for Elasticsearch.
        """
        return self.templatesection["passwd"]

    # Property to return the schema for Elasticsearch
    @property
    def es_schema(self):
        """
        Property to get the schema for Elasticsearch.

        Returns:
        String containing the schema for Elasticsearch.
        """
        return self.templatesection["schema"]

    # Property to return the host for Elasticsearch
    @property
    def es_host(self):
        """
        Property to get the host for Elasticsearch.

        Returns:
        String containing the host for Elasticsearch.
        """
        return self.templatesection["host"]

    # Property to return the port for Elasticsearch
    @property
    def es_port(self):
        """
        Property to get the port for Elasticsearch.

        Returns:
        String containing the port for Elasticsearch.
        """
        return self.templatesection["port"]

    # Property to return the status of the psql
    @property
    def psql_status(self):
        """
        Property to get the status for psql in Elasticsearch.

        Returns:
        list of transfer status for psql in Elasticsearch.
        """
        return self.config["elasticsearch"]["status_changes"]

    def run_es(self):
        return self.templatesection["query_search"]

    def query_search(self):
        return self.templatesection["query_search"]

    def query_insert(self):
        return self.templatesection["query_insert"]

    def query_update(self):
        return self.templatesection["query_update"]

    def additional_search(self):
        return self.templatesection["additional_search"]

    def additional_query(self):
        return self.templatesection["additional_query"]

    @property
    def mock_run(self):
        return self.templatesection["mock_run"]

    def es_url(self):
        # Create a list to store the URL components
        elk_url = list()

        # Check if all required values are present
        if None not in (self.es_schema, str(self.es_host + ":" + str(self.es_port))):
            # Add the URL components to the list
            elk_url.extend(
                [self.es_schema, self.es_host + ":" + str(self.es_port), "", "", ""],
            )

        # Return the URL as a string
        return urlunsplit(elk_url)

    def connect_elasticsearch(self):
        # Connect to Elasticsearch
        _es = Elasticsearch(self.es_url(), basic_auth=(self.es_user, self.es_passwd))

        # Check if the connection was successful
        if _es.ping:
            self.logger.info("Yay Connect to " + self.es_url())
        else:
            self.logger.info("Awww it could not connect!")

        # Return the Elasticsearch connection object
        return _es

    def es_query(self, file_name, file_scope, file_transfer_type):
        # Open the file containing the Elasticsearch query
        body = open(self.es_body)

        # Load the file contents as a dictionary
        es_query = json.load(body)

        # Replace the placeholders in the query with actual values
        es_query = json.loads(json.dumps(es_query).replace("$file_name", file_name))
        es_query = json.loads(json.dumps(es_query).replace("$file_scope", file_scope))
        es_query = json.loads(
            json.dumps(es_query).replace("$file_transfer_type", file_transfer_type),
        )

        # Log the final query
        self.logger.info(es_query)

        # Return the final query
        return es_query

    def process_files(self, scope):
        """
        Processes list of files and performs operations on database.
        """

        print("this is enabled value ", self.es_enabled)
        if self.es_enabled is True:
            # Loop through each status
            for status in self.psql_status:
                self.logger.info(
                    f'Processing status: {self.psql_status[status]["pql_id"]}',
                )

                # Get list of files from database
                query = self.query_search().format(
                    status=self.psql_status[status]["pql_id"],
                )
                list_files = self.db.execute_query(query)
                # Loop through each file
                for single_file in list_files:
                    # Query Elasticsearch for file information
                    query = self.es_query(
                        single_file,
                        scope,
                        self.psql_status[status]["es_id"],
                    )
                    res = self.connect_elasticsearch().search(
                        index="rucio-*",
                        query=query,
                    )

                    # Get creation date of file from Elasticsearch response
                    created_at = None
                    try:
                        created_at = res["hits"]["hits"][0]["_source"]["created_at"]
                        created_at = datetime.strptime(
                            created_at,
                            "%Y-%m-%dT%H:%M:%S.%f",
                        )
                        created_at = datetime.strftime(created_at, "%Y-%m-%d %H:%M:%S")
                        self.logger.info(created_at)
                    except Exception as e:
                        self.logger.warning(
                            f"No entry found in Elasticsearch for file {single_file}. Error: {e}",
                        )
                    except KeyError as e:
                        self.logger.warning(
                            f"Field not found in Elasticsearch response: {e}",
                        )
                        created_at = None

                    # If additional search is required and creation date is available
                    if self.additional_search() and created_at:
                        # Perform additional search for file
                        add_query = self.additional_query()
                        add_query = add_query.format("%s" % single_file)
                        id_files = list(self.db.execute_query(add_query))[0]
                        self.logger.info(id_files)

                        # Prepare insert and update queries
                        in_query = self.query_insert().format(
                            id_files,
                            created_at,
                            self.psql_status[status]["next_status"],
                        )
                        up_query = self.query_update().format(
                            self.psql_status[status]["next_status"],
                            id_files,
                        )
                        self.logger.info(in_query)
                        self.logger.info(up_query)
                        # Execute insert and update queries (if not a mock run)

                    else:
                        # Perform additional search for file
                        up_query = self.query_update().format(
                            self.psql_status[status]["next_status"],
                            created_at,
                            single_file,
                        )

                    if not self.mock_run:
                        self.logger.info(
                            f"Real run, updating and inserting into database (mock run set to {self.mock_run})",
                        )
                        try:
                            self.db.commit_changes(in_query)
                        except Exception:
                            exc_type, exc_obj, tb = sys.exc_info()
                            f = tb.tb_frame
                            lineno = tb.tb_lineno
                            filename = f.f_code.co_filename
                            linecache.checkcache(filename)
                            line = linecache.getline(filename, lineno, f.f_globals)
                            self.logger.warning(
                                f'EXCEPTION IN ({filename}, LINE {lineno} "{line.strip()}"): {exc_obj}',
                            )
                        try:
                            print(up_query)

                            self.db.commit_changes(up_query)
                        except:
                            exc_type, exc_obj, tb = sys.exc_info()
                            f = tb.tb_frame
                            lineno = tb.tb_lineno
                            filename = f.f_code.co_filename
                            linecache.checkcache(filename)
                            line = linecache.getline(filename, lineno, f.f_globals)
                            self.logger.warning(
                                f'EXCEPTION IN ({filename}, LINE {lineno} "{line.strip()}"): {exc_obj}',
                            )
                    else:
                        self.logger.info(
                            "- This is a mock run, no entry will be updated or inserted.",
                        )

        else:
            self.logger.info("Elasticsearch is not enabled, skipping execution.")
