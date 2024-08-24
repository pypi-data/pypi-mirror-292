import os.path
import sys
import platform

arch = platform.machine().lower()
bin_path = os.path.join(os.path.dirname(__file__), f"await-{arch}")


def main():
    if not os.path.exists(bin_path):
        raise RuntimeError(f"Unknown CPU architecture: {arch}")
    os.execv(bin_path, sys.argv)


if __name__ == "__main__":
    main()