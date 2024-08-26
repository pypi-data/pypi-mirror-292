from trussit.main import GUI
import subprocess
import sys

def check_and_install_tkinter():
    try:
        import tkinter
    except ImportError:
        try:
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'python3-tk'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"An error occurred during installation: Report a Bug")
        except Exception as e:
            print(f"An unexpected error occurred: Report a Bug")

if __name__ == "__main__":
    check_and_install_tkinter()

