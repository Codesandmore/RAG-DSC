#### python
# filepath: c:\Users\joelj\RAG-DSC\app.py
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import shutil
import PyPDF2
import re
import torch
import ollama
from openai import OpenAI
import time

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize global vars
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama'
)
vault_content = []
vault_embeddings = []
conversation_history = []

# Load vault content if exists
if os.path.exists("vault.txt"):
    with open("vault.txt", "r", encoding='utf-8') as vault_file:
        vault_content = vault_file.readlines()

# Generate embeddings for vault content
if vault_content:
    for content in vault_content:
        try:
            response = ollama.embeddings(model='mxbai-embed-large', prompt=content)
            vault_embeddings.append(response["embedding"])
        except Exception as e:
            print(f"Error generating embedding: {e}")

vault_embeddings_tensor = torch.tensor(vault_embeddings) if vault_embeddings else torch.tensor([])

# Chat endpoint
@app.post("/chat")
async def chat_endpoint(request: Request):
    try:
        data = await request.json()
        user_message = data.get("message", "")
        
        # Get relevant context
        context = get_relevant_context(user_message)
        
        # Prepare chat message
        messages = [{"role": "system", "content": "You are a helpful assistant."}]
        if context:
            messages.append({"role": "system", "content": f"Use this context to answer: {context}"})
        
        for msg in conversation_history[-6:]:  # Only use last 6 messages for context
            messages.append(msg)
            
        messages.append({"role": "user", "content": user_message})
        conversation_history.append({"role": "user", "content": user_message})
        
        # Call LLM
        response = client.chat.completions.create(
            model="llama3",
            messages=messages,
            max_tokens=1000,
        )
        
        assistant_response = response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": assistant_response})
        
        return JSONResponse({"response": assistant_response})
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return JSONResponse({"response": f"Error: {str(e)}"}, status_code=500)

# File upload endpoint
@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    global vault_content, vault_embeddings, vault_embeddings_tensor
    
    temp_file_path = f"temp_{file.filename}"
    try:
        # Save uploaded file
        with open(temp_file_path, "wb") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
        
        # Extract text from PDF
        with open(temp_file_path, "rb") as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                if page.extract_text():
                    text += page.extract_text() + " "
        
        # Process into chunks
        text = re.sub(r'\s+', ' ', text).strip()
        sentences = re.split(r'(?<=[.!?]) +', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 < 1000:
                current_chunk += (sentence + " ").strip()
            else:
                chunks.append(current_chunk)
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk)
            
        # Add to vault
        with open("vault.txt", "a", encoding="utf-8") as vault_file:
            for chunk in chunks:
                vault_file.write(chunk + "\n")
                vault_content.append(chunk)
                
                # Generate embedding for chunk
                response = ollama.embeddings(model='mxbai-embed-large', prompt=chunk)
                embedding = response["embedding"]
                vault_embeddings.append(embedding)
        
        # Update tensor
        vault_embeddings_tensor = torch.tensor(vault_embeddings)
        
        # Clean up
        os.remove(temp_file_path)
        
        return JSONResponse({
            "message": "PDF processed successfully", 
            "chunks": len(chunks)
        })
        
    except Exception as e:
        print(f"Error processing PDF: {e}")
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        return JSONResponse({"error": str(e)}, status_code=500)

# Helper function to get relevant context based on similarity
def get_relevant_context(query, top_k=3):
    if len(vault_content) == 0 or vault_embeddings_tensor.nelement() == 0:
        return ""
        
    try:
        # Get query embedding
        query_embedding = ollama.embeddings(model='mxbai-embed-large', prompt=query)["embedding"]
        query_tensor = torch.tensor([query_embedding])
        
        # Calculate similarity
        similarity = torch.nn.functional.cosine_similarity(
            query_tensor, 
            vault_embeddings_tensor
        )
        
        # Get top-k most similar chunks
        top_indices = torch.argsort(similarity, descending=True)[:top_k]
        
        context = "\n".join([vault_content[i] for i in top_indices])
        return context
    except Exception as e:
        print(f"Error getting context: {e}")
        return ""

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)