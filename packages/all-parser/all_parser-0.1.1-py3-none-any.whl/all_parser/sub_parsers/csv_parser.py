import csv

def parse(file_path):
    '''
    Common parse function, this parses csv files.
    '''
    with open(file_path, 'r') as f:
        return list(csv.reader(f))