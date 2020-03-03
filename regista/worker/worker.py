import subprocess


if __name__ == "__main__":

    cmd = "ssh -f {server} 'bash ~/git/regista/bin/run_worker.sh'"

    server_list = [
        "ec2-3-87-14-67.compute-1.amazonaws.com",
    ]
    
    for server in server_list:
        subprocess.call(cmd.format(server), shell=True)
