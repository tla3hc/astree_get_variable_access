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
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        pass
    
    def __find_log_file(self):
        """
        Searches for the log file in the user's temporary directory.
        This method attempts to locate a log file within a specific folder structure
        in the user's temporary directory. It performs the following steps:
        1. Retrieves the current user's username.
        2. Searches for folders starting with 'a3c-' in the user's temporary directory.
        3. Attempts to delete these folders; if deletion fails, assumes the folder contains the log file.
        4. Checks for the existence of 'log.txt' within the identified folder.
        Returns:
            str: The path to the log file if found and only one folder matches the criteria.
            None: If the log file does not exist or if more than one matching folder is found.
        Logs:
            - Info: When starting the search for the log file.
            - Error: If the log file does not exist.
            - Info: If the log file is found.
            - Error: If more than one matching folder is found.
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
        delay_time = 0
        while True:
            if delay_time > 0:
                logging.info("LogMonitor", f"Log file is incomplete, waiting for {delay_time} seconds ...")
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
                delay_time = 3
                continue
            elif "#data-dictionary:" in log_data_str and ("/* Result summary */" not in log_data_str or '#shared memory usage:' not in log_data_str):
                delay_time = 0.3
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
            time.sleep(5)
            toc = time.time()
            if toc - tic > 60:
                logging.error("LogMonitor", "Finding log file timeout")
                return
        
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
            
        # event_handler = LogFileHandler(log_file, output_directory)
        # observer = Observer()
        # observer.schedule(event_handler, path=os.path.dirname(log_file), recursive=False)
        # observer.start()
        
        # try:
        #     while True:
        #         # Check if the variable access file exists
        #         if os.path.exists(os.path.join(output_directory, 'variable_access.txt')):
        #             logging.info("LogMonitor", "#"*100)
        #             logging.info("LogMonitor", f"Variable access file created: {os.path.join(output_directory, 'variable_access.txt')}")
        #             logging.info("LogMonitor", "#"*100)
        #             # Stop the observer
        #             observer.stop()
        #             break
        # except KeyboardInterrupt:
        #     observer.stop()
        # observer.join()
        
        # # Check if the variable access file is empty
        # if os.path.exists(variable_access_file):
        #     with open(variable_access_file, 'r', encoding='utf-8') as f:
        #         data = f.read()
        # if data == "":
        #     logging.error("LogMonitor", "Variable access file is empty")
        #     os.remove(variable_access_file)
        
        self.__monitor(log_file)
    
    