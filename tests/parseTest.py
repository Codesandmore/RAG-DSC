import unittest
from src.parsing import PDFParser
from io import BytesIO
import spacy

model = "en_core_web_sm"
# change this to tranformer model when deploying 

expecetdVectorShape = 96
# shape of the vector generated by the spacy model

class TestParser(unittest.TestCase):
    nlp = spacy.load(model)
    def test_parser_init(self):
        """
        This method tests if the parser is initialized properly.
        """
        invalidPath = "tests/files/hello.txt"
        validPath = "tests/files/hello.pdf"
        filePath = "tests/files/testFIle.pdf"

        with self.assertRaises(ValueError):
            PDFParser(invalidPath, self.nlp)

        with self.assertRaises(FileNotFoundError):
            PDFParser(validPath, self.nlp)

        with self.assertRaises(TypeError):
            PDFParser(5, self.nlp)

        with open(invalidPath, 'rb') as f:
            b = BytesIO(f.read())
            with self.assertRaises(ValueError):
                PDFParser(b, self.nlp)

        PDFParser(filePath, self.nlp)
        
        with open(filePath, "rb") as f:
            b = BytesIO(f.read())
            PDFParser(b, self.nlp)

        with self.assertRaises(TypeError):
            PDFParser(filePath, 50)

    def test_extract(self):
        """
        Tests if the parser is able to extract text.
        """
        filePath = "tests/files/testFIle.pdf"
        parser = PDFParser(filePath, self.nlp)
        extractedText = parser.extractText()

        self.assertEqual(extractedText, "This is a test pdf file.")

    def test_split(self):
        """
        Tests if the splitting method is working properly.
        """
        filePaths = "tests/files/testFIle.pdf", "tests/files/ml_guide.pdf"
        for filePath in filePaths:
            parser = PDFParser(filePath, self.nlp)
            extractedText = parser.extractText()
            splitText = parser.splitExtractedText(extractedText)

            for text in splitText:
                self.assertLessEqual(len(text), 500)

    def test_vectorization(self):
        """
        Tests if the vectorization method is working properly.
        """
        filePaths = "tests/files/testFIle.pdf", "tests/files/ml_guide.pdf"
        for filePath in filePaths:
            parser = PDFParser(filePath, self.nlp)
            extractedText = parser.extractText()
            splitText = parser.splitExtractedText(extractedText)
            for text in splitText:
                vectors = parser.vectorize(text)
                self.assertIsNotNone(vectors)
                self.assertEqual(len(vectors), expecetdVectorShape)

    def test_document_vectorization(self):
        """
        Tests if the vectorization of a document is working properly.
        """
        filePaths = "tests/files/testFIle.pdf", "tests/files/ml_guide.pdf"
        for filePath in filePaths:
            parser = PDFParser(filePath, self.nlp)
            vectors = parser.vectorizeDocument()
            
            self.assertIsNotNone(vectors)
            for vector in vectors:
                self.assertEqual(len(vector), expecetdVectorShape)        