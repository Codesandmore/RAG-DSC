import unittest
from src.parsing import PDFParser
from io import BytesIO
import spacy

model = "en_core_web_sm"
# change this to tranformer model when deploying 

class TestParser(unittest.TestCase):
    nlp = spacy.load(model)
    def test_parser_init(self):
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
        filePath = "tests/files/testFIle.pdf"
        parser = PDFParser(filePath, self.nlp)
        extractedText = parser.extractText()

        self.assertEqual(extractedText, "This is a test pdf file.")

    def test_split(self):
        filePaths = "tests/files/testFIle.pdf", "tests/files/ml_guide.pdf"
        for filePath in filePaths:
            parser = PDFParser(filePath, self.nlp)
            extractedText = parser.extractText()
            splitText = parser.splitExtractedText(extractedText)

            for text in splitText:
                self.assertLessEqual(len(text), 500)

        