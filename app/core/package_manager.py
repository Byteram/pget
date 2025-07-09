#!/usr/bin/env python3

import os
import sys
import zipfile
import tempfile
import warnings
import urllib.request
import subprocess
import shutil
from pathlib import Path


def setup_pget_directories():
    """Creates the pget home directory and bin directory"""
    pget_home = Path.home() / ".pget"
    bin_dir = pget_home / "bin"
    
    bin_dir.mkdir(parents=True, exist_ok=True)
    
    return pget_home, bin_dir


def download_github_repo(app_name):
    """Downloads a GitHub repository as a ZIP file"""
    url = f"https://github.com/pynosaur/{app_name}/archive/refs/heads/main.zip"
    
    try:
        with urllib.request.urlopen(url) as response:
            return response.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def build_with_bazel(app_dir):
    """Builds the application using Bazel"""
    try:
        # Change to the app directory
        original_dir = os.getcwd()
        os.chdir(app_dir)
        
        # First, query for available targets to find the binary target
        print("Querying Bazel targets...")
        result = subprocess.run(
            ["bazel", "query", "//app:*"],
            capture_output=True,
            text=True,
            check=True
        )
        
        targets = result.stdout.strip().split('\n')
        binary_targets = []
        
        # Look for binary targets (exclude BUILD.bazel, main.py, etc.)
        for target in targets:
            if target.endswith(':yday') or target.endswith(':pget_bin') or target.endswith(':yday_bin'):
                binary_targets.append(target)
        
        if not binary_targets:
            # If no specific binary targets found, try the app target
            binary_targets = ["//app:app"]
        
        # Build the first binary target found
        target_to_build = binary_targets[0]
        print(f"Building target: {target_to_build}")
        
        result = subprocess.run(
            ["bazel", "build", target_to_build],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Look for the binary in bazel-bin/app/
        bazel_bin_dir = app_dir / "bazel-bin" / "app"
        if bazel_bin_dir.exists():
            # Look for executable files
            for item in bazel_bin_dir.iterdir():
                if item.is_file() and os.access(item, os.X_OK):
                    return item
                elif item.is_file() and not item.suffix:  # No extension, likely binary
                    return item
        
        # If not found, try alternative paths
        possible_paths = [
            app_dir / "bazel-bin" / "app" / "app",
            app_dir / "bazel-bin" / "app" / "pget_bin",
            app_dir / "bazel-bin" / "app" / "yday",
            app_dir / "bazel-bin" / "app" / "yday_bin"
        ]
        
        for path in possible_paths:
            if path.exists() and path.is_file():
                return path
        
        # If still not found, look for any file in bazel-bin/app/
        if bazel_bin_dir.exists():
            files = list(bazel_bin_dir.glob("*"))
            if files:
                return files[0]  # Return the first file found
        
        raise RuntimeError("No binary found in bazel-bin directory")
        
    except subprocess.CalledProcessError as e:
        print(f"Bazel build failed: {e.stderr}")
        return None
    except Exception as e:
        print(f"Error during Bazel build: {e}")
        return None
    finally:
        # Change back to original directory
        os.chdir(original_dir)


def install_app(app_name, compile_binary=False):
    """Installs an application to ~/.pget/bin/"""
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
    
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = Path(temp_dir) / f"{app_name}.zip"
        with open(zip_path, "wb") as f:
            f.write(zip_data)
        
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)
        
        extracted_dir = Path(temp_dir) / f"{app_name}-main"
        app_dir = extracted_dir / "app"
        
        if not app_dir.exists():
            sys.stderr.write(f"ERROR: The application {app_name} has no candidate.\n")
            return False
        
        if compile_binary:
            print(f"Compiling {app_name} with Bazel...")
            binary_path = build_with_bazel(extracted_dir)
            if binary_path is None:
                sys.stderr.write(f"ERROR: Failed to compile {app_name} with Bazel.\n")
                return False
            
            # Copy the binary to the bin directory
            shutil.copy2(binary_path, app_path)
            os.chmod(app_path, 0o755)
            print(f"Successfully compiled and installed {app_name} to {app_path}")
            return True
        else:
            # Original script installation logic
            # Check if it's a single-file app (just main.py)
            app_files = list(app_dir.iterdir())
            if len(app_files) == 1 and app_files[0].name == "main.py":
                # Single-file app - return just the content
                with open(app_path, "w") as f:
                    f.write("#!/usr/bin/env python3\n")
                    f.write(app_files[0].read_text())
            else:
                # Multi-file app (including those with subdirectories like core/, utils/, etc.)
                # Return the entire directory as a string path
                app_files_dir = bin_dir / f"{app_name}_files"
                
                # Remove existing files if upgrading
                if app_files_dir.exists():
                    shutil.rmtree(app_files_dir)
                
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
    """Removes an installed application"""
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
    """Lists all installed applications"""
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


def upgrade_app(app_name, compile_binary=False):
    """Upgrades an installed application to the latest version"""
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
    
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = Path(temp_dir) / f"{app_name}.zip"
        with open(zip_path, "wb") as f:
            f.write(zip_data)
        
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)
        
        extracted_dir = Path(temp_dir) / f"{app_name}-main"
        app_dir = extracted_dir / "app"
        
        if not app_dir.exists():
            sys.stderr.write(f"ERROR: The application {app_name} has no candidate.\n")
            return False
        
        if compile_binary:
            print(f"Compiling {app_name} with Bazel...")
            binary_path = build_with_bazel(extracted_dir)
            if binary_path is None:
                sys.stderr.write(f"ERROR: Failed to compile {app_name} with Bazel.\n")
                return False
            
            # Copy the binary to the bin directory
            shutil.copy2(binary_path, app_path)
            os.chmod(app_path, 0o755)
            print(f"Successfully compiled and upgraded {app_name} to {app_path}")
            return True
        else:
            # Original script upgrade logic
            # Check if it's a single-file app (just main.py)
            app_files = list(app_dir.iterdir())
            if len(app_files) == 1 and app_files[0].name == "main.py":
                # Single-file app
                with open(app_path, "w") as f:
                    f.write("#!/usr/bin/env python3\n")
                    f.write(app_files[0].read_text())
            else:
                # Multi-file app
                app_files_dir = bin_dir / f"{app_name}_files"
                
                # Remove existing files if upgrading
                if app_files_dir.exists():
                    shutil.rmtree(app_files_dir)
                
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