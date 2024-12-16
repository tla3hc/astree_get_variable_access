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
    
    def validate_variable_data(self, log_data: str) -> bool:
        """
        Validates the format of the given log data string.

        The log data string is expected to follow a specific format, for example:
        "[23:44:04] #  ADC_AXF_p_EnaPlausBlndLgtF_b of type const boolean in [0, 1]"

        This method checks if the log data contains the substrings "of type", "in", and "#".

        Args:
            log_data (str): The log data string to validate.

        Returns:
            bool: True if the log data string is in the expected format, False otherwise.
        """
        # log_data example:
        # "[23:44:04] #  ADC_AXF_p_EnaPlausBlndLgtF_b of type const boolean in [0, 1]""
        # strip the log_data
        log_data = log_data.strip()
        if "of type" in log_data and "in" in log_data and "#" in log_data:
            return True
        return False
    
    def get_variable_name(self, log_data: str) -> str:
        """
        Extracts the variable name from a given log data string.

        Args:
            log_data (str): The log data string containing the variable information.

        Returns:
            str: The extracted variable name.
        """
        variable_name = log_data.split("of type")[0].strip()
        variable_name = variable_name.split("#")[1].strip()
        return variable_name
    
    def get_variable_range(self, log_data: str) -> str:
        """
        Extracts and returns the variable range from the provided log data.

        Args:
            log_data (str): The log data string containing the variable range.

        Returns:
            str: The extracted variable range.
        """
        variable_range = log_data.split("in")[1].strip()
        return variable_range
    
    def get_variable_type(self, log_data: str) -> str:
        """
        Extracts and returns the variable type from the given log data string.

        Args:
            log_data (str): The log data string containing the variable type information.

        Returns:
            str: The extracted variable type.
        """
        variable_type = log_data.split("of type")[1].split("in")[0].strip()
        return variable_type
        
    def get_variable_data(self, log_data: str) -> list:
        """
        Extracts variable data from the provided log data.

        Args:
            log_data (str): The log data containing variable information.

        Returns:
            list: A list containing the variable name, type, and range if the log data is valid.
                  Returns None if the log data is invalid.
        """
        # validate the log data
        if not self.validate_variable_data(log_data):
            return None
        # get the variable name
        variable_name = self.get_variable_name(log_data)
        # get the variable type
        variable_type = self.get_variable_type(log_data)
        # get the variable range
        variable_range = self.get_variable_range(log_data)
        return [variable_name, variable_type, variable_range]
    
    def is_float(self, value: str) -> bool:
        """_summary_
        Check if given string can be converted to a float.
        Args:
            value (str): _description_

        Returns:
            bool: _description_
        """
        try:
            if not value:
                return False
            # Lowercase the value
            value = value.lower()
            if "nan" in value or "inf" in value:
                return False
            float(value)
            return True
        except ValueError:
            return False
    
    def get_range_values(self, variable_range: str) -> str:
        """
        Extracts the minimum and maximum values from the given variable range.

        Args:
            variable_range (str): The variable range string.

        Returns:
            list: A str containing the minimum and maximum values.
        """
        try:
            # Validate range
            if not variable_range:
                return None
            # Range in the format [0, 1]
            if "[" in variable_range and "]" in variable_range:
                # Get lower and upper ranges
                upper_range = variable_range.split(",")[1].replace("]", "").strip()
                lower_range = variable_range.split(",")[0].replace("[", "").strip()
                # Check if the values are floats
                if self.is_float(upper_range) and self.is_float(lower_range):
                    return f'{float(lower_range)}..{float(upper_range)}'
                else:
                    return None
            # Variable range is in "{40} /\ != 0"
            elif "{" in variable_range and "}" in variable_range:
                # The value between the curly braces is the range and should be a float
                range_value = variable_range.split("{")[1].split("}")[0].strip()
                if self.is_float(range_value):
                    return f'{float(range_value)}..{float(range_value)}'
                else:
                    return None
            return None
        except Exception as ex:
            logging.debug("VariableAcces", f"Error: {ex}")
            return None
        
    def get_variable_access_obj(self, log_data_list: list) -> dict:
        """
        Extracts variable data from a given log data list.

        Args:
            log_data (list): A list of strings containing log data.

        Returns:
            dict: A dictionary containing the variable name as the key and the variable data as the value.
        """
        logging.info("VariableAcces", "Getting variable access object ...")
        variable_access_obj = {}
        for log_data in log_data_list:
            variable_data = self.get_variable_data(log_data)
            if variable_data:
                variable_name = variable_data[0]
                variable_type = variable_data[1]
                variable_range = variable_data[2]
                # check if the variable name already exists in the variable access object
                if variable_name in variable_access_obj:
                    continue
                # Validate the variable range and get the min and max values
                variable_range = self.get_range_values(variable_range)
                if not variable_range:
                    continue
                new_data = {}
                new_data["type"] = variable_type
                new_data["range"] = variable_range
                variable_access_obj[variable_name] = new_data
        return variable_access_obj
    
    def write_variable_access_to_csv(self, variable_access_obj: dict, output_file: str) -> None:
        """
        Writes the variable access object to a CSV file.

        Args:
            variable_access_obj (dict): A dictionary containing variable data.
            output_file (str): The path to the output CSV file.
        """
        logging.info("VariableAcces", "Writing variable access to CSV ...")
        if os.path.exists(output_file):
            os.remove(output_file)
        with open(output_file, "w") as csv_file:
            csv_file.write("Variable Name,Variable Type,Variable Range\n")
            for variable_name, variable_data in variable_access_obj.items():
                variable_type = variable_data["type"]
                variable_range = variable_data["range"]
                csv_file.write(f"{variable_name},{variable_type},{variable_range}\n")
    
    def save_variable_access_to_csv(self, log_data_list: list, output_file: str) -> None:
        """
        Converts a log file containing variable data to a CSV file.

        Args:
            log_data (list): A list of strings containing log data.
            output_file (str): The path to the output CSV file.
        """
        logging.info("VariableAcces", "Converting variable data to CSV ...")
        variable_access_obj = self.get_variable_access_obj(log_data_list)
        self.write_variable_access_to_csv(variable_access_obj, output_file)