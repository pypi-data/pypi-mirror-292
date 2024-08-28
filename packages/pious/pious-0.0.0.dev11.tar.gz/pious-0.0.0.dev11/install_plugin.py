import os
from os import path as osp
import venv
import subprocess
from argparse import ArgumentParser
import shutil
import sys

PIOUS_ROOT = osp.abspath(osp.dirname(__name__))

PIO_INSTALL_DIR = r"C:\PioSOLVER"
PLUGINS_DIR = osp.join(PIO_INSTALL_DIR, "Plugins")
PIOUS_PLUGIN_MENU_FILE = osp.join(PLUGINS_DIR, "Pious.txt")
PIOUS_PLUGIN_DIR = osp.join(PLUGINS_DIR, "PiousPlugin")
PIOUS_PLUGIN_BAT_FILE = osp.join(PIO_INSTALL_DIR, "PiousPlugin.bat")
PIOUS_PLUGIN_PY_FILE = osp.join(PIOUS_PLUGIN_DIR, "pious_plugin.py")
PIOUS_PLUGIN_VENV = osp.join(PIOUS_PLUGIN_DIR, "venv_pious")
PIO_PLUGIN_VENV_PIP = osp.join(PIOUS_PLUGIN_VENV, "Scripts", "pip.exe")


def pip_install_pious(local=True):
    if local:
        subprocess.run([PIO_PLUGIN_VENV_PIP, "install", "-e", PIOUS_ROOT])
    else:
        subprocess.run([PIO_PLUGIN_VENV_PIP, "install", "pious"])


def install():
    if not osp.isdir(PIO_INSTALL_DIR):
        raise RuntimeError("No such directory as", PIO_INSTALL_DIR)

    if not osp.isdir(PLUGINS_DIR):
        print(f"No Plugins directory at {PLUGINS_DIR}...creating it")
        os.makedirs(PLUGINS_DIR)

    if not osp.isfile(PIOUS_PLUGIN_MENU_FILE):
        print(f"Copying menu file to {PIOUS_PLUGIN_MENU_FILE}")
        shutil.copyfile(
            osp.join(PIOUS_ROOT, "plugin", "Pious.txt"), PIOUS_PLUGIN_MENU_FILE
        )

    if not osp.isdir(PIOUS_PLUGIN_DIR):
        print(f"Copying Pious Plugin to {PIOUS_PLUGIN_DIR}")
        shutil.copytree(osp.join(PIOUS_ROOT, "plugin", "PiousPlugin"), PIOUS_PLUGIN_DIR)
    else:
        if not osp.isfile(PIOUS_PLUGIN_PY_FILE):
            print(f"Copying pious_plugin.py to {PIOUS_PLUGIN_PY_FILE}")
            shutil.copyfile(
                osp.join(PIOUS_ROOT, "plugin", "PiousPlugin", "pious_plugin.py"),
                PIOUS_PLUGIN_PY_FILE,
            )
        if not osp.isfile(PIOUS_PLUGIN_BAT_FILE):
            print(f"Copying PiousPlugin.bat to {PIOUS_PLUGIN_BAT_FILE}")
            shutil.copyfile(
                osp.join(PIOUS_ROOT, "plugin", "PiousPlugin", "PiousPlugin.bat"),
                PIOUS_PLUGIN_BAT_FILE,
            )

    if not osp.isfile(PIOUS_PLUGIN_PY_FILE):
        raise RuntimeError(f"Could not find file {PIOUS_PLUGIN_PY_FILE}")

    if not osp.isfile(PIOUS_PLUGIN_BAT_FILE):
        raise RuntimeError(f"Could not find file {PIOUS_PLUGIN_BAT_FILE}")

    if not osp.isdir(PIOUS_PLUGIN_VENV):
        print(f"Creating a virtual environment: {PIOUS_PLUGIN_VENV}...")
        venv.create(PIOUS_PLUGIN_VENV, with_pip=True)
        print(f"Installing Pious...")
        pip_install_pious()


def uninstall(hard=False):
    if not osp.exists(PIOUS_PLUGIN_DIR):
        print("Cannot uninstall: no files to uninstall")
    elif hard:
        # Ensure that this is the correct place to uninstall
        print(f"Completely remove all files in {PIOUS_PLUGIN_DIR}?")
        r = input("  [Y/n] ").strip().lower()
        response = r.lower()
        if response in ("y", "yes"):
            shutil.rmtree(PIOUS_PLUGIN_DIR)
        elif response in ("n", "no"):
            pass
        else:
            print(f"Unrecognized option: '{r}'. Aborting")
            sys.exit(1)
    else:
        if osp.isfile(PIOUS_PLUGIN_BAT_FILE):
            os.remove(PIOUS_PLUGIN_BAT_FILE)
        if osp.isfile(PIOUS_PLUGIN_PY_FILE):
            os.remove(PIOUS_PLUGIN_PY_FILE)
        if osp.isfile(PIOUS_PLUGIN_MENU_FILE):
            os.remove(PIOUS_PLUGIN_MENU_FILE)


def main():
    global PIO_INSTALL_DIR
    parser = ArgumentParser()
    parser.add_argument(
        "--reinstall",
        action="store_true",
        help="Remove plugin if it exists and (re)install",
    )
    parser.add_argument(
        "--uninstall", action="store_true", help="Remove all plugin files"
    )
    parser.add_argument(
        "--pio_install_location",
        default=r"C:\PioSOLVER",
        help="Location where PioSOLVER is installed",
    )
    parser.add_argument("--reinstall_pious", action="store_true")
    args = parser.parse_args()

    PIO_INSTALL_DIR = args.pio_install_location

    if args.uninstall:
        uninstall()
    elif args.reinstall:
        uninstall()
        install()
    else:
        install()

    if args.reinstall_pious:
        subprocess.run([PIO_PLUGIN_VENV_PIP, "uninstall", "pious"])
        pip_install_pious()


if __name__ == "__main__":
    main()
