import os
import subprocess


def run():
    pg_restore_command = f"PGPASSWORD={os.environ['POSTGRES_PASSWORD']} pg_restore"
    args = f" -h {os.environ['POSTGRES_HOST']}"
    args += f" -U {os.environ['POSTGRES_USER']}"
    args += f" -d {os.environ['POSTGRES_DB']}"
    args += " --no-privileges"
    args += " --no-owner"
    args += " data/finx-tracker.dump"
    command = f"{pg_restore_command} {args}"
    subprocess.run(command, shell=True)
