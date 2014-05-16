import subprocess


def run(cmd):
    cmd = shlex.split(cmd)
    subprocess.check_call(cmd)

def dictzip(d1,d2):
  for k,v1 in d1.items():
    v2 = d2[k]
    yield (k,v1,v2)
