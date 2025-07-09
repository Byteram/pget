# -*- coding: utf-8 -*-
#
# pget - Pure Python Package Manager
#
# Author: vvrmatos (@spacemany2k38)
# Date: 2025-07-09
# Description: Pure Python Package Manager
# License: CC0 1.0 Universal
#

#!/usr/bin/env python3

import os
import sys
import zipfile
import argparse
import tempfile
import warnings
import urllib.request

from pathlib import Path


def setup_pget_directories():
    pget_home = Path.home() / ".pget"
    bin_dir = pget_home / "bin"
    
    bin_dir.mkdir(parents=True, exist_ok=True)
    
    return pget_home, bin_dir


def download_github_repo(app_name):
    url = f"https://github.com/pynosaur/{app_name}/archive/refs/heads/main.zip"
    
    try:
        with urllib.request.urlopen(url) as response:
            return response.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def extract_app_directory(zip_data, app_name):
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = Path(temp_dir) / f"{app_name}.zip"
        with open(zip_path, "wb") as f:
            f.write(zip_data)
        
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)
        
        extracted_dir = Path(temp_dir) / f"{app_name}-main"
        app_dir = extracted_dir / "app"
        
        if not app_dir.exists():
            return None, None
        
        # Check if it's a single-file app (just main.py)
        app_files = list(app_dir.iterdir())
        if len(app_files) == 1 and app_files[0].name == "main.py":
            # Single-file app - return just the content
            return app_files[0].read_text(), None
        
        # Multi-file app - return the entire directory
        return None, app_dir


def install_app(app_name):
    pget_home, bin_dir = setup_pget_directories()
    
    app_path = bin_dir / app_name
    

    if app_path.exists():
        print(f"{app_name} is already installed at {app_path}")
        print("Use 'pget upgrade {app_name}' to update to the latest version.")
        return True
    
    print(f"Installing {app_name}...")
    
    zip_data = download_github_repo(app_name)
    if zip_data is None:
        sys.stderr.write(f"ERROR: The application {app_name} has no candidate.\n")
        return False
    
    main_py_content, app_dir = extract_app_directory(zip_data, app_name)
    if main_py_content is None and app_dir is None:
        sys.stderr.write(f"ERROR: The application {app_name} has no candidate.\n")
        return False
    
    if main_py_content is not None:
        # Single-file app
        with open(app_path, "w") as f:
            f.write("#!/usr/bin/env python3\n")
            f.write(main_py_content)
    else:
        # Multi-file app
        app_files_dir = bin_dir / f"{app_name}_files"
        
        # Remove existing files if upgrading
        if app_files_dir.exists():
            import shutil
            shutil.rmtree(app_files_dir)
        

        import shutil
        shutil.copytree(app_dir, app_files_dir)


        launcher_content = f"""#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add the app files directory to Python path
app_files_dir = Path(__file__).parent / "{app_name}_files"
sys.path.insert(0, str(app_files_dir))

# Import and run main
from main import main
if __name__ == '__main__':
    main()
"""
        
        with open(app_path, "w") as f:
            f.write(launcher_content)
    
    os.chmod(app_path, 0o755)
    
    print(f"Successfully installed {app_name} to {app_path}")
    return True


def remove_app(app_name):
    pget_home, bin_dir = setup_pget_directories()
    
    app_path = bin_dir / app_name
    app_files_dir = bin_dir / f"{app_name}_files"
    
    if app_path.exists():
        app_path.unlink()
        print(f"Successfully removed {app_name}")
        
        # Also remove the files directory if it exists (multi-file app)
        if app_files_dir.exists():
            import shutil
            shutil.rmtree(app_files_dir)
            print(f"Removed {app_name} files directory")
    else:
        warnings.warn(f"The application {app_name} is not installed.")


def list_apps():
    pget_home, bin_dir = setup_pget_directories()
    
    if not bin_dir.exists():
        print("No applications installed.")
        return
    
    apps = [f.name for f in bin_dir.iterdir() if f.is_file() and os.access(f, os.X_OK)]
    
    if not apps:
        print("No applications installed.")
        return
    
    print("Installed applications:")
    for app in sorted(apps):
        print(f"  {app}")


def upgrade_app(app_name):
    pget_home, bin_dir = setup_pget_directories()
    
    app_path = bin_dir / app_name
    
    if not app_path.exists():
        print(f"{app_name} is not installed. Use 'pget install {app_name}' to install it.")
        return False
    
    print(f"Upgrading {app_name}...")
    
    zip_data = download_github_repo(app_name)
    if zip_data is None:
        sys.stderr.write(f"ERROR: The application {app_name} has no candidate.\n")
        return False
    
    main_py_content, app_dir = extract_app_directory(zip_data, app_name)
    if main_py_content is None and app_dir is None:
        sys.stderr.write(f"ERROR: The application {app_name} has no candidate.\n")
        return False
    
    if main_py_content is not None:
        # Single-file app
        with open(app_path, "w") as f:
            f.write("#!/usr/bin/env python3\n")
            f.write(main_py_content)
    else:
        # Multi-file app
        app_files_dir = bin_dir / f"{app_name}_files"
        
        # Remove existing files if upgrading
        if app_files_dir.exists():
            import shutil
            shutil.rmtree(app_files_dir)
        
        # Copy all files from app directory
        import shutil
        shutil.copytree(app_dir, app_files_dir)
        
        # Create launcher script
        launcher_content = f"""#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add the app files directory to Python path
app_files_dir = Path(__file__).parent / "{app_name}_files"
sys.path.insert(0, str(app_files_dir))

# Import and run main
from main import main
if __name__ == '__main__':
    main()
"""
        
        with open(app_path, "w") as f:
            f.write(launcher_content)
    
    os.chmod(app_path, 0o755)
    
    print(f"Successfully upgraded {app_name} to {app_path}")
    return True


def main():
    parser = argparse.ArgumentParser(description="pget - Pure Python Package Manager")
    parser.add_argument("command", choices=["install", "remove", "list", "upgrade"], help="Command to execute")
    parser.add_argument("app_name", nargs="?", help="Application name")
    
    args = parser.parse_args()
    
    if args.command == "install":
        if not args.app_name:
            sys.stderr.write("ERROR: Application name required for install command.\n")
            sys.exit(1)
        success = install_app(args.app_name)
        if not success:
            sys.exit(1)
    
    elif args.command == "remove":
        if not args.app_name:
            sys.stderr.write("ERROR: Application name required for remove command.\n")
            sys.exit(1)
        remove_app(args.app_name)
    
    elif args.command == "upgrade":
        if not args.app_name:
            sys.stderr.write("ERROR: Application name required for upgrade command.\n")
            sys.exit(1)
        success = upgrade_app(args.app_name)
        if not success:
            sys.exit(1)
    
    elif args.command == "list":
        list_apps()


if __name__ == "__main__":
    main() 