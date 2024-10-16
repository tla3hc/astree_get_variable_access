import logging
import os
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from utils.astree_log_utils.variable_access import VariableAcces
import time

class LogFileHandler(FileSystemEventHandler):
    """Handler that triggers when log.txt is modified or created."""
    
    def __init__(self, log_file: str, output_directory:str) -> None:
        logging.info("LogFileHandler", "Init")
        self.astree_variable_access = VariableAcces()
        self.log_data = None
        self.log_file = log_file
        # Check if the log file exists
        if not os.path.exists(log_file):
            raise FileNotFoundError(f"File not found: {log_file}")
        self.output_directory = output_directory
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        pass
    
    def on_modified(self, event):
        if event.src_path == self.log_file:
            # self.__get_variable_access()
            logging.info("LogFileHandler", f"Log file: {self.log_file} modified")
            self.__read_log()
            
    def on_deleted(self, event):
        if event.src_path == self.log_file:
            logging.info("LogFileHandler", f"Log file: {self.log_file} deleted")
            self.__get_variable_access()

    def __copy_log(self):
        """Copy log.txt to the backup directory."""
        backup_file = os.path.join(self.backup_directory, 'log_backup.txt')
        shutil.copy2(self.log_file, backup_file)
        print(f"Backup updated: {backup_file}")
        
    def __read_log(self):
        """Read the log file and return the content."""
        with open(self.log_file, 'r', encoding='utf-8') as f:
            self.log_data = f.readlines()
        
    def __get_variable_access(self):
        """
        Retrieves the data range from the log file and writes it to a new file.

        This method uses the `astree_variable_access` object to get the data range
        from the specified log file. If the data range is successfully retrieved,
        it writes the data to a file named 'variable_access.txt' in the output directory.

        Returns:
            None
        """
        # Get the data range from the log file
        data_range_str = self.astree_variable_access.get_data_from_log(self.log_data)
        # Write the data range to a new file
        output_file = os.path.join(self.output_directory, 'variable_access.txt')
        if not data_range_str:
            # Create file empty variable access file
            with open(output_file, 'w', encoding='utf-8') as f:
                pass
        else:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(data_range_str)
        
class LogMonitor:
    
    def __init__(self, output_folder) -> None:
        logging.info("LogMonitor", "Init")
        self.astree_variable_access = VariableAcces()
        self.output_folder = output_folder
        self.removed_folder = []
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        pass
    
    def __find_log_file(self):
        """
        Searches for the log file in the user's temporary directory.
        This method attempts to locate a log file within a folder that starts with 'a3c-' 
        in the current user's temporary directory. It performs the following steps:
        1. Retrieves the current Windows user.
        2. Searches for folders starting with 'a3c-' in the user's temp directory.
        3. Checks if the log file is currently open by another process.
        4. If the log file is not open, it deletes the folder and adds it to the removed_folder list.
        5. If exactly one log file is found, it returns the path to the log file.
        6. Logs appropriate messages based on the outcome of the search.
        Returns:
            str: The path to the log file if found and only one log file is present.
            None: If no log file or more than one log file is found.
        """
        logging.info("VariableAcces", "Finding log file ...")
        # Get windows current user
        user = os.getlogin()
        # Try to search log file in the log folder
        log_folder = f'C:\\Users\\{user}\\AppData\\Local\\Temp'
        # Search and find folder start with 'a3c-'
        found_no = 0
        for folder in os.listdir(log_folder):
            if 'a3c-' in folder:
                current_folder = os.path.join(log_folder, folder)
                if current_folder in self.removed_folder:
                    continue
                txt_log_file = os.path.join(current_folder,'persistent', 'log.txt')
                log_file = os.path.join(current_folder,'persistent', 'astree.log')
                if not os.path.isfile(log_file):
                    continue
                else:
                    # Check if the log file is currently open by another process
                    try:
                        os.listdir(current_folder)
                        with open(log_file, 'r', encoding='utf-8') as f:
                            pass
                        # Try to rename current folder
                        shutil.move(current_folder, current_folder+'_')
                        # Rename folder back
                        shutil.move(current_folder+'_', current_folder)
                        # If nothing is hold the log file, delete the folder
                        shutil.rmtree(current_folder)
                        self.removed_folder.append(current_folder)
                        continue
                    except:
                        log_folder = os.path.join(log_folder, folder)
                        found_no += 1
                        continue
                    
                # Try to delete the folder, if could not delete, this is the log folder
                # try:
                #     shutil.rmtree(os.path.join(log_folder, folder))
                # except:
                #     log_folder = os.path.join(log_folder, folder)
                #     found_no += 1
                    # continue
        if found_no == 1:
            log_file = os.path.join(log_folder,'persistent', 'log.txt')
            if not os.path.isfile(log_file):
                logging.error("VariableAcces", "Log file does not exist")
                return None
            logging.info("VariableAcces", f"Log file found: {log_file}")
            return log_file
        else:
            logging.error("VariableAcces", f"ERROR: Different than one log file found: {found_no} file(s)")
            return None
    
    def __monitor(self, log_file):
        """
        Monitors the specified log file for specific content and processes it accordingly.
        This method continuously checks the log file for the presence of specific markers
        ("#data-dictionary:", "/* Result summary */", and "#shared memory usage:"). If the
        markers are found, it processes the log data and writes the variable access data to
        an output file. If the log file is incomplete or the markers are not found, it waits
        for a specified delay time before checking again.
        Args:
            log_file (str): The path to the log file to be monitored.
        Raises:
            FileNotFoundError: If the specified log file does not exist.
        """
        delay_time = 0
        while True:
            if delay_time > 0:
                # logging.info("LogMonitor", f"Log file is incomplete, waiting for {delay_time} seconds ...")
                time.sleep(delay_time)
            # Check if the log file exists
            if not os.path.exists(log_file):
                raise FileNotFoundError(f"File not found: {log_file}")
            # Read from the log file
            with open(log_file, 'r', encoding='utf-8') as f:
                log_data_list = f.readlines()
                log_data_str = '\n'.join(log_data_list)
            
            # logging.info("LogMonitor", f"len(log_data_list): {len(log_data_list)}")
            # logging.info("LogMonitor", log_data_str)
            if "#data-dictionary:" not in log_data_str:
                delay_time = 1
                continue
            elif "#data-dictionary:" in log_data_str and ("/* Result summary */" not in log_data_str or '#shared memory usage:' not in log_data_str):
                delay_time = 0.1
                continue
            else:
                variable_access_data = self.astree_variable_access.get_data_from_log(log_data_list)
                if variable_access_data:
                    variable_access_file = os.path.join(self.output_folder, 'variable_access.txt')
                    with open(variable_access_file, 'w', encoding='utf-8') as f:
                        f.write(variable_access_data)
                    return
    
    def monitor(self):
        """
        Monitors the log file for changes and handles the creation of a variable access file.
        This method performs the following steps:
        1. Logs the start of monitoring.
        2. Finds the log file to monitor.
        3. Logs an error and exits if the log file is not found.
        4. Ensures the output directory exists, creating it if necessary.
        5. Sets up a file system event handler for the log file.
        6. Starts an observer to watch for changes in the log file directory.
        7. Continuously checks for the existence of a 'variable_access.txt' file in the output directory.
        8. Stops the observer if the 'variable_access.txt' file is created or if a KeyboardInterrupt is received.
        Raises:
            KeyboardInterrupt: If the monitoring is interrupted by the user.
        """
        logging.info("LogMonitor", "Monitoring log file ...")
        output_directory = self.output_folder
        variable_access_file = os.path.join(output_directory, 'variable_access.txt')
        if os.path.exists(variable_access_file):
            os.remove(variable_access_file)
        # Find the log file to monitor for 30 seconds
        # Get current time stamp
        tic = time.time()
        while True:
            log_file = self.__find_log_file()
            if log_file:
                break
            time.sleep(3)
            toc = time.time()
            if toc - tic > 60:
                logging.error("LogMonitor", "Finding log file timeout")
                return
        
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
            
        logging.info("LogMonitor", "Waiting for the variable access data ...")
        self.__monitor(log_file)
        logging.info("LogMonitor", "Get variable access data successfully")
    
    