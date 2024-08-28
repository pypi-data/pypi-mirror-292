import socket
import json
import base64
import io
import os
import inspect
import mimetypes
import csv
import tempfile
# import zarr
import pandas as pd
import hashlib
import subprocess
from .git_utils import (
    is_git_repo,
    get_commit_hash,
    get_git_diff,
    get_remote_url,
    get_repo_name,
    get_current_branch,
    get_last_commit_message,
    get_last_commit_author,
    get_last_commit_date,
)

class Cherty:
    def __init__(self, host='127.0.0.1', port=1337):
        self.host = host
        self.port = port

        # Get the local path to the script file, which called this init function
        caller_frame = inspect.stack()[1]
        caller_filename = caller_frame.filename
        self.script_local_path = os.path.abspath(caller_filename)

        # Initialize git struct
        self.git_info = {
            'commit_hash': None,
            'diffs': None,
            'remote_url': None,
            'repo_name': None,
            'branch_name': None,
            'commit_message': None,
            'commit_author': None,
            'commit_date': None
        }

        # Find data about the current state of the repo
        if is_git_repo():
            self.git_info['commit_hash'] = get_commit_hash()
            self.git_info['diffs'] = get_git_diff()
            self.git_info['remote_url'] = get_remote_url()
            self.git_info['repo_name'] = get_repo_name(self.git_info['remote_url'])
            self.git_info['branch_name'] = get_current_branch()
            self.git_info['commit_message'] = get_last_commit_message()
            self.git_info['commit_author'] = get_last_commit_author()
            self.git_info['commit_date'] = get_last_commit_date()

        # Figure out what environment we're in and set variables
        environment = None
        environment_params = None
        if self.is_conda_environment():
            environment = 'conda'
            environment_params = self.export_conda_environment()
        # else:
        #     print("This script is not running in an Anaconda environment.")

        # Send details on the script
        message = {
            'msg_type': 'script',
            'script_local_path': self.script_local_path,
            'git_info': self.git_info,
            'environment': environment,
            'environment_params': environment_params,
            'protocol_name': 'poplar.network',
            'protocol_version': '1.0.0'
        }
        message_str = json.dumps(message)
        message_len = f"{len(message_str):<10}"
        self.send_message(message_len + message_str)

    # extension is optional; required to correctly interpret binary data
    def checkpoint(self, data, metadata, identifier, extension=None):

        # Figure out what type of data is being sent
        # local_is_temp is a flag to indicate if the file is temporary and should be deleted after sending
        data, data_type, local_path, local_is_temp = self.evaluate_data(data, extension)

        # Find the line number of the checkpoint call
        caller_frame = inspect.stack()[1]
        caller_line_number = caller_frame.lineno

        
        # The data is either (1) base64 encoded, so it can be sent as a string
        # or (2) a path to a file, so it can also be sent as a string
        message = {
            'msg_type': 'var_checkpoint',
            'data': data,
            'metadata': metadata,
            'identifier': identifier,
            'localPath': local_path if 'local_path' in locals() else None,
            'localIsTemp': local_is_temp,
            'dataType': data_type,
            'extension': extension,
            'script_local_path': self.script_local_path,
            'checkpoint_line_number': caller_line_number,
            'commit_hash': self.git_info['commit_hash']
        }

        # Convert the message to a JSON string
        message_str = json.dumps(message)

        # Prefix with the length of the message
        message_len = f"{len(message_str):<10}"  # Fixed-width length field

        print('sending checkpoint message')

        # Send the length-prefixed message
        self.send_message(message_len + message_str)
        
    
    def send_message(self, message):
        message_json = json.dumps(message)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((self.host, self.port))
            client_socket.sendall(message_json.encode('utf-8'))
        finally:
            client_socket.close()

    def evaluate_data(self, data, extension):

        # Check if data is a path to a file. In this case, transmit the path over IPC
        try:
            possible_path = os.path.abspath(data)
            if os.path.isfile(possible_path):
                mime_type, _ = mimetypes.guess_type(possible_path)
                return (data, mime_type or 'binary', possible_path, False)
        except Exception as e:
            # print(f"Error in evaluating data as file path: {e}")
            pass

        # Convert dict to JSON string if data is a dictionary
        # Send directly if below 100 MB, otherwise send as a temp file
        if isinstance(data, dict):
            data = json.dumps(data)
            data_type = 'application/json'
            size_in_bytes = len(data.encode('utf-8'))
            data, local_path, is_temp = self.size_switch(size_in_bytes, data, '.json')
            return (data, data_type, local_path, is_temp)
        
        # For xarray datasets, save as temporary Zarr file
        elif hasattr(data, 'to_zarr'):
            data, data_type, local_path, is_temp = self.store_as_netcdf(data)
            return (data, data_type, local_path, is_temp)
        
        # Check if data is bytes
        elif isinstance(data, bytes):
            data_type = 'application/octet-stream'
            size_in_bytes = len(data)
            data, local_path, is_temp = self.size_switch(size_in_bytes, data, '.bin')
            return (data, data_type, local_path, is_temp)
        # If it's a pandas df, convert to a csv string
        elif isinstance(data, pd.DataFrame):
            data = data.to_csv(index=False)
        
        # Check if data is a string and try to identify the type
        try:
            if isinstance(data, str):
                # Check if it's a valid JSON
                try:
                    parsed_data = json.loads(data)
                    return self.evaluate_data(parsed_data, '.json')
                except json.JSONDecodeError:
                    pass

                # Check if it's a CSV by trying to parse the first few lines
                try:
                    # A CSV should have multiple rows and columns, so we do a more thorough check
                    dialect = csv.Sniffer().sniff(data)
                    # Split the data into lines and check if it has multiple lines with the delimiter
                    lines = data.splitlines()
                    if len(lines) > 1 and all(dialect.delimiter in line for line in lines):
                        size_in_bytes = len(data)
                        data_type = 'text/csv'
                        data, local_path, is_temp = self.size_switch(size_in_bytes, data, '.csv')
                        return (data, data_type, local_path, is_temp)
                except csv.Error:
                    pass
                
                # Default to plain text
                size_in_bytes = len(data)
                data, local_path, is_temp = self.size_switch(size_in_bytes, data, '.txt')
                data_type = 'text/plain'
                return (data, data_type, local_path, is_temp)
        except Exception as e:
            print(f"Error in evaluating data type: {e}")
        
        try:
            data_as_bytes = bytes(data, 'utf-8')
            return self.evaluate_data(data_as_bytes, extension)
        except:
            pass
        return (data, None, None, None)

    def size_switch (self, size_in_bytes, data, extension):
        if size_in_bytes < 75 * 1024 * 1024:  # 75 MB
            if isinstance(data, (bytes, bytearray)):
                data = base64.b64encode(data).decode('utf-8') # Convert to base64 so it can be sent as ASCII
            local_path = None
            is_temp = False
        else:
            local_path = self.save_temp_data(data, extension)
            data = None
            is_temp = True
        return (data, local_path, is_temp)

    def save_temp_data(self, data, extension):

        # Create a temporary file that won't be deleted automatically
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=extension)
        try:
            if not isinstance(data, (bytes, bytearray)):
                data = data.encode('utf-8') 
            temp_file.write(data)
            temp_file_path = temp_file.name  # Get the path to the file
            # print(f"Temporary file created at: {temp_file_path}")
        finally:
            temp_file.close()  # Close the file, but it won't be deleted

        return temp_file_path


    def store_as_netcdf(self, data):
        # Create a named temporary file with .nc extension and ensure it is not deleted automatically
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.nc')
        
        try:
            # Save the xarray Dataset to NetCDF format
            data.to_netcdf(temp_file.name)

            # Calculate the hash of the file
            with open(temp_file.name, 'rb') as f:
                file_data = f.read()
                data_hash = hashlib.sha256(file_data).hexdigest()
            # print(f"Data SHA-256 Hash: {data_hash}")

            # Save the path of the temporary file
            temp_file_path = temp_file.name
            # print(f"Temporary file created at: {temp_file_path}")
        finally:
            temp_file.close()  # Close the file, but it won't be deleted

        # Return metadata for further use
        data = None
        data_type = 'application/x-netcdf'
        local_path = temp_file_path
        is_temp = True
        return (data, data_type, local_path, is_temp)

    def is_conda_environment(self):
        return 'CONDA_PREFIX' in os.environ

    def export_conda_environment(self):
        try:
            # Run the conda list command and capture the output
            result = subprocess.run(["conda", "list", "--explicit"], capture_output=True, text=True, check=True)
            # Split the output into a list of lines
            # conda_env_list = result.stdout.splitlines()
            return result.stdout
        except subprocess.CalledProcessError as e:
            print("Failed to export the conda environment details:", e)
            return None
