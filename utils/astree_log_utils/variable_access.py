import logging
import os

class VariableAcces:
    
    def __init__(self) -> None:
        logging.info("VariableAcces", "Init")
        pass
    
    def get_data_from_log(self, log_data: list) -> str:
        """
        Extracts data from a log file based on specific markers.

        This method processes a list of log lines to find and extract a block of data
        that is located between the markers '#data-dictionary:' and either '#shared memory usage:'
        or '#ALARM'. If the log data is empty or the markers are not found, appropriate actions
        are taken.

        Args:
            log_data (list): A list of strings representing lines from a log file.

        Returns:
            str: A string containing the extracted data block if found, otherwise None.

        Raises:
            FileNotFoundError: If the log data is empty.
        """
        logging.info("VariableAcces", "Getting data from log file ...")
        # Check if the log data exists
        if len(log_data) == 0:
            raise FileNotFoundError(f"Log data is empty")
        data_range = []
        lines = log_data
        # Find the line that contains the data range
        is_in_data_range_block = False
        for line in lines:
            if '#data-dictionary:' in line and not is_in_data_range_block:
                is_in_data_range_block = True
                continue
            elif is_in_data_range_block and '#shared memory usage:' in line:
                data_range_str = '\n'.join(data_range)
                return data_range_str
            elif is_in_data_range_block and '#ALARM' in line:
                data_range_str = '\n'.join(data_range)
                return data_range_str
            elif is_in_data_range_block:
                data_range.append(line)
        return None
    