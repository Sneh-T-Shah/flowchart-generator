from git import Repo
import os
from dotenv import load_dotenv
from groq import Groq
import shutil
import time

load_dotenv()

local_dir = './repos/'

def get_repo(repo_url: str):
    """Clone the repository from the given URL."""
    try:
        repo_dir = f"{local_dir}/{repo_url.split('/')[-1]}"
        print(repo_dir)
        if os.path.exists(repo_dir):
            print("Repository already exists!")
            return repo_dir
        print(f"Cloning repository from {repo_url} to {repo_dir}...")
        Repo.clone_from(repo_url, repo_dir)
        print("Repository cloned successfully!")
        return repo_dir
    except Exception as e:
        print(f"An error occurred while cloning the repository: {e}")
        

def generate_tree_from_path(root_path):
    prefix_middle = '├── '
    prefix_last = '└── '
    prefix_vertical = '│   '
    prefix_space = '    '
    
    def _generate_tree(dir_path, prefix=''):
        entries = sorted(os.listdir(dir_path))
        entries = [e for e in entries if not e.startswith('.git')]  # Skip .git
        tree = []
        
        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            current_prefix = prefix_last if is_last else prefix_middle
            full_path = os.path.join(dir_path, entry)
            
            tree.append(f'{prefix}{current_prefix}{entry}')
            
            if os.path.isdir(full_path):
                extension = prefix_space if is_last else prefix_vertical
                tree.extend(_generate_tree(full_path, prefix + extension))
                
        return tree

    result = [root_path]
    result.extend(_generate_tree(root_path))
    return '\n'.join(result)

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),  # This is the default and can be omitted
)

def get_llm_response(message: str) -> str: 
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": message,
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content

def get_folders_to_summarize(folder_structure: str, readme: str) -> list:
    base_prompt = """Given below is a directory strcuture of a github repo and the readme file of the project
    I want to know the make a algorithm working of the repo please give me a list of files from the given structure that I should summarize to know the working of the project.
    I should know the things like database schema data flow and the main functions of the code
    from the given file name sometimes it is not clear it's working or I need to view the code to get necessary information to make complete algorithm of the project
    Do not give me files which do not have code in them or code which can not be parsed like jupyter notebooks or images or font files css etc 
    limit the number of files to top 10 most important files only
    the path should be be absolute path and on each new line of code without any numbering or bullet points just path 
    also in the resonse do not give me any other information other than the folder path
    """
    message = f"{base_prompt}\nReadme.md::\n{readme}\n{folder_structure}\n"
    response = get_llm_response(message)
    return [line for line in response.split('\n') if line]

def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            contents = file.read()
            contents = contents[:1000]  # Limiting to 1000 characters
        return contents
    except Exception as e:
        print(f"An unexpected error occurred: {e} for file: {file_path}")
        return "Not able to read this file"

def summarize_files(paths: str) -> str:
    responses = {}
    
    for file in paths:
    
        if os.path.isfile(file):
            file_contents = read_file(file)
            prompt = f"""
            Given below is the code of a file from the repo please summarize the code in the file
            I want to know the following things from the code
            - what is the main function of the code
            - what is the database schema if present
            - what is the data flow of the code
            - what is the input data and output data of the code if any
            try to be short and concise in your response . If some of above details are not in code just do not mention it.
            The file name is  {file} and the code is as below
            {file_contents}
            """
            response = get_llm_response(prompt)
            responses[file] = response
    return responses

def get_final_algo(readme,directory_sturcture,file_summary):
    prompt = f"""
    I am giving you the readme file directory structure and the summary of the important code files in the repo.
    With the help of this information please make a complete algorithm of the project.
    You need to give me the following thing based on the information that you have:
    - what is the main function of the project and project working
    - how is the flow of the data in the project , from where to where does the data go
    - what is the database schema of the project if there is any
    - give me step by step working of the project like a flowchart
    Here is the readme {readme}
    Here is the directory structure {directory_sturcture}
    Here is the summary of the important files {file_summary}
    """
    response = get_llm_response(prompt)
    return response

def get_repo_algo(url):
    url = url.strip()
    dir_name = get_repo(url)
    print(dir_name)
    # read the readme file is it is in the root of the repo
    readme_contents = ""
    files = os.listdir(dir_name)
    for file in files:
        if file.lower() == 'readme.md':
            file_path = os.path.join(dir_name, file)
            readme_contents = read_file(file_path)
            break


    repo_dir_structure = generate_tree_from_path(dir_name)
    print(repo_dir_structure)
    folders_to_summarize = get_folders_to_summarize(repo_dir_structure, readme_contents)
    print(folders_to_summarize)
    file_summaries = summarize_files(folders_to_summarize)
    final_summary = ""
    for file in file_summaries.keys():
        final_summary += f"File: {file}\nSummary: {file_summaries[file]}\n\n"
    final_algo = get_final_algo(readme_contents, repo_dir_structure, final_summary)
    return final_algo,repo_dir_structure