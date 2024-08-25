import xml.etree.ElementTree as ET

def parse(file_path):
    '''
    Common parse function, this parses xml files.
    '''
    tree = ET.parse(file_path)
    root = tree.getroot()
    return root    