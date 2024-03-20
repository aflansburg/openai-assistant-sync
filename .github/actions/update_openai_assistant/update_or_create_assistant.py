import os
import json
import yaml
from openai import OpenAI

openai_api_key = os.environ["OPENAI_API_KEY"]

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY must be set as environment variables")

client = OpenAI(api_key=openai_api_key)


def read_function_json(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


def read_config_yaml(file_path):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def git_commit_and_push(file_path):
    git_actor = os.environ.get("GITHUB_ACTOR", "github-actions")
    os.system(f'git config --global user.name "{git_actor}"')
    os.system(
        f'git config --global user.email "{git_actor}@users.noreply.github.com"'
    )
    os.system(f"git add {file_path}")
    os.system('git commit -m "Update assistant ID"')
    os.system("git push origin main")


def update_or_create_assistant(root_directory="./assistants"):
    for directory in os.listdir(root_directory):
        full_directory_path = os.path.join(root_directory, directory)
        # ignore directory named example
        if directory == "example":
            continue
        if os.path.isdir(full_directory_path):
            config_file_path = os.path.join(full_directory_path, "config.yml")
            config = read_config_yaml(config_file_path)
            assistant_name = config["assistant"]["name"]
            assistant_id = config["assistant"].get("id")
            model = config["assistant"].get("model", "gpt-4")

            print(f"Working with assistant: {assistant_name}")

            with open(
                os.path.join(
                    full_directory_path, "prompt-templates/prompt-template.md"
                ),
                "r",
            ) as file:
                instructions = file.read()

            function_files = []
            for root, dirs, files in os.walk(
                os.path.join(full_directory_path, "functions")
            ):
                for file in files:
                    if file.endswith(".func.json"):
                        function_files.append(os.path.join(root, file))

            functions = [read_function_json(f) for f in function_files]

            if assistant_id:
                try:
                    my_assistant = client.beta.assistants.retrieve(
                        assistant_id
                    )
                except Exception:
                    my_assistant = None
            else:
                my_assistant = None

            if my_assistant is None:
                print(f"Creating assistant: {assistant_name}")
                my_assistant = client.beta.assistants.create(
                    instructions=instructions,
                    name=assistant_name,
                    tools=[
                        {"type": "function", "function": func}
                        for func in functions
                    ],
                    model=model,
                )
                print(f"Created new assistant: {my_assistant}")

                config["assistant"]["id"] = my_assistant.id
                with open(config_file_path, "w") as file:
                    yaml.safe_dump(config, file)

                git_commit_and_push(config_file_path)
            else:
                print(
                    f"Updatid assistant: {assistant_name} with id {assistant_id}"
                )
                if not assistant_id:
                    assistant_id = my_assistant.id
                    config["assistant"]["id"] = assistant_id
                    with open(config_file_path, "w") as file:
                        yaml.safe_dump(config, file)
                my_updated_assistant = client.beta.assistants.update(
                    assistant_id=assistant_id,
                    instructions=instructions,
                    name=assistant_name,
                    tools=[
                        {"type": "function", "function": func}
                        for func in functions
                    ],
                    model=model,
                )
                print(my_updated_assistant)

                git_commit_and_push(config_file_path)


update_or_create_assistant()
