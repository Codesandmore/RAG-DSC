from pypdf import PdfReader
from io import BytesIO
import os

class PDFParser:
    def __init__(self, file:str|BytesIO):
        if not isinstance(file, (str, BytesIO)):
            raise TypeError("File argument must be a bytes object or a string.")
        
        if isinstance(file, str) and not file.lower().endswith('.pdf') :
            raise ValueError("Invalid file extension. Please provide a PDF file.")
        
        if isinstance(file, str):
            if not os.path.isfile(file) :
                raise FileNotFoundError(f"{file} does not exist. Please provide a valid file.")
        
        if isinstance(file, BytesIO):
            file.seek(0)
            if file.read(4) != b'%PDF':
                raise ValueError("Invalid PDF file.")
        
        self.file = file

    def extractText(self):
        reader = PdfReader(self.file)
        text = ""
        
        for page in reader.pages:
            text += page.extract_text()
        
        return text.strip()

