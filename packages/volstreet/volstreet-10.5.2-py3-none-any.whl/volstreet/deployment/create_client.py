import os
import subprocess
import sys
import getpass
from importlib.resources import files
import numpy as np


def create_client_and_websocket_scripts(
    client_name,
    client_template_content: str = None,
    websocket_template_content: str = None,
    output_dir="client_scripts",
):
    if client_template_content is None:
        # Define the template file path
        template_path = files("volstreet").joinpath("deployment/client_run_template.py")
        try:
            # Read the template
            with open(template_path, "r") as template_file:
                template_content = template_file.read()
        except FileNotFoundError:
            print(f"Template file not found at {template_path}")
            sys.exit(1)

    # Replace the placeholder with the actual client name
    script_content = template_content.replace("{client_name}", client_name)

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Define the output file path
    client_file_path = os.path.join(output_dir, f"{client_name.lower()}.py")

    try:
        # Write the new script to the output file
        with open(client_file_path, "w") as output_file:
            output_file.write(script_content)
    except IOError as e:
        print(f"Error writing to {client_file_path}: {e}")
        sys.exit(1)

    if websocket_template_content is None:
        try:
            # Read the template
            websocket_template_path = files("volstreet").joinpath(
                "deployment/websocket_template.py"
            )
            with open(websocket_template_path, "r") as w_file:
                w_content = w_file.read()
        except FileNotFoundError:
            print(f"Websocket Template file not found at {websocket_template_path}")
            sys.exit(1)

    # Replace the placeholder with the actual client name
    w_content = w_content.replace("{client_name}", client_name)

    websocket_file_path = "websocket_master.py"

    # Write the new script to the output file
    with open(websocket_file_path, "w") as w_file:
        w_file.write(w_content)

    return client_file_path, websocket_file_path


def create_batch_file(client_name, env, script_path, output_dir="client_scripts"):
    # Define the batch file content
    batch_content = f"""@echo off
cd C:\\Users\\Administrator
call C:\\Users\\Administrator\\envs\\{env}\\Scripts\\activate.bat
python C:\\Users\\Administrator\\{script_path}
"""

    # Define the output batch file path

    batch_file_path = os.path.join(output_dir, f"run_{client_name.lower()}.bat")

    try:
        # Write the batch file content to the output file
        with open(batch_file_path, "w") as batch_file:
            batch_file.write(batch_content)
    except IOError as e:
        print(f"Error writing to {batch_file_path}: {e}")
        sys.exit(1)

    full_batch_file_path = os.path.abspath(batch_file_path)
    print(f"Batch file for '{client_name}' created at {full_batch_file_path}")

    return full_batch_file_path


def create_websocket_batch_file(env, websocket_batch_file="run_websocket.bat"):
    # Define the batch file content
    batch_content = f"""@echo off
cd C:\\Users\\Administrator
call C:\\Users\\Administrator\\envs\\{env}\\Scripts\\activate.bat
python C:\\Users\\Administrator\\websocket_master.py
"""

    try:
        # Write the batch file content to the output file
        with open(websocket_batch_file, "w") as batch_file:
            batch_file.write(batch_content)
    except IOError as e:
        print(f"Error writing to {websocket_batch_file}: {e}")
        sys.exit(1)

    full_batch_file_path = os.path.abspath(websocket_batch_file)
    print(f"Batch file for 'websocket' created at {full_batch_file_path}")
    return full_batch_file_path


def schedule_task(task_name, batch_file, password, time):
    try:
        # Define the command
        command = [
            "schtasks",
            "/create",
            "/tn",
            task_name,
            "/tr",
            batch_file,
            "/sc",
            "daily",
            "/st",
            time,
            "/ru",
            "Administrator",
            "/rp",
            password,
            "/rl",
            "HIGHEST",
        ]

        # Execute the command
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Print the output
        print(f"Task '{task_name}' scheduled successfully.")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error scheduling task '{task_name}':")
        print(e.stderr)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_client.py <client_name>")
        sys.exit(1)

    client_name = sys.argv[1]
    env = sys.argv[2] if len(sys.argv) > 2 else "volstreet"

    password = getpass.getpass("Enter the password: ")

    # Generate a script for each client
    client_py_file_path, websocket_py_file_path = create_client_and_websocket_scripts(
        client_name
    )

    # Creating batch files
    client_batch_file = create_batch_file(
        client_name,
        env,
        client_py_file_path,
    )

    websocket_batch_file = create_websocket_batch_file(env)

    # Task scheduler
    time_ = np.random.choice(["03:42", "03:43", "03:44"])
    schedule_task(
        f"{client_name}_strategies".capitalize(), client_batch_file, password, time_
    )
    time_ = np.random.choice(["03:40", "03:41"])
    schedule_task("websocket", websocket_batch_file, password, time_)
