import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")

    import click
    from thunder import auth
    import sys
    import os
    from os.path import join
    from scp import SCPClient
    import paramiko
    import subprocess
    from multiprocessing import Process, Event
    import time
    import platform
    import getpass

    from thunder import thunder_helper
    from thunder import container_helper
    from thunder import utils
    from thunder.file_sync import start_file_sync

    try:
        from importlib.metadata import version
    except Exception as e:
        from importlib_metadata import version

    import requests
    from packaging import version as version_parser
    from thunder import api
    from yaspin import yaspin
    from beautifultable import BeautifulTable

PACKAGE_NAME = "tnr"  # update if name changes
# Get the directory of the current file (thunder.py), then go up two levels to the root
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.join(current_dir, "..", "..")

# Add the src directory to sys.path
sys.path.append(root_dir)


class DefaultCommandGroup(click.Group):
    def resolve_command(self, ctx, args: list):
        try:
            # Try to resolve the command normally
            # check_for_update()
            return super(DefaultCommandGroup, self).resolve_command(ctx, args)
        except click.exceptions.UsageError:
            # If no command is found, default to 'run' and include the args
            return "run", run, args

def get_token():
    id_token, refresh_token, uid = auth.load_tokens()
    if not id_token or not refresh_token:
        click.echo("Please log in to begin using Thunder Compute.")
        id_token, refresh_token, uid = auth.login()

        if not id_token or not refresh_token:
            return None

    if not api.is_token_valid(id_token):
        id_token, refresh_token, uid = auth.handle_token_refresh(refresh_token)

    return id_token


@click.group(
    cls=DefaultCommandGroup,
    help="This CLI is the interface between you and Thunder Compute.",
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
)
@click.pass_context
@click.version_option(version=version(PACKAGE_NAME))
def cli(ctx):
    utils.setup_instance()

# @cli.group('GPU Usage')
# def gpu_usage():
#     # """Commands to use the Thunder Compute GPU"""
#     pass

@cli.command(
    help="Runs a specified task on Thunder Compute. This is the default behavior of the tnr command. Please see thundergpu.net for detailed documentation.",
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def run(args):
    if not args:  # Check if args is empty
        click.echo("No arguments provided. Exiting...")
        sys.exit(0)

    id_token, refresh_token, uid = auth.load_tokens()

    if not id_token or not refresh_token:
        click.echo("Please log in to begin using Thunder Compute.")
        id_token, refresh_token, uid = auth.login()

        if not id_token or not refresh_token:
            return

    id_token, refresh_token, uid = auth.handle_token_refresh(refresh_token)

    # Identify current computer
    basedir = join(os.path.expanduser("~"), ".thunder")
    device_id_file = join(basedir, "device_id")
    if not os.path.exists(device_id_file):
        try:
            endpoint = f"https://api.thundercompute.com:8443/next_id"
            response = requests.get(endpoint, headers={"Authorization": f"Bearer {id_token}"})
            identity = response.json()['id']
            with open(device_id_file, 'w+', encoding="utf-8") as f:
                f.write(str(identity))
        except Exception as e:
            click.echo(
                click.style(
                    f"⛔ Unable to create device identity file. Please report this error to the developers",
                    fg="red",
                )
            )
            exit(1)
        os.chmod(device_id_file, 0o400)

    # Create an instance of Task with required arguments
    task = thunder_helper.Task(args, uid)

    # Execute the task
    if not task.execute_task(id_token):
        return

    # Close the session
    if not task.close_session(id_token):
        click.echo("Failed to close the session.")

@cli.command(help="Set which type of GPU to run on.")
@click.argument("device_type", required=False)
@click.option("-n", "--ngpus", type=int)
@click.option("--raw", required=False, is_flag=True)
def device(device_type, ngpus, raw):
    basedir = join(os.path.expanduser("~"), ".thunder")
    device_file = join(basedir, "dev")
    num_file = join(basedir, "ngpus")
    supported_devices = set(
        [
            "cpu",
            "t4",
            "v100",
            "a100",
            "l4",
            "p4",
            "p100",
            "h100",
        ]
    )

    if device_type is None:
        with open(device_file, "r") as f:
            device = f.read().strip()

        if device not in supported_devices:
            # If not valid, set it to the default value
            device = "t4"
            with open(device_file, "w") as f:
                f.write(device)

        if ngpus is None:
            with open(num_file, "r") as f:
                content = f.read().strip()

            if not content.isnumeric():
                # If not valid, set it to the default value
                ngpus = 1
                with open(num_file, "w") as f:
                    f.write(str(ngpus))
            else:
                ngpus = int(content)

        if raw is not None and raw:
            if ngpus == 1:
                click.echo(device.upper())
            else:
                click.echo(f"{ngpus}x{device.upper()}")
            return

        if device.lower() == "cpu":
            click.echo(
                click.style(
                    "📖 No GPU selected - use `tnr device <gpu-type>` to select a GPU",
                    fg="white",
                )
            )
            return

        if ngpus == 1:
            click.echo(click.style(f"📖 Current GPU: {device.upper()}", fg="white"))
        else:
            click.echo(
                click.style(f"📖 Current GPUs: {ngpus} x {device.upper()}", fg="white")
            )

        available_gpus = utils.get_available_gpus()
        if available_gpus is not None and len(available_gpus) > 0:
            click.echo(
                click.style(
                    f"🌐 Available GPUs: {', '.join(available_gpus)}", fg="white"
                )
            )
        return

    if device_type.lower() not in supported_devices:
        click.echo(
            click.style(
                f"⛔ Unsupported device type: {device_type}. Please select one of CPU, T4, V100, A100, L4, P4, P100, or H100",
                fg="red",
            )
        )
        exit(1)

    if device_type.lower() == "cpu":
        with open(device_file, "w") as f:
            f.write(device_type.lower())

        with open(num_file, "w") as f:
            f.write("0")

        click.echo(
            click.style(
                f"✅ Device set to CPU, you are now disconnected from any GPUs.",
                fg="green",
            )
        )
        return

    with open(device_file, "w") as f:
        f.write(device_type.lower())

    if ngpus is None:
        ngpus = 1

    with open(num_file, "w") as f:
        f.write(str(ngpus))

    click.echo(
        click.style(f"✅ Device set to {ngpus} x {device_type.upper()}", fg="green")
    )

def add_key_to_instance(id_token):
    add_key_to_instance_url = "https://add-key-to-instance-b7ngwrgpka-uc.a.run.app"
    try:
        headers = {
            "Authorization": "Bearer " + id_token,
            "Content-Type": "application/json",
        }

        response = requests.post(add_key_to_instance_url, headers=headers, timeout=120)
        if response.status_code == 401:
            # Retry with refreshed token
            id_token, refresh_token, uid = auth.handle_token_refresh(refresh_token)
            headers = {
                "Authorization": "Bearer " + id_token,
                "Content-Type": "application/json",
            }
            response = requests.post(
                add_key_to_instance_url, headers=headers, timeout=120
            )

        return response

    except Exception as _:
        return None


@cli.command(help="Get status of running Thunder Compute instances")
def status():
    token = get_token()
    success, error, instances = utils.get_instances(token)
    if not success:
        click.echo(
            click.style(
                f"⛔ Failed to list thunder compute instance: {error}",
                fg="red",
            )
        )
        exit(1)

    table = BeautifulTable()
    title = [
        click.style("ID", bold=True),
        click.style("Status", bold=True),
        click.style("Address", bold=True),
        click.style("Creation Date", bold=True),
    ]
    table.rows.append(title)

    for instance_id, metadata in instances.items():
        if metadata["status"] == "RUNNING":
            status_color = "green"
        elif metadata["status"] == "STOPPED":
            status_color = "red"
        else:
            status_color = "yellow"

        if metadata["ip"] is None or len(metadata["ip"]) == 0:
            ip_entry = '--'
        else:
            ip_entry = metadata["ip"]
            
        table.rows.append(
            [
                instance_id,
                click.style(metadata["status"], fg=status_color),
                ip_entry,
                metadata["createdAt"],
            ]
        )
    
    if len(instances) == 0:
        table.rows.append(["--", "--", "--", "--"])


    click.echo(click.style("Thunder Compute Instances", bold=True, fg='cyan'),)
    print(table)
    print()
    
    active_sessions = utils.get_active_sessions(token)
    table = BeautifulTable()
    title = [
        click.style("Type", bold=True),
        click.style("Duration", bold=True),
    ]
    table.rows.append(title)

    for session_info in active_sessions:        
        table.rows.append(
            [
                session_info['gpu'],
                f"{session_info['duration']}s",
            ]
        )

    if len(active_sessions) == 0:
        table.rows.append(["--", "--"])

    click.echo(click.style("Active GPUs", bold=True, fg='cyan'),)
    print(table)


@cli.command(help="Create a new Thunder Compute instance")
def create():
    token = get_token()
    success, error = utils.create_instance(token)
    if success:
        click.echo(
            click.style(f"✅ Successfully created thunder compute instance!", fg="green")
        )
    else:
        click.echo(
            click.style(
                f"⛔ Failed to create thunder compute instance: {error}",
                fg="red",
            )
        )

@click.argument("instance_id", required=True)
@cli.command(help="Delete an existing Thunder Compute instance")
def delete(instance_id):
    token = get_token()
    success, error = utils.delete_instance(instance_id, token)
    if success:
        click.echo(
            click.style(f"✅ Successfully deleted thunder compute instance {instance_id}", fg="green")
        )
        
        utils.remove_instance_from_ssh_config(f'tnr-{instance_id}')
    else:
        click.echo(
            click.style(
                f"⛔ Failed to delete thunder compute instance {instance_id}: {error}",
                fg="red",
            )
        )
        
@click.argument("instance_id", required=True)
@cli.command(help="Start a stopped Thunder Compute instance")
def start(instance_id):
    token = get_token()
    success, error = utils.start_instance(instance_id, token)
    if success:
        click.echo(
            click.style(f"✅ Successfully started thunder compute instance {instance_id}", fg="green")
        )
    else:
        click.echo(
            click.style(
                f"⛔ Failed to start thunder compute instance {instance_id}: {error}",
                fg="red",
            )
        )


@click.argument("instance_id", required=True)
@cli.command(help="Stop a running Thunder Compute instance")
def stop(instance_id):
    token = get_token()
    success, error = utils.stop_instance(instance_id, token)
    if success:
        click.echo(
            click.style(f"✅ Successfully stopped thunder compute instance {instance_id}", fg="green")
        )
    else:
        click.echo(
            click.style(
                f"⛔ Failed to stop thunder compute instance {instance_id}: {error}",
                fg="red",
            )
        )

@click.argument("instance_id", required=True)
@cli.command(help="Connect to a Thunder Compute instance")
def connect(instance_id):
    token = get_token()
    success, error, instances = utils.get_instances(token)
    if not success:
        click.echo(
            click.style(
                f"⛔ Failed to list thunder compute instance: {error}",
                fg="red",
            )
        )
        exit(1)

    for curr_instance_id, metadata in instances.items():
        if curr_instance_id == instance_id:
            if metadata['ip'] == None:
                click.echo(
                    click.style(
                        f"⛔ Instance {instance_id} is not available to connect",
                        fg="red",
                    )
                )
                return
            ip = metadata['ip']
            
            if ip is None or ip == "":
                click.echo(
                    click.style(
                        f"⛔ Unable to connect to instance {instance_id}, is the instance running?",
                        fg="red",
                    )
                )
                exit(1)

            
            keyfile = utils.get_key_file(metadata['uuid'])
            if not os.path.exists(keyfile):
                if not utils.add_key_to_instance(instance_id, token):
                    click.echo(
                        click.style(
                            f"⛔ Unable to find or create ssh key file for instance {instance_id}",
                            fg="red",
                        )
                    )
                    exit(1)

            start_time = time.time()
            connection_successful = False
            while start_time + 60 > time.time():
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                try:
                    ssh.connect(ip, username="ubuntu", key_filename=keyfile, timeout=10)
                    connection_successful = True
                    break
                except Exception as e:
                    continue
            
            if not connection_successful:
                click.echo(
                    click.style(
                        "⛔ Failed to connect to the thunder compute instance within a minute. Please retry this command or contant the developers at support@thundercompute.com if this issue persists.",
                        fg="red",
                    )
                )
                exit(1)

            basedir = join(os.path.expanduser("~"), ".thunder")
            ssh.exec_command("mkdir -p ~/.thunder && chmod 700 ~/.thunder")
            stdin, stdout, stderr = ssh.exec_command("pip install --upgrade tnr")
            stdout.read().decode() # Forces the command to get executed

            scp = SCPClient(ssh.get_transport())
            scp.put(join(basedir, "token"), remote_path="~/.thunder/token")

            # Update ~/.ssh/config
            host_alias = f'tnr-{instance_id}'
            exists, prev_ip = utils.get_ssh_config_entry(host_alias)
            if not exists:
                utils.add_instance_to_ssh_config(ip, keyfile, host_alias)
            else:
                if ip != prev_ip:
                    utils.update_ssh_config_ip(host_alias, ip)
            
            if platform.system() == "Windows":
                subprocess.run(
                    [
                        "ssh",
                        f"ubuntu@{ip}",
                        "-o",
                        "StrictHostKeyChecking=accept-new",
                        "-i",
                        rf"{keyfile}",
                        "-t",
                        f"exec /home/ubuntu/.local/bin/tnr run /bin/bash",
                    ],
                    shell=True,
                )
            else:
                subprocess.run(
                    [
                        f"ssh ubuntu@{ip} -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=/dev/null -i {keyfile} -t 'exec /home/ubuntu/.local/bin/tnr run /bin/bash'"
                    ],
                    shell=True,
                )
            click.echo(click.style("⚡ Exiting thunder instance ⚡", fg="cyan"))
            return
    
    click.echo(
        click.style(
            f"⛔ Unable to find instance {instance_id}",
            fg="red",
        )
    )
    
@click.argument("dst", required=True)
@click.argument("src", required=True)
@cli.command(help="Copy data from local machine to a thunder instance")
def scp(src, dst):
    token = get_token()
    success, error, instances = utils.get_instances(token)
    if not success:
        click.echo(
            click.style(
                f"⛔ Failed to list thunder compute instance: {error}",
                fg="red",
            )
        )
        exit(1)

    # Determine direction and instance
    src_split = src.split(':')
    dst_split = dst.split(':')
    if len(src_split) > 1:
        src_candidate_instance = src_split[0]
    else:
        src_candidate_instance = None
        
    if len(dst_split) > 1:
        dst_candidate_instance = dst_split[0]
    else:
        dst_candidate_instance = None

    for instance_id, metadata in instances.items():
        if instance_id == src_candidate_instance or instance_id == dst_candidate_instance:
            local_to_remote = True if instance_id == dst_candidate_instance else False
            local_path = src if local_to_remote else dst
            remote_path = dst_split[1] if local_to_remote else src_split[1]
            if remote_path == '':
                remote_path = '~/'
            
            if metadata['ip'] == None:
                click.echo(
                    click.style(
                        f"⛔ Instance {instance_id} is not available to connect",
                        fg="red",
                    )
                )
                return
            ip = metadata['ip']
            
            if ip is None or ip == "":
                click.echo(
                    click.style(
                        f"⛔ Unable to connect to instance {instance_id}, is the instance running?",
                        fg="red",
                    )
                )
                exit(1)

            
            keyfile = utils.get_key_file(metadata['uuid'])
            if not os.path.exists(keyfile):
                if not utils.add_key_to_instance(instance_id, token):
                    click.echo(
                        click.style(
                            f"⛔ Unable to find or create ssh key file for instance {instance_id}",
                            fg="red",
                        )
                    )
                    exit(1)

            start_time = time.time()
            connection_successful = False
            while start_time + 60 > time.time():
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                try:
                    ssh.connect(ip, username="ubuntu", key_filename=keyfile, timeout=10)
                    connection_successful = True
                    break
                except Exception as e:
                    continue
            
            if not connection_successful:
                click.echo(
                    click.style(
                        "⛔ Failed to connect to the thunder compute instance within a minute. Please retry this command or contant the developers at support@thundercompute.com if this issue persists.",
                        fg="red",
                    )
                )
                exit(1)                
            
            if local_to_remote:
                waiting_text = f"Copying {local_path} to {remote_path} on remote instance {instance_id}"
            else:
                waiting_text = f"Copying {remote_path} from instance {instance_id} to {local_path}"
            
            with yaspin(text=waiting_text, color="blue") as spinner:
                transport = ssh.get_transport()
                transport.use_compression(True)

                with SCPClient(transport) as scp:
                    if local_to_remote:
                        scp.put(local_path, remote_path, recursive=True)
                    else:
                        scp.get(remote_path, local_path, recursive=True)
                        
                spinner.ok("✅")
            return
    
    click.echo(
        click.style(
            f"⛔ Unable to find instance to copy to/from in {src} or {dst}",
            fg="red",
        )
    )


@cli.command(help="Logs in to Thunder Compute.")
def login():
    auth.login()


@cli.command(help="Logs out from the Thunder Compute CLI.")
def logout():
    auth.logout()

def check_for_update():
    try:
        current_version = version(PACKAGE_NAME)
        response = requests.get(f"https://pypi.org/pypi/{PACKAGE_NAME}/json", timeout=1)
        json_data = response.json() if response else {}
        latest_version = json_data.get("info", {}).get("version", None)
        if version_parser.parse(current_version) < version_parser.parse(latest_version):
            click.echo(
                click.style(
                    f"New version of tnr available, please run pip install --upgrade tnr",
                    fg="blue",
                )
            )

    except Exception as e:
        click.echo(f"Error checking for update: {e}", err=True)


if __name__ == "__main__":
    cli()
