import os

def is_run_in_docker() -> bool:
    # https://stackoverflow.com/a/43879407/8302811
    return os.environ.get("DOCKER", "").lower() in ("yes", "y", "on", "true", "1")


if __name__ == "__main__":
    print(is_run_in_docker())