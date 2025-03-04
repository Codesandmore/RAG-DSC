import os
import numpy as np
from pypdf import PdfReader
from io import BytesIO
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

class PDFVectorizer:
    def __init__(self, model_name="all-MiniLM-L6-v2", chunk_size=500, chunk_overlap=100):
        """
        Initializes the PDFVectorizer.

        Parameters:
        model_name (str): The name of the sentence-transformers model.
        chunk_size (int): The number of characters in each chunk.
        chunk_overlap (int): Overlapping characters between chunks.
        """
        self.model = SentenceTransformer(model_name)
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    def extract_text(self, file_path: str) -> str:
        """Extracts text from a PDF file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        reader = PdfReader(file_path)
        text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
        return text.strip()

    def split_text(self, text: str) -> list[str]:
        """Splits extracted text into chunks."""
        return self.splitter.split_text(text)

    def vectorize_text(self, text_chunks: list[str]) -> np.ndarray:
        """Generates embeddings for text chunks."""
        return self.model.encode(text_chunks)

    def process_pdf(self, file_path: str, save_path="sentence_embeddings.npy"):
        """Extracts, splits, vectorizes text, and saves embeddings."""
        text = self.extract_text(file_path)
        chunks = self.split_text(text)
        embeddings = self.vectorize_text(chunks)
        np.save(save_path, embeddings)
        print(f"Saved embeddings to {save_path}")

if __name__ == "__main__":
    pdf_path = "tests/files/ml_guide.pdf"  # Adjust path if needed
    vectorizer = PDFVectorizer()
    vectorizer.process_pdf(pdf_path)
