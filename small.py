import subprocess


def run(cmd):
    cmd = shlex.split(cmd)
    subprocess.check_call(cmd)
