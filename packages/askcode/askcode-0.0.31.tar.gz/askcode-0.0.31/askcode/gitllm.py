# import streamlit as st
import ollama
import os
import json
import numpy as np
from numpy.linalg import norm
from git import Repo
import shutil
import requests
import ast
import sys
from tqdm import tqdm
import subprocess

def clone_with_progress(repo_url,destination,branch):
       # Create a command for git clone with a specific branch
    command = ["git", "clone", "--branch", branch, repo_url, destination]

    # Use subprocess to run the git command
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Set up tqdm progress bar
    progress_bar = tqdm(total=100, desc="Cloning repository", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]")
    
    while True:
        # Read the output line by line
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            print(output.strip())  # Print the output

            # Check for the progress line
            match = re.search(r'Receiving objects: (\d+)%', output)
            if match:
                progress = int(match.group(1))
                progress_bar.n = progress
                progress_bar.refresh()

    # Wait for the process to complete
    process.wait()
    progress_bar.close()

    if process.returncode == 0:
        print(f"\nRepository cloned to {destination}")
    else:
        print(f"\nError cloning repository: {process.stderr.read()}")

def parse_file(directory):
    paragraphs = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.py', '.go', '.md', '.js', '.json', '.html', '.yml')):
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
    return paragraphs

def save_embeddings(filename, embeddings):
    if not os.path.exists("embeddings"):
        os.makedirs("embeddings")
    with open(f"embeddings/{filename}.json", "w") as f:
        json.dump(embeddings, f)

def load_embeddings(filename):
    if not os.path.exists(f"embeddings/{filename}.json"):
        return False
    with open(f"embeddings/{filename}.json", "r") as f:
        return json.load(f)

def get_embeddings(filename, modelname, chunks):
    if (embeddings := load_embeddings(filename)) is not False:
        return embeddings
    embeddings = [
        ollama.embeddings(model=modelname, prompt=chunk)["embedding"]
        for chunk in chunks
    ]
    save_embeddings(filename, embeddings)
    return embeddings

def find_most_similar(needle, haystack):
    needle_norm = norm(needle)
    similarity_scores = [
        np.dot(needle, item) / (needle_norm * norm(item)) for item in haystack
    ]
    return sorted(zip(similarity_scores, range(len(haystack))), reverse=True)

def clone_repo(git_url, clone_dir , branch):
    print(f"Cloning {branch} branch of repository into {clone_dir}")
    Repo.clone_from(git_url, clone_dir, branch=branch)
    print(f"Repository cloned to {clone_dir}")

# def main():
#     st.title("ASCode")

#     # Create session state to manage the Git URL and embeddings
#     if 'cloned' not in st.session_state:
#         st.session_state.cloned = False
#     if 'embeddings' not in st.session_state:
#         st.session_state.embeddings = None
#     if 'directory' not in st.session_state:
#         st.session_state.directory = './tmp'

#     git_url = st.text_input("Enter Git (ssh) Link: ")

#     if git_url:
#         if not st.session_state.cloned:
#         shutil.rmtree(st.session_state.directory)
#         clone_repo(git_url, st.session_state.directory)
#         st.session_state.cloned = True
#         paragraphs = parse_file(st.session_state.directory)
#         st.session_state.embeddings = get_embeddings(st.session_state.directory.replace('/', '_'), "nomic-embed-text", paragraphs)
#         st.success("ASCode processed Repo | embeddings generated.")

#         if st.session_state.cloned:
#             index = 0
#             prompt = st.text_area("Let's Discuss : ")

#             if st.button("Submit", key=index):
#                 if prompt:
#                     prompt_embedding = ollama.embeddings(model="nomic-embed-text", prompt=prompt)["embedding"]
#                     most_similar_chunks = find_most_similar(prompt_embedding, st.session_state.embeddings)[:5]

#                     # Convert embeddings to string representation
#                     context = ""
#                     for score, idx in most_similar_chunks:
#                         if idx < len(paragraphs):
#                             context += paragraphs[idx] + "\n\n"

#                     stream = ollama.chat(
#                         model="ascode-mini",
#                         messages=[
#                             {
#                                 "role": "system",
#                                 "content": "You are code bot\n" + context,
#                             },
#                             {"role": "user", "content": prompt},
#                         ],
#                         stream=True,
#                     )
                    
#                     st.write("".join(chunk['message']['content'] for chunk in stream), end='', flush=True)
#                     index += 1
#                 else:
#                     st.error("No prompt given")
#     else:
#         st.warning("Please enter a Git link to proceed.")

#     st.markdown(
#         """
#         <div style='position: fixed; width: 100%;'>
#             <p>Powered by <strong>EmbedUR</strong></p>
#         </div>
#         """,
#         unsafe_allow_html=True
#     )

def main():
    print("-------------------Ask Code-------------------------")
    
    session_state = {}

    # Create session state to manage the Git URL and embeddings
    if session_state.get('cloned') is None:
        session_state['cloned'] = False
    if session_state.get('embeddings') is None:
        session_state['embeddings'] = None
    if session_state.get('directory') is None:
        session_state['directory'] = './tmp'
    
    git_url = input("Enter Git (ssh) Link: ")
    branch = input("Enter branch to clone from: ")
    
    repo_name = git_url.split(':')[1].split('/')[1].replace('.git', '')
    session_state['directory'] = session_state['directory']+'/'+repo_name
    
    if git_url and branch and not session_state['cloned']:
        if os.path.isdir(session_state["directory"]):
            shutil.rmtree(session_state['directory'])
        os.makedirs(session_state['directory'])
        clone_repo(git_url, session_state['directory'] , branch)
        session_state['cloned'] = True
        

    if session_state['cloned']:
        index = 0
        paragraphs = parse_file(session_state['directory'])
        session_state['embeddings'] = get_embeddings(session_state['directory'].replace('/', '_'), "nomic-embed-text", paragraphs)
        print("ASCode processed Repo | embeddings generated.")
        
    while(True):
        prompt = input("\n Let's Discuss : \n")

        # if st.button("Submit", key=index):
        if prompt and prompt.lower() != "q":
                prompt_embedding = ollama.embeddings(model="nomic-embed-text", prompt=prompt)["embedding"]
                most_similar_chunks = find_most_similar(prompt_embedding, session_state['embeddings'])[:5]
                # Convert embeddings to string representation
                context = ""
                for score, idx in most_similar_chunks:
                    if idx < len(paragraphs):
                        context += paragraphs[idx] + "\n\n"

                #print(context)
                remote_server_url = "http://192.168.138.224:11434/api/chat"
                # stream = ollama.chat(
                payload = {
                    "model":"ascode-mini:latest",
                    "messages":[
                        {
                            "role": "system",
                            "content": "You are code bot\n" + context,
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "stream":True,
                }
                response = requests.post(remote_server_url, json=payload , stream=True)
                #print(response.status_code)
                # print(type(response.content))
                # for chunk in response.content.decode('utf-8').split("\n"):
                #     print(ast.literal_eval(chunk))
                #     print(type(chunk))
                
                #st.write("".join(chunk.decode('utf-8') for chunk in response.content(chunk=1024)), end='', flush=True)
            #     print(
            # *(
            #     json.loads(line).get('message', {}).get('content', 'No content')
            #     for chunk in response.iter_content(chunk_size=10000000)
            #     if chunk
            #     for line in chunk.decode('utf-8').splitlines()
            #     if line.strip()
            # )
            #
            # )
                for chunk in response.iter_content(chunk_size=10000000):
                    if chunk:
                        for line in chunk.decode('utf-8').splitlines():
                            if line.strip():
                                print(json.loads(line).get('message',{}).get('content',{}),end='')
                index += 1
        elif prompt.lower() == "q":
            print("Thank you!")
            sys.exit(0)
        else:
                print("No prompt given")

    # st.markdown(
    #     """
    #     <div style='position: fixed; width: 100%;'>
    #         <p>Powered by <strong>embedUR</strong></p>
    #     </div>
    #     """,
    #     unsafe_allow_html=True
    # )

if __name__ == "__main__":
    main()