import os
import json
import ollama
import numpy as np
import logging
import argparse
import psutil
from tqdm import tqdm
import time
import subprocess
import sys

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def check_ollama_installed():
    try:
        # Check if ollama is installed
        result = subprocess.run(['ollama', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return True
        return False
    except FileNotFoundError:
        return False

def install_pack():
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])

        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'ollama','--quiet'])
    
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'numpy','--quiet'])

        print("pip packages installed successfully.")
        
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing Ollama: {e}")

def pull_images():
    try:
        subprocess.check_call(['ollama', 'pull', select_model_based_on_ram()])
        print("Images pulled successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while pulling images: {e}")

def parse_file(directory, show_files=False):
    paragraphs = []
    total_files = sum(len(files) for _, _, files in os.walk(directory))
    file_count = 0

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.py', '.go', '.md','.c','.cc','.hpp','.h','.txt','.json','.js','.ts')):
                file_count += 1
                if show_files:
                    tqdm.write(f"Processing {file} ({file_count}/{total_files})", end="")
                    time.sleep(0.2)  # Sleep to show the file processing (can be adjusted)

                try:
                    with open(os.path.join(root, file), encoding="utf-8-sig") as f:
                        buffer = []
                        for line in f.readlines():
                            line = line.strip()
                            if line:
                                buffer.append(line)
                            elif len(buffer):
                                paragraphs.append(" ".join(buffer))
                                buffer = []
                        if len(buffer):
                            paragraphs.append(" ".join(buffer))
                except Exception as e:
                    logging.error(f"Error reading file {file}: {e}")
                
    return paragraphs

def save_embeddings(filename, embeddings):
    if not os.path.exists("embeddings"):
        os.makedirs("embeddings")
    try:
        with open(f"embeddings/{filename}.json", "w", encoding="utf-8-sig") as f:
            json.dump(embeddings, f)
    except Exception as e:
        logging.error(f"Error saving embeddings to {filename}.json: {e}")

def load_embeddings(filename):
    filepath = f"embeddings/{filename}.json"
    if not os.path.exists(filepath):
        return False
    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading embeddings from {filepath}: {e}")
        return False

def get_embeddings(filename, modelname, chunks, show_files=False):
    if (embeddings := load_embeddings(filename)) is not False:
        return embeddings
    embeddings = []
    total_chunks = len(chunks)

    for i, chunk in enumerate(tqdm(chunks, desc="Generating Embeddings", unit="chunk")):
        try:
            embedding = ollama.embeddings(model=modelname, prompt=chunk)["embedding"]
            embeddings.append(embedding)
        except Exception as e:
            logging.error(f"Error generating embedding for chunk {i+1}/{total_chunks}: {e}")
    
    save_embeddings(filename, embeddings)
    return embeddings

def find_most_similar(needle, haystack):
    needle_norm = np.linalg.norm(needle)
    similarity_scores = [
        np.dot(needle, item) / (needle_norm * np.linalg.norm(item)) for item in haystack
    ]
    return sorted(zip(similarity_scores, range(len(haystack))), reverse=True)

def select_model_based_on_ram():
    available_memory_gb = psutil.virtual_memory().available / (1024 ** 3)
    logging.info(f"Available RAM: {available_memory_gb:.2f} GB")
    
    if available_memory_gb > 16:
       return "codestral:22b" 
    elif 8 < available_memory_gb <= 16:
        return "mistral:latest" 
    else:
        return "0ssamaak0/xtuner-llava:phi3-mini-int4"

def main(directory, show_files=False):
    modelname = select_model_based_on_ram()
    logging.info(f"Selected model: {modelname}")

    logging.info(f"Parsing files in directory: {directory}")
    paragraphs = parse_file(directory, show_files)
    embeddings = get_embeddings(directory.replace('/', '_'), modelname, paragraphs, show_files)

    logging.info("Starting interactive session...")
    print("\n Hii👋, I'm ASCode by EmbedUR, Your coding companion !!\n")
    first = True
    while(True): 
        if first:
            prompt = input("Let's discuss : \n")
            first = False
        else:    
            prompt = input("\n Follow Up:\n")
        try:
            prompt_embedding = ollama.embeddings(model=modelname, prompt=prompt)["embedding"]
            most_similar_chunks = find_most_similar(prompt_embedding, embeddings)[:5]

            # Get top three referenced documents based on similarity
            top_three_docs = [paragraphs[item[1]] for item in most_similar_chunks[:3]]
            print("\nReference:")
            for i, doc in enumerate(top_three_docs):
                print(f"{i+1}. {doc[:50]}...")

            stream = ollama.chat(
                model= modelname,
                messages=[
                    {
                        "role": "system",
                        "content": "You are coding assistant"
                        + "\n".join(paragraphs[item[1]] for item in most_similar_chunks),
                    },
                    {"role": "user", "content": prompt},
                ],
                stream = True,
            )
            
            for chunk in stream:
                print(chunk['message']['content'], end='', flush=True)
        except Exception as e:
            logging.error(f"Error in interactive session: {e}")
            break
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ASCode: Your Coding Companion")
    parser.add_argument("-d", "--directory", type=str, default="./", help="Directory to parse files from")
    parser.add_argument("-an", "--show-files", action="store_true", help="Show file processing animations")
    args = parser.parse_args()
    
    if check_ollama_installed():
        print("Ollama is already installed.")
        pull_images()
    else:
        print("Failed to install Ollama. Please refer to the documentation for further instructions.")
        print("Documentation: https://ollama.com/download")
        exit()
    install_pack()
    main(args.directory, args.show_files)