from pypdf import PdfReader
from io import BytesIO
import os
from spacy import Language
from langchain.text_splitter import RecursiveCharacterTextSplitter

class PDFParser:
    def __init__(self, file:str|BytesIO, nlp:Language, chunkSize:int=500, chunkOverlap = 100):
        """
        Initializes the PDFParser.

        Parameters:
        file (str|BytesIO): The file to be parsed.
        nlp (Language): An instance of a Spacy language model.
        chunkSize (int): The number of characters to include in each chunk.
        chunkOverlap (int): The number of characters to overlap between chunks.
        """
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
            
        if not issubclass(type(nlp), Language):
            raise TypeError("NLP argument must be a child of Spacy language model.")
        
        self.file = file
        self.nlp = nlp
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size = chunkSize,
            chunk_overlap = chunkOverlap,
            length_function = len,
            add_start_index = True
        )

    def extractText(self) -> str:
        """
        Extracts the text from the PDF file and returns it as a single string.

        Returns:
        str: The extracted text from the PDF file.
        """
        reader = PdfReader(self.file)
        text = ""
        
        for page in reader.pages:
            text += page.extract_text()
        
        return text.strip()
    
    def splitExtractedText(self, text:str) -> list[str]:
        """
        Splits the extracted text to chunks.

        Parameters:
        text (str): The extracted text to be split.
        
        Returns:
        list[str]: A list of chunks extracted from the input text.
        """
        chunks = self.splitter.split_text(text)
        
        return chunks
    
    def vectorize(self, text:str):
        """
        Vectorizes the input text using the Spacy language model.
        
        Parameters:
        text (str): The text to be vectorized.
        
        Returns:
        spacy.Floats1d: The vectorized representation of the input text. 
        """
        doc = self.nlp(text)
        return doc.vector
    
    def vectorizeDocument(self):
        """
        Vectorizes the entire document and returns a list of vectors.
        
        Returns:
        List[spacy.Floats1d]: A list of vectorized representations of the document.
        """
        text = self.extractText()
        chunks = self.splitExtractedText(text)
        vectors = [self.vectorize(chunk) for chunk in chunks]
        
        return vectors

