import os
import tkinter as tk
from tkinter import filedialog
import PyPDF2
import re
import json
import torch
import ollama
from openai import OpenAI
import argparse

PINK = '\033[95m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
NEON_GREEN = '\033[92m'
RESET_COLOR = '\033[0m'

def convert_pdf_to_text():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)
            text = ''
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                if page.extract_text():
                    text += page.extract_text() + " "
            text = re.sub(r'\s+', ' ', text).strip()
            sentences = re.split(r'(?<=[.!?]) +', text)
            chunks = []
            current_chunk = ""
            for sentence in sentences:
                if len(current_chunk) + len(sentence) + 1 < 1000:
                    current_chunk += (sentence + " ").strip()
                else:
                    chunks.append(current_chunk)
                    current_chunk = sentence + " "
            if current_chunk:
                chunks.append(current_chunk)
            with open("vault.txt", "a", encoding="utf-8") as vault_file:
                for chunk in chunks:
                    vault_file.write(chunk.strip() + "\n")
            print(f"PDF content appended to vault.txt with each chunk on a separate line.")

def upload_txtfile():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, 'r', encoding="utf-8") as txt_file:
            text = txt_file.read()
            text = re.sub(r'\s+', ' ', text).strip()
            sentences = re.split(r'(?<=[.!?]) +', text)
            chunks = []
            current_chunk = ""
            for sentence in sentences:
                if len(current_chunk) + len(sentence) + 1 < 1000:
                    current_chunk += (sentence + " ").strip()
                else:
                    chunks.append(current_chunk)
                    current_chunk = sentence + " "
            if current_chunk:
                chunks.append(current_chunk)
            with open("vault.txt", "a", encoding="utf-8") as vault_file:
                for chunk in chunks:
                    vault_file.write(chunk.strip() + "\n")
            print(f"Text file content appended to vault.txt with each chunk on a separate line.")

def launch_file_upload_gui():
    root = tk.Tk()
    root.title("Upload .pdf or .txt")
    pdf_button = tk.Button(root, text="Upload PDF", command=convert_pdf_to_text)
    pdf_button.pack(pady=10)
    txt_button = tk.Button(root, text="Upload Text File", command=upload_txtfile)
    txt_button.pack(pady=10)
    root.mainloop()

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

def get_relevant_context(rewritten_input, vault_embeddings, vault_content, top_k=3):
    if vault_embeddings.nelement() == 0:
        return []
    input_embedding = ollama.embeddings(model='mxbai-embed-large', prompt=rewritten_input)["embedding"]
    cos_scores = torch.cosine_similarity(torch.tensor(input_embedding).unsqueeze(0), vault_embeddings)
    top_k = min(top_k, len(cos_scores))
    top_indices = torch.topk(cos_scores, k=top_k)[1].tolist()
    
    relevant_context = [vault_content[idx].strip() for idx in top_indices]
    
    seen = set()
    filtered_context = []
    for context in relevant_context:
        if context not in seen:
            filtered_context.append(context)
            seen.add(context)
    return filtered_context

def rewrite_query(user_input_json, conversation_history, ollama_model):
    user_input = json.loads(user_input_json)["Query"]
    context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-2:]])
    prompt = f"""Rewrite the following query by incorporating relevant context from the conversation history.
The rewritten query should:

- Preserve the core intent and meaning of the original query
- Expand and clarify the query to make it more specific and informative for retrieving relevant context
- Avoid introducing new topics or queries that deviate from the original query
- DONT EVER ANSWER the Original query, but instead focus on rephrasing and expanding it into a new query

Return ONLY the rewritten query text, without any additional formatting or explanations.

Conversation History:
{context}

Original query: [{user_input}]

Rewritten query:"""
    response = client.chat.completions.create(
        model=ollama_model,
        messages=[{"role": "system", "content": prompt}],
        max_tokens=200,
        n=1,
        temperature=0.1,
    )
    rewritten_query = response.choices[0].message.content.strip()
    return json.dumps({"Rewritten Query": rewritten_query})

def ollama_chat(user_input, system_message, vault_embeddings, vault_content, ollama_model, conversation_history):
    conversation_history.append({"role": "user", "content": user_input})
    if len(conversation_history) > 1:
        query_json = {"Query": user_input, "Rewritten Query": ""}
        rewritten_query_json = rewrite_query(json.dumps(query_json), conversation_history, ollama_model)
        rewritten_query_data = json.loads(rewritten_query_json)
        rewritten_query = rewritten_query_data["Rewritten Query"]
        print(PINK + "Original Query: " + user_input + RESET_COLOR)
        print(PINK + "Rewritten Query: " + rewritten_query + RESET_COLOR)
    else:
        rewritten_query = user_input
    relevant_context = get_relevant_context(rewritten_query, vault_embeddings, vault_content)
    if relevant_context:
        context_str = "\n".join(relevant_context)
        print("Context Pulled from Documents: \n\n" + CYAN + context_str + RESET_COLOR)
    else:
        print(CYAN + "No relevant context found." + RESET_COLOR)
    
    if relevant_context:
        user_message_with_context = user_input + "\n\nRelevant Context:\n" + context_str
        messages = [
            {"role": "system", "content": system_message},
            *conversation_history[:-1],
            {"role": "user", "content": user_message_with_context}
        ]
    else:
        messages = [
            {"role": "system", "content": system_message},
            *conversation_history
        ]
    response = client.chat.completions.create(
        model=ollama_model,
        messages=messages,
        max_tokens=2000,
    )
    conversation_history.append({"role": "assistant", "content": response.choices[0].message.content})
    return response.choices[0].message.content


if __name__ == "__main__":
    launch_file_upload_gui()
    
    print(NEON_GREEN + "Parsing command-line arguments..." + RESET_COLOR)
    parser = argparse.ArgumentParser(description="Ollama Chat")
    parser.add_argument("--model", default="llama3", help="Ollama model to use (default: llama3)")
    args = parser.parse_args()
    
    print(NEON_GREEN + "Initializing Ollama API client..." + RESET_COLOR)
    client = OpenAI(
        base_url='http://localhost:11434/v1',
        api_key='llama3'
    )
    
    print(NEON_GREEN + "Loading vault content..." + RESET_COLOR)
    vault_content = []
    if os.path.exists("vault.txt"):
        with open("vault.txt", "r", encoding='utf-8') as vault_file:
            vault_content = vault_file.readlines()
    
    print(NEON_GREEN + "Generating embeddings for the vault content..." + RESET_COLOR)
    vault_embeddings = []
    for content in vault_content:
        response = ollama.embeddings(model='mxbai-embed-large', prompt=content)
        vault_embeddings.append(response["embedding"])
    
    print("Converting embeddings to tensor...")
    vault_embeddings_tensor = torch.tensor(vault_embeddings)
    print("Embeddings for each line in the vault:")
    print(vault_embeddings_tensor)
    
    print("Starting conversation loop...")
    conversation_history = []
    system_message = "You are JON,a helpful assistant that is an expert at extracting the most useful information from a given text. Also bring in extra relevant infromation to the user query from outside the given context.Also start every response with a randon friendly chatter such as 'Hey,JON here' and other friendly chatter and based on the time also givr the appropriate greeting like good morning,good evening,good afternoon etc"
    
    while True:
        user_input = input(YELLOW + "Ask a query about your documents (or type 'quit' to exit): " + RESET_COLOR)
        if user_input.lower() == 'quit':
            break
        response = ollama_chat(user_input, system_message, vault_embeddings_tensor, vault_content, args.model, conversation_history)
        print(NEON_GREEN + "Response: \n\n" + response + RESET_COLOR)