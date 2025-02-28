# PDFParser Class Documentation

## Overview

The `PDFParser` class is responsible for extracting, processing, and vectorizing text from a PDF file. Text vectorization transforms textual data into numerical representations, enabling advanced natural language processing tasks such as similarity analysis and machine learning applications. It leverages `pypdf` for text extraction, `spaCy` for natural language processing, and `langchain` for splitting extracted text into manageable chunks.

## Dependencies

- `pypdf.PdfReader`: Used to read and extract text from PDF files.
- `spaCy.Language`: A natural language processing model for tokenization and vectorization.
- `langchain.text_splitter.RecursiveCharacterTextSplitter`: Splits text into smaller, overlapping chunks for processing.
- `io.BytesIO`: Handles in-memory PDF files.
- `os`: Verifies file existence.

## Class Definition

```python
class PDFParser:
    def __init__(self, file: str | BytesIO, nlp: Language, chunkSize: int = 500, chunkOverlap: int = 100)
```

### Parameters

- The optimal values for `chunkSize` and `chunkOverlap` should be determined based on the specific use case, as they can impact the effectiveness of text processing.

- `file` (`str | BytesIO`): The input PDF file. Can be a file path (`str`) or an in-memory file (`BytesIO`).
- `nlp` (`Language`): An instance of a spaCy language model.
- `chunkSize` (`int`, default `500`): The size of each text chunk in characters.
- `chunkOverlap` (`int`, default `100`): The number of overlapping characters between text chunks.

### Exceptions Raised

- `TypeError`: Raised when `file` is neither a string nor a `BytesIO` object, or when `nlp` is not a valid `spaCy` language model. Example: `PDFParser(123, nlp)` will raise this error.
- `ValueError`: Raised when the provided `file` is not a valid PDF. Example: Passing a `.txt` file or an improperly formatted `BytesIO` object will trigger this exception.
- `FileNotFoundError`: Raised when the specified file path does not exist. Example: `PDFParser("non_existent.pdf", nlp)` will raise this error if the file is missing.

- `TypeError`: If `file` is not a string or `BytesIO`, or if `nlp` is not a valid `spaCy` language model.
- `ValueError`: If `file` is not a valid PDF file.
- `FileNotFoundError`: If the file path does not exist.

## Methods

### `extractText() -> str`

Extracts all text from the PDF and returns it as a single string.

#### Returns

- `str`: The extracted text from the PDF file.

#### Example

```python
parser = PDFParser("sample.pdf", nlp)
text = parser.extractText()
print(text)
```

### `splitExtractedText(text: str) -> list[str]`

Splits the extracted text into smaller chunks based on `chunkSize` and `chunkOverlap`.

#### Parameters

- `text` (`str`): The extracted text from the PDF.

#### Returns

- `list[str]`: A list of text chunks.

#### Example

```python
chunks = parser.splitExtractedText(text)
print(chunks)
```

### `vectorize(text: str)`

Converts the given text into a numerical vector using the provided spaCy language model.

#### Parameters

- `text` (`str`): The input text to be vectorized.

#### Returns

- `spacy.Floats1d`: A numerical vector representation of the text.

#### Example

```python
vector = parser.vectorize("Sample text")
print(vector)
```

### `vectorizeDocument() -> list[spacy.Floats1d]`

Processes the entire PDF document by extracting text, splitting it into chunks, and vectorizing each chunk.

#### Returns

- `list[spacy.Floats1d]`: A list of numerical vectors representing the document.

#### Example

```python
vectors = parser.vectorizeDocument()
print(vectors)
```

## Usage Example

```python
import spacy
nlp = spacy.load('en_core_web_sm')
parser = PDFParser("document.pdf", nlp)
vectors = parser.vectorizeDocument()
```

## Notes

- Ensure the input file is a valid PDF.
- The `spaCy` language model must be properly initialized before use.
- The chunking mechanism helps in handling large PDF documents efficiently.

