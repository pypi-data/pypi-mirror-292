import os
from all_parser.constants import supported_extensions
from all_parser.allparse_utils import is_supported
from all_parser.sub_parsers import json_parser, yaml_parser, xml_parser
from all_parser.sub_parsers import csv_parser, pdf_parser, docx_parser
from all_parser.all_parser_exceptions import *

class AllParse():
    def __init__(self, file_path, type=None, try_all=False):
        self.file_path = file_path
        self.extension = os.path.splitext(file_path)[1].lower()
        if type:
            self.extension = f'.{type}'
        if self.extension == '':
            self.extension = None
        if try_all:
            self.extension = None
        self.resolve_synonyms()
        self.check_file()
        self.parse()

    def resolve_synonyms(self):
        '''
        Resolve synonyms for the extensions
        '''
        synonyms = {
            '.yml': '.yaml',
            '.xlsx': '.csv',
            '.xls': '.csv',
            '.doc': '.docx',
        }
        if self.extension in synonyms:
            self.extension = synonyms[self.extension]

    def check_file(self):
        '''
        Check if the file exists, is a file, has read permission,
        is not empty, and has a valid extension.
        '''
        file_checks = {
            'exists': {'method': os.path.exists,
                       'args': [self.file_path],
                       'exception': FileNotFoundError},
            'read_permission': {'method': os.access,
                                'args': [self.file_path, os.R_OK],
                                'exception': PermissionError},
            'supported_extension': {'method': is_supported,
                                    'args': [self.file_path],
                                    'exception': UnsupportedExtensionError},
        }

        for _, check_dict in file_checks.items():
            if not check_dict['method'](*check_dict['args']):
                raise check_dict['exception'](self.file_path)
        return True, None
    def write_output(self, output):
        '''
        Write the output to the file.
        '''
        if self.parsed_obj:
            with open(output, 'w') as f:
                f.write(str(self.parsed_obj))
        else:
            raise UnknownFormatError(self.file_path)
    
    def print_parsed(self):
        '''
        Print the parsed object.
        '''
        if self.parsed_obj:
            print(self.parsed_obj)
        else:
            raise UnknownFormatError(self.file_path)

    def parse(self):
        '''
        :param output: if output is defined, its extension is honored,
                       if the input file data cannot be stored as the
                       required extension, parser fails.
        Try to parse,
        1. Based on extension we've got
        2. Try to parse with all types if no extension is found
        3. Give suggestion for the type if extension isn't parsing
           but other file type load passes(to be implemented)
        '''
        if not self.extension:
            for ext in supported_extensions:
                self.extension = ext
                try:
                    self.parsed_obj = globals()\
                        [f'{ext[1:]}_parser'].parse(self.file_path)
                except:
                    self.parsed_obj = None
                if self.parsed_obj:
                    return
            raise UnknownFormatError(self.file_path)
        else:
            self.parsed_obj = globals()\
                [f'{self.extension[1:]}_parser'].parse(self.file_path)
            return