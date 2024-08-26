import os


def download(url, out_path):
    if os.path.isdir(out_path):
        raise ValueError(f"Output path is a directory: {out_path}")
    dir = os.path.dirname(out_path)
    if not os.path.exists(dir):
        os.mkdir(dir)
    os.system(f"curl {url} -o {out_path} -L")
