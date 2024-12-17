import os
import logging

class LinkVar2Sim:
    m_var_data = {}
    m_source_c = ""
    m_used_variables = []
    m_linked_data = {}
    
    def __init__(self) -> None:
        logging.info("LinkVar2Sim", "Init")
        pass
    
    def validate_file_path(self, file_path: str) -> bool:
        logging.debug("LinkVar2Sim", "Validating file path")
        if not file_path:
            return False
        if os.path.exists(file_path):
            return True
        else:
            return False
    
    def get_simulink_path(self):
        logging.debug("LinkVar2Sim", "Getting Simulink path")
        for var in self.m_used_variables:
            if f'"{var} = "' in self.m_source_c:
                pass
            
    def get_comment_block_in_c_code(self, variable: str) -> str:
        '''
        Get comment block in C code above the given line
        '''
        logging.debug("LinkVar2Sim", "Getting comment block in C code")
        comment_block = ''
        source_c_lines = self.m_source_c.split('\n')
        for i, line in enumerate(source_c_lines):
            if f' {variable} = ' in line and line.strip().startswith(variable):
                for j in range(i-1, -1, -1):
                    if '/*' in source_c_lines[j]:
                        first_comment_block = source_c_lines[j].strip()
                        # Get comment block end with space
                        for k in range(j, len(source_c_lines), 1):
                            # print(source_c_lines[k])
                            # print(repr(source_c_lines[k]))
                            if '#' in source_c_lines[k] or "*/" in source_c_lines[k]:
                                if comment_block == '':
                                    return first_comment_block
                                return comment_block
                            else :
                                comment_block += source_c_lines[k].strip()
                    else:
                        continue
        return comment_block
    
    def get_used_variables(self) -> list:
        '''Return list of used variables in source C file'''
        logging.debug("LinkVar2Sim", "Used variables")
        for var in self.m_var_data:
            if f'{var} = ' in self.m_source_c:
                # Check if the line.strip is start with variable name
                for line in self.m_source_c.split('\n'):
                    if f'{var} = ' in line:
                        if line.strip().startswith(var):
                            self.m_used_variables.append(var)
    
    def save_linked_variables(self, output_folder: str) -> None:
        # Save to CSV file
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        if os.path.exists(f"{output_folder}/linked_variables.csv"):
            os.remove(f"{output_folder}/linked_variables.csv")
        with open(f"{output_folder}/linked_variables.csv", 'w') as f:
            for var in self.m_linked_data:
                f.write(f"{var.strip()},{self.m_linked_data[var][0][0].strip()},{self.m_linked_data[var][0][1].strip()},{self.m_linked_data[var][1].strip()}\n")
        logging.info("LinkVar2Sim", "Saved linked variables to CSV file")
        
    def link(self, source_c_path: str, variable_csv_path: str, output_folder: str) -> None:
        logging.info("LinkVar2Sim", "Linking")
        # Check input file paths
        if not self.validate_file_path(source_c_path):
            logging.error("LinkVar2Sim", "Invalid source C file path")
            return
        if not self.validate_file_path(variable_csv_path):
            logging.error("LinkVar2Sim", "Invalid variable CSV file path")
            return
        # Read variable CSV file
        with open(variable_csv_path, 'r') as f:
            lines = f.readlines()
        # Extract variable 
        for line in lines:
            variable_name = line.split(',')[0]
            if "@" in variable_name:
                variable_name = variable_name.split("@")[0]
            variable_type = line.split(',')[1]
            variable_value = line.split(',')[2]
            logging.debug("LinkVar2Sim", f"Extracted variable: {variable_name}")
            new_var_data = {variable_name: (variable_type, variable_value)}
            # Add to dictionary
            self.m_var_data.update(new_var_data)
        # Read source C file
        with open(source_c_path, 'r') as f:
            self.m_source_c = f.read()
        
        self.get_used_variables()
        logging.info("LinkVar2Sim", f"Used variables: {self.m_used_variables}")
        
        for var in self.m_used_variables:
            this_comment_block = self.get_comment_block_in_c_code(var)
            logging.debug("LinkVar2Sim", f"Comment block: {this_comment_block}") 
            self.m_linked_data.update({var: (self.m_var_data[var], this_comment_block)})
        
        logging.info("LinkVar2Sim", "Linking completed")
        self.save_linked_variables(output_folder)
        logging.info("LinkVar2Sim", "Saved linked variables")
    

# include utils folder in sys.path
import sys
sys.path.append(r"C:\Users\trand\Desktop\Bosch\astree_get_variable_access\utils")
from log import Logger
import click
import logging

@click.command()
@click.option('--source_c_path', prompt='Source C path', help='Source C path')
@click.option('--variable_access_csv_path', prompt='Variable access csv path', help='Variable access csv path')
@click.option('--output_folder', prompt='Output folder path', help='Output folder path')
def main(source_c_path, variable_access_csv_path, output_folder):
    logger = Logger()
    if not source_c_path:
        logging.error("main", "Source C path is required")
        return
    if not variable_access_csv_path:
        logging.error("main", "Variable access csv path is required")
        return
    if not output_folder:
        logging.error("main", "Output folder path is required")
        return
    link_var2sim = LinkVar2Sim()
    link_var2sim.link(source_c_path, variable_access_csv_path, output_folder)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error("main", str(e))
