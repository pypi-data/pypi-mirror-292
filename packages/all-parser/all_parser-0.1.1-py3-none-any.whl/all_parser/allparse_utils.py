from all_parser.constants import supported_extensions
import os

def is_supported(file_path):
    '''
    Check if the file is supported by the parser.
    '''
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in supported_extensions:
        return False, (f"File {file_path} is not a supported"
                       f"file yet (Please check for newer relase "
                       f"and support).")
    return True, None