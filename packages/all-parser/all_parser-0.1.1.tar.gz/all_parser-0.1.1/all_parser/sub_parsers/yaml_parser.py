import yaml

def parse(file_path):
    '''
    Common parse function, this parses yaml files.
    '''
    with open(file_path, 'r') as f:
        return yaml.load(f, Loader=yaml.FullLoader)