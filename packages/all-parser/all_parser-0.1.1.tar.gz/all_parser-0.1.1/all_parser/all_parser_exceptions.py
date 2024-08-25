class UnsupportedExtensionError(Exception):
    def __init__(self, file):
        self.file = file
        self.message = (f"File {file} is not a supported file yet "
                        f"(Please check for newer relase and support).")
        super().__init__(self.message)

class FileAlreadyExistsError(Exception):
    def __init__(self, file):
        self.file = file
        self.message = f"File {file} already exists."
        super().__init__(self.message)

class UnknownFormatError(Exception):
    def __init__(self, file):
        self.file = file
        self.message = f"Could not parse {file}."
        super().__init__(self.message)