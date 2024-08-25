import PyPDF2


def parse(file_path):
    '''
    Common parse function, this parses pdf files.
    '''
    pdf_file = open(file_path, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_file)
    pdf_text = []
    for page_num in range(pdf_reader.numPages):
        page = pdf_reader.getPage(page_num)
        pdf_text.append(page.extract_text())
    pdf_file.close()
    return pdf_text