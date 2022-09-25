import os
import subprocess

def run():
    pg_dump_command = "pg_dump"
    args = f"{os.environ['DATABASE_URL']} -Fc -v > data/finx-tracker.dump"
    command = f"{pg_dump_command} {args}"
    subprocess.run(command, shell=True)
