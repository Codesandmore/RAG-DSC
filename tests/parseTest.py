import unittest
from src.parsing import PDFParser
from io import BytesIO

class TestParser(unittest.TestCase):
    def test_parser_init(self):
        invalidPath = "tests/files/hello.txt"
        validPath = "tests/files/hello.pdf"
        filePath = "tests/files/testFIle.pdf"

        with self.assertRaises(ValueError):
            PDFParser(invalidPath)

        with self.assertRaises(FileNotFoundError):
            PDFParser(validPath)

        with self.assertRaises(TypeError):
            PDFParser(5)

        with open(invalidPath, 'rb') as f:
            b = BytesIO(f.read())
            with self.assertRaises(ValueError):
                PDFParser(b)

        parser = PDFParser(filePath)
        
        with open(filePath, "rb") as f:
            b = BytesIO(f.read())
            parser = PDFParser(b)

    def test_extract(self):
        filePath = "tests/files/testFIle.pdf"
        parser = PDFParser(filePath)
        extractedText = parser.extractText()

        self.assertEqual(extractedText, "This is a test pdf file.")