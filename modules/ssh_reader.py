import subprocess

class SSHReader(object):
    def __init__(self, ip, port=22):
        self.ip = ip
        self.port = port

    def read(self):
        ssh_command = """
python -c "import psutil;m=1024*1024;c=psutil.cpu_percent(interval=5);t=psutil.TOTAL_PHYMEM/m;u=(psutil.used_phymem()-psutil.cached_phymem())/m;vt=psutil.total_virtmem()/m;vu=psutil.used_virtmem()/m;print c,t,u,vt,vu"
"""
        process = subprocess.Popen("ssh -o ConnectTimeout=10 -p %d %s '%s'" % (self.port, self.ip, ssh_command), shell=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output,stderr = process.communicate()
        return [float(r) for r in output.strip().split(' ')]
