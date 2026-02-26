import subprocess

if __name__ == "__main__":
    cmd = (
        "uv",
        "run",
        "nuitka",
        "--standalone",
        "--onefile",
        "--show-progress",
        "--lto=yes",
        "--include-package=quas",
        "--include-package-data=quas",
        "--warn-unusual-code",
        "--output-filename=quas",
        "build/main.py",
    )
    subprocess.run(cmd)
