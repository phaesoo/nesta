import subprocess


if __name__ == "__main__":
    server_list = [
        "ec2-3-87-14-67.compute-1.amazonaws.com",
    ]

    for server in server_list:
        subprocess.call(
            f"ssh -f {server} 'bash ~/git/absinthe/bin/run_worker.sh'",
            shell=True
        )
