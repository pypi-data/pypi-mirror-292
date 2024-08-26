from __future__ import annotations

import linecache
import logging
import os
import sys

import psycopg2
import yaml

from transfer_agents.commons import setupLogging

# Import the `setupLogging` function from the `commons` module


class dbData:
    """
    The dbData class provides a connection to a PostgreSQL database and
    functions to query and commit data to the database.
    """

    def __init__(self, default_config="../config/sample.yaml"):
        """
        Loads the database configuration from a YAML file.

        Args:
            default_config (str, optional): The file path to the YAML configuration file. Defaults to '../config/sample.yaml'.
        """
        DEFAULT_CONFIG_FILE = "../config/sample.yaml"

        if default_config != DEFAULT_CONFIG_FILE:
            if os.path.exists(default_config):
                with open(default_config) as f:
                    self.config = yaml.safe_load(f)
                    f.close()
                    if "psql" not in self.config:
                        raise ValueError("'psql' not found in the configuration file")
            else:
                print(
                    f"Configuration file '{default_config}' not found. Using default configuration file.",
                )
                with open(DEFAULT_CONFIG_FILE) as f:
                    self.config = yaml.safe_load(f)
                    f.close()
        else:
            with open(DEFAULT_CONFIG_FILE) as f:
                self.config = yaml.safe_load(f)
                f.close()
        # Call the `setupLogging` function to configure logging
        setupLogging(default_config)

        # Create a self.logger with the name `client.agents.list_file`
        self.logger = logging.getLogger("list_file")

    @property
    def templatesection(self):
        """
        Returns the 'psql' section of the YAML configuration file.

        Returns:
            dict: The 'psql' section of the YAML configuration file.
        """
        return self.config["psql"]

    @property
    def db_user(self):
        """
        Returns the database username from the YAML configuration file.

        Returns:
            str: The database username.
        """
        return self.templatesection["user"]

    @property
    def db_passwd(self):
        """
        Returns the database password from the YAML configuration file.

        Returns:
            str: The database password.
        """
        return self.templatesection["passwd"]

    @property
    def db_port(self):
        """
        Returns the database port from the YAML configuration file.

        Returns:
            str: The database port.
        """
        return self.templatesection["port"]

    @property
    def db_database(self):
        """
        Returns the database name from the YAML configuration file.

        Returns:
            str: The database name.
        """
        return self.templatesection["db"]

    @property
    def db_host(self):
        """
        Returns the database host from the YAML configuration file.
        """
        return self.templatesection["host"]

    @property
    def db_config(self):
        """
        Initialize the database connection.

        Args:
            host (str): The host name or IP address of the database server.
            database (str): The name of the database.
            user (str): The name of the user.
            password (str): The password for the user.
            port (int, optional): The port number. Defaults to 5432.
        """
        config = {
            "user": self.db_user,
            "host": self.db_host,
            "password": self.db_passwd,
            "database": self.db_database,
        }

        return config

    def get_connection(self):
        """_summary_

        Returns:
            _type_: _description_
                    return psycopg2.connect(database="mock",
                            host="mock.pic.es",
                            user="mock",
                            password="mock",
                            port="5432")
        """
        try:
            return psycopg2.connect(**self.db_config)
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

    def execute_query(self, query):
        """
        Execute a query on the database and return the result.

        Args:
            query (str): The SQL query to be executed.

        Returns:
            result (set): A set of results returned by the query.
        """
        conn = self.get_connection()

        if conn:
            self.logger.info("Connection to the PostgreSQL established successfully.")
            cursor = conn.cursor()
            try:
                # Execute the query
                cursor.execute(query)
                # Fetch the results
                result = cursor.fetchall()
                # Return a set of results, if any
                return {item[0] for item in result} if result else set()
            except Exception as e:
                # Log the error, if any occurred
                self.logger.error(f"An error occurred while executing the query: {e}")
            finally:
                # Close the cursor, regardless of whether an error occurred or not
                cursor.close()
        else:
            # Log an error if the connection could not be established
            self.logger.error("Error establishing connection to the PostgreSQL.")

    def commit_changes(self, query):
        """
        Execute a query on the database and commit the changes.

        Args:
            query (str): The SQL query to be executed.
        """
        conn = self.get_connection()

        if conn:
            self.logger.info("Connection to the PostgreSQL established successfully.")
            cursor = conn.cursor()
            try:
                # Execute the query
                cursor.execute(query)
                # Commit the changes
                conn.commit()
            except Exception as e:
                # Log the error, if any occurred
                self.logger.error(f"An error occurred while committing changes: {e}")
            finally:
                # Close the cursor, regardless of whether an error occurred or not
                cursor.close()
        else:
            # Log an error if the connection could not be established
            self.logger.error("Error establishing connection to the PostgreSQL.")
