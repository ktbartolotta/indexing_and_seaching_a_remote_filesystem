import os
import paramiko

from whoosh.fields import *
from whoosh.index import create_in, open_dir


ssh = paramiko.SSHClient()
ssh.load_system_host_keys()
ssh.set_missing_host_key_policy(
    paramiko.AutoAddPolicy())
ssh.connect("host")

schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT)

adhoc = "/apps/ppl/adhoc/"


def process_directory(dir_path, spaces):

    file_match = re.compile(
        r"^[A-Za-z1-9_]+(\.sql|\.log|\.bat|\.py|\.sh)?$", re.IGNORECASE)
    print("".join([spaces, dir_path]))
    stdin, stdout, stderr = ssh.exec_command(
        "".join(["ls -p ", dir_path]))
    content = stdout.readlines()
    if len(content) > 0:
        for line in content:
            line = line.strip()
            if "arch/" not in dir_path and "exppadh/" not in dir_path:
                if line[-1] == "/":
                    process_directory(
                        "".join([dir_path, line]),
                        "".join([spaces, "\t"]))
                else:
                    if file_match.match(line):
                        print("".join([spaces, "\t(f) ", dir_path, line]))
                        index_file(
                            "".join([dir_path, line]), line)


def index_file(path, title):

    if not os.path.exists("index"):
        os.mkdir("index")
        ix = create_in("index", schema)
    else:
        ix = open_dir("index")

    stdin, stdout, stderr = ssh.exec_command(
        " ".join(["cat", path]))
    content = "".join(stdout.readlines())

    writer = ix.writer()
    writer.add_document(
        title=title.decode("utf-8"),
        path=path.decode("utf-8"),
        content=content.decode("utf-8"))
    writer.commit()


def main():
    process_directory(adhoc, "")


if __name__ == "__main__":
    main()
