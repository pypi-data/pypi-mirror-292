from __future__ import annotations

import csv
import logging
import os

import pandas as pd
import yaml

from transfer_agents.commons import setupLogging

# import Classes


class TransferFile:
    def __init__(
        self,
        default_config: str = "../config/sample.yaml",
        csv_file: str = None,
    ):
        """
        Initializes TransferFile instance.

        Args:
            default_config (str, optional): The file path to the YAML configuration file. Defaults to '../config/sample.yaml'.
            csv_file (str, optional): The file path to the CSV file to validate.
        """

        self.setup_logger(default_config)  # Set up the logger
        self.load_config(default_config)  # Load the YAML configuration file
        self.csv_file = csv_file

    def setup_logger(self, default_config):
        """
        Configures the logger for the TransferFile class.

        Args:
            default_config (str): The file path to the YAML configuration file for the logger.
        """
        # Configure the message logging format
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        # Create a logger for the TransferFile class
        self.logger = logging.getLogger("TransferFile")
        # Configure the logger with the YAML configuration file
        setupLogging(default_config)

    def load_config(self, default_config):
        """
        Loads the database configuration from a YAML file.

        Args:
            default_config (str): The file path to the YAML configuration file.
        """
        DEFAULT_CONFIG_FILE = "../config/sample.yaml"

        # Check if the provided configuration file is different from the default one
        if default_config != DEFAULT_CONFIG_FILE:
            if os.path.exists(default_config):
                with open(default_config) as f:
                    self.config = yaml.safe_load(f)
                    f.close()
                    if "psql" not in self.config:
                        raise ValueError("'psql' not found in the configuration file")
            else:
                self.logger.warning(
                    f"Configuration file '{default_config}' not found. Using default configuration file.",
                )
                with open(DEFAULT_CONFIG_FILE) as f:
                    self.config = yaml.safe_load(f)
                    f.close()
        else:
            with open(DEFAULT_CONFIG_FILE) as f:
                self.config = yaml.safe_load(f)
                f.close()

    def validate_csv(self):
        """
        Validates the structure of a CSV file.

        Returns:
            list: A list representing the row of the CSV file if the structure is valid, None otherwise.
        """
        if self.csv_file is None:
            self.logger.error("No CSV file provided.")
            return None

        try:
            # Open the CSV file in read mode
            with open(self.csv_file) as file:
                # Create a CSV reader object
                reader = csv.reader(file, delimiter=" ")
                line_number = 0
                for row in reader:
                    line_number += 1
                    # Check if the number of columns is not equal to 3
                    if len(row) != 3:
                        raise ValueError(
                            f"Line {line_number} does not have the correct structure.",
                        )
            # Return None if all lines have correct structure
            return None
        except FileNotFoundError:
            self.logger.error("The specified file was not found.")
            return None
        except Exception as e:
            self.logger.error(f"An error occurred while reading the file: {e}")
            return None

    def get_csv_data(self):
        """
        Reads the CSV file and returns its content as a DataFrame.

        Returns:
            DataFrame: A DataFrame containing the data from the CSV file.
        """
        try:
            df = pd.read_csv(self.csv_file, delimiter=" ", header=None)
            return df
        except FileNotFoundError:
            self.logger.error("The specified file was not found.")
            return None
        except Exception as e:
            self.logger.error(f"An error occurred while reading the file: {e}")
            return None


# Example usage
if __name__ == "__main__":
    default_config = "../config/logging.yaml"  # Specify the logger configuration file
    csv_file = input("Enter the path to the CSV file: ")  # Prompt for the CSV file path
    transfer_file = TransferFile(
        default_config=default_config,
        csv_file=csv_file,
    )  # Create an instance of TransferFile
    csv_structure = (
        transfer_file.validate_csv()
    )  # Validate the structure of the CSV file
    if csv_structure:
        print("CSV file structure validated successfully:")
        print(csv_structure)
