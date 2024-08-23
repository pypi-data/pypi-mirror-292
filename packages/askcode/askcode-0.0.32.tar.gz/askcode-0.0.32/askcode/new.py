import os
import json
import ollama
import numpy as np
import logging
import subprocess
import sys
import psutil
from tqdm import tqdm
import time
import requests
import re
from numpy.linalg import norm
from git import Repo

# Logging setup (uncomment to enable logging)
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_ollama_installed():
    try:
        result = subprocess.run(['ollama', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_pack():
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'ollama', '--quiet'])
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'numpy', '--quiet'])
        print("pip packages installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing packages: {e}")

def pull_images(modelname):
    try:
        subprocess.check_call(['ollama', 'pull', modelname])
        print("Images pulled successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while pulling images: {e}")

def parse_file(directory, show_files=False):
    paragraphs = []
    total_files = sum(len(files) for _, _, files in os.walk(directory))
    file_count = 0

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.py', '.go', '.md', '.c', '.cc', '.hpp', '.h', '.txt', '.json', '.js', '.ts')):
                file_count += 1
                if show_files:
                    tqdm.write(f"Processing {file} ({file_count}/{total_files})", end="")
                    time.sleep(0.2)

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
            print("Generating Embedding")
        except Exception as e:
            logging.error(f"Error generating embedding for chunk {i+1}/{total_chunks}: {e}")

    save_embeddings(filename, embeddings)
    return embeddings

def find_most_similar(needle, haystack):
    needle_norm = norm(needle)
    similarity_scores = [
        np.dot(needle, item) / (needle_norm * norm(item)) for item in haystack
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

def clone_repo(git_url, destination, branch):
    print(f"Cloning {branch} branch of repository into {destination}")
    command = ["git", "clone", "--branch", branch, git_url, destination]

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            print(output.strip())
            match = re.search(r'Receiving objects: (\d+)%', output)

    process.wait()

    if process.returncode == 0:
        print(f"\nRepository cloned to {destination}")
    else:
        print(f"\nError cloning repository: {process.stderr.read()}")

def pull_repo(directory, branch):
    print(f"Pulling {branch} branch of the repository")
    
    checkout_command = ["git", "checkout", branch]
    process = subprocess.Popen(checkout_command, cwd=directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    for line in process.stdout:
        print(line.strip())
        
    process.wait()
    
    if process.returncode != 0:
        print(f"Error checking out branch: {process.stderr.read()}")
        return
    
    pull_command = ["git", "pull"]
    process = subprocess.Popen(pull_command, cwd=directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    for line in process.stdout:
        print(line.strip())
        match = re.search(r'Receiving objects: (\d+)%', line)
        if match:
            print(f"Progress: {match.group(1)}%")
    
    process.wait()
    
    if process.returncode == 0:
        print(f"\nRepository Pulled Successfully")
    else:
        print(f"\nError pulling repository: {process.stderr.read()}")

def generate_test_cases(file_path):
    # Read the code from the specified file
    try:
        with open(file_path, 'r') as file:
            code_snippet = file.read()
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    # Prepare the payload for the remote server
    payload = {
        "model": "llama3:8b",
        "messages": [
            {
                "role": "system",
                "content": f"Please generate detailed unit and integration test cases for the following code snippet:\n```{code_snippet}```"
            }
        ],
        "stream": False  # Assuming the server handles non-streaming requests
    }
    
    remote_server_url = "http://192.168.138.224:11434/api/chat"
    
    try:
        # Execute the request to the remote server
        response = requests.post(remote_server_url, json=payload)
        response.raise_for_status()  # Raise an error for bad responses
        output = response.json().get('message', {}).get('content', '')
    except requests.RequestException as e:
        print(f"Error executing request: {e}")
        return
    except Exception as e:
        print(f"Unexpected error: {e}")
        return
    
    # Print the generated test cases
    print("Generated Test Cases:")
    print(output)

def main():
    if not check_ollama_installed():
        print("Ollama is not installed. Installing...")
        install_pack()

    print("What are you up to work with?")
    print(" (1) Remote Repository\n (2) Local Repository\n (3) Generate Test Case")
    repo_choice = input("Choice : ").strip().lower()

    if repo_choice == '1':
        git_url = input("Enter Git (ssh) Link: ").strip()
        branch = input("Enter branch to clone from: ").strip()
        repo_name = git_url.split(':')[1].split('/')[-1].replace('.git', '')
        directory = os.path.join('./tmp', repo_name)

        if os.path.isdir(directory):
            pull_repo(directory, branch)
        else:
            os.makedirs(directory)
            clone_repo(git_url, directory, branch)
        paragraphs = parse_file(directory)

    elif repo_choice == '2':
        directory = input("Enter the directory to parse files from: ").strip()
        if not os.path.isdir(directory):
            print(f"The directory '{directory}' does not exist or is not a valid directory.")
            sys.exit(1)
        paragraphs = parse_file(directory)
    elif repo_choice == '3':
        file_path = input("Enter the file path to generate test cases from: ").strip()
        generate_test_cases(file_path)
        return  # Exit after generating test cases
    else:
        print("Invalid choice.")
        sys.exit(1)

    print("Select model type:")
    print(" (1) Remote Repository\n (2) Local Repository\n ")
    model_choice = input("Choice : ").strip().lower()

    if model_choice == '1':
        modelname = select_model_based_on_ram()
        pull_images(modelname)
    elif model_choice == '2':
        modelname = select_model_based_on_ram()
  

    else:
        print("Invalid choice.")
        sys.exit(1)


    embeddings = get_embeddings(directory.replace('/', '_'), modelname, paragraphs)

    print("\nHi👋, I'm ASCode by EmbedUR, Your coding companion!!\n")
    first = True
    while True:
        if first:
            prompt = input("Let's discuss: \n")
            first = False
        else:
            prompt = input("\nFollow Up:\n")

        if prompt.lower() == "q":
            print("Thank you!")
            sys.exit(0)

        try:
            prompt_embedding = ollama.embeddings(model=modelname, prompt=prompt)["embedding"]
            most_similar_chunks = find_most_similar(prompt_embedding, embeddings)[:5]

            # Get top three referenced documents based on similarity
            top_three_docs = [paragraphs[item[1]] for item in most_similar_chunks[:3]]
            print("\nReference:")
            for i, doc in enumerate(top_three_docs):
                print(f"{i+1}. {doc[:50]}...")

            if model_choice == '2':  # Remote model interaction
                remote_server_url = "http://192.168.138.224:11434/api/chat"
                payload = {
                    "model": "codestral:22b",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a code bot\n" + "\n".join(paragraphs[item[1]] for item in most_similar_chunks),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "stream": True,
                }
                response = requests.post(remote_server_url, json=payload, stream=True)
                
                for chunk in response.iter_content(chunk_size=10000000):
                    if chunk:
                        for line in chunk.decode('utf-8').splitlines():
                            if line.strip():
                                print(json.loads(line).get('message', {}).get('content', ''), end='')
            else:  # Local model interaction
                stream = ollama.chat(
                    model=modelname,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are coding assistant\n" + "\n".join(paragraphs[item[1]] for item in most_similar_chunks),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    stream=True,
                )

                for chunk in stream:
                    print(chunk['message']['content'], end='', flush=True)

        except Exception as e:
            logging.error(f"Error in interactive session: {e}")

if __name__ == "__main__":
    main()
