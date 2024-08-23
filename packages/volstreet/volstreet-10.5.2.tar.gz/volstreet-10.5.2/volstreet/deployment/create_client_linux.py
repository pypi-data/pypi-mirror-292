import os
import sys
from importlib.resources import files
import random
from crontab import CronTab


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


def create_shell_script(client_name, env, script_path, output_dir="client_scripts"):
    # Define the shell script content
    shell_content = f"""#!/bin/bash
source ~/envs/{env}/bin/activate
python ~/{script_path}
"""

    # Define the output shell script path
    shell_file_path = os.path.join(output_dir, f"run_{client_name.lower()}.sh")

    try:
        # Write the shell script content to the output file
        with open(shell_file_path, "w") as shell_file:
            shell_file.write(shell_content)
        # Make the shell script executable
        os.chmod(shell_file_path, 0o755)
    except IOError as e:
        print(f"Error writing to {shell_file_path}: {e}")
        sys.exit(1)

    full_shell_file_path = os.path.abspath(shell_file_path)
    print(f"Shell script for '{client_name}' created at {full_shell_file_path}")

    return full_shell_file_path


def create_websocket_shell_script(env, websocket_shell_file="run_websocket.sh"):
    # Define the shell script content
    shell_content = f"""#!/bin/bash
source ~/envs/{env}/bin/activate
python ~/websocket_master.py
"""

    try:
        # Write the shell script content to the output file
        with open(websocket_shell_file, "w") as shell_file:
            shell_file.write(shell_content)
        # Make the shell script executable
        os.chmod(websocket_shell_file, 0o755)
    except IOError as e:
        print(f"Error writing to {websocket_shell_file}: {e}")
        sys.exit(1)

    full_shell_file_path = os.path.abspath(websocket_shell_file)
    print(f"Shell script for 'websocket' created at {full_shell_file_path}")
    return full_shell_file_path


def schedule_cron_job(task_name, shell_script, time):
    user_cron = CronTab(user=True)
    job = user_cron.new(command=shell_script)

    hour, minute = time.split(":")
    job.setall(f"{minute} {hour} * * *")

    job.set_comment(task_name)

    if user_cron.write():
        print(f"Cron job '{task_name}' scheduled successfully for {time}.")
    else:
        print(f"Error scheduling cron job '{task_name}'.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_client_linux.py <client_name>")
        sys.exit(1)

    client_name = sys.argv[1]
    env = sys.argv[2] if len(sys.argv) > 2 else "volstreet"

    # Generate a script for each client
    client_py_file_path, websocket_py_file_path = create_client_and_websocket_scripts(
        client_name
    )

    # Creating shell scripts
    client_shell_file = create_shell_script(
        client_name,
        env,
        client_py_file_path,
    )

    websocket_shell_file = create_websocket_shell_script(env)

    # Cron job scheduler
    time_ = random.choice(["03:42", "03:43", "03:44"])
    schedule_cron_job(
        f"{client_name}_strategies".capitalize(), client_shell_file, time_
    )
    time_ = random.choice(["03:40", "03:41"])
    schedule_cron_job("websocket", websocket_shell_file, time_)
