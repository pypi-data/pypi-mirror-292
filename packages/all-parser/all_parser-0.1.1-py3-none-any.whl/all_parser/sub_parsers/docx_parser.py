from docx import Document

def parse(file_path):
    '''
    Common parse function, this parses docx files.
    '''
    doc = Document(file_path)
    return [p.text for p in doc.paragraphs]