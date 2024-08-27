import os

current_dir = os.path.dirname(__file__)
static_dir = os.path.join(current_dir, "static")


with open(os.path.join(static_dir, "index.html"), "r") as f:
    print(f.read())