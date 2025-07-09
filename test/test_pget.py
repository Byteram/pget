#!/usr/bin/env python3

import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open


sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from main import (
    setup_pget_directories,
    download_github_repo,
    install_app,
    remove_app,
    list_apps,
    upgrade_app
)

class TestPgetDirectories(unittest.TestCase):
    @patch('pathlib.Path.home')
    @patch('pathlib.Path.mkdir')
    def test_setup_pget_directories(self, mock_mkdir, mock_home):
        # Arrange
        mock_home.return_value = Path("/home/test")
        # Act
        pget_home, bin_dir = setup_pget_directories()
        # Assert
        self.assertEqual(pget_home, Path("/home/test/.pget"))
        self.assertEqual(bin_dir, Path("/home/test/.pget/bin"))
        mock_mkdir.assert_called_with(parents=True, exist_ok=True)

class TestDownloadGitHubRepo(unittest.TestCase):
    @patch('urllib.request.urlopen')
    def test_download_github_repo_success(self, mock_urlopen):
        # Arrange
        mock_response = MagicMock()
        mock_response.read.return_value = b"fake zip content"
        mock_urlopen.return_value.__enter__.return_value = mock_response
        # Act
        result = download_github_repo("test-app")
        # Assert
        self.assertEqual(result, b"fake zip content")
        mock_urlopen.assert_called_once_with(
            "https://github.com/pynosaur/test-app/archive/refs/heads/main.zip"
        )
    @patch('urllib.request.urlopen')
    def test_download_github_repo_404(self, mock_urlopen):
        # Arrange
        from urllib.error import HTTPError
        mock_urlopen.side_effect = HTTPError(
            "https://github.com/pynosaur/test-app/archive/refs/heads/main.zip",
            404, "Not Found", {}, None
        )
        # Act
        result = download_github_repo("test-app")
        # Assert
        self.assertIsNone(result)

class TestInstallApp(unittest.TestCase):
    @patch('main.setup_pget_directories')
    @patch('main.download_github_repo')
    @patch('tempfile.TemporaryDirectory')
    @patch('zipfile.ZipFile')
    @patch('shutil.copytree')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.chmod')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.iterdir')
    @patch('pathlib.Path.read_text')
    @patch('builtins.print')
    @patch('sys.stderr.write')
    def test_install_single_file_app(self, mock_stderr, mock_print, mock_read_text, mock_iterdir, mock_exists, mock_chmod, mock_file, mock_copytree, mock_zipfile, mock_tempdir, mock_download, mock_setup):
        # Arrange
        mock_setup.return_value = (Path("/home/test/.pget"), Path("/home/test/.pget/bin"))
        mock_download.return_value = b"fake zip content"
        mock_tempdir.return_value.__enter__.return_value = "/tmp/test"
        # Provide enough values for all exists() calls: app_path, app_dir, app_files_dir
        mock_exists.side_effect = [False, True, False]  # app_path doesn't exist, app_dir exists, app_files_dir doesn't exist
        mock_iterdir.return_value = [MagicMock(name="main.py")]
        mock_read_text.return_value = "print('Hello World')"
        # Act
        result = install_app("test-app")
        # Assert
        self.assertTrue(result)
        mock_file.assert_called()
        mock_chmod.assert_called()
        call_args = mock_chmod.call_args
        self.assertEqual(call_args[0][1], 0o755)
    
    @patch('main.setup_pget_directories')
    @patch('pathlib.Path.exists', return_value=True)
    @patch('builtins.print')
    def test_install_app_already_installed(self, mock_print, mock_exists, mock_setup):
        # Arrange
        mock_setup.return_value = (Path("/home/test/.pget"), Path("/home/test/.pget/bin"))
        # Act
        result = install_app("test-app")
        # Assert
        self.assertTrue(result)
    
    @patch('main.setup_pget_directories')
    @patch('main.download_github_repo')
    @patch('sys.stderr.write')
    def test_install_app_not_found(self, mock_stderr, mock_download, mock_setup):
        # Arrange
        mock_setup.return_value = (Path("/home/test/.pget"), Path("/home/test/.pget/bin"))
        mock_download.return_value = None
        # Act
        result = install_app("non-existent-app")
        # Assert
        self.assertFalse(result)

class TestRemoveApp(unittest.TestCase):
    @patch('main.setup_pget_directories')
    @patch('warnings.warn')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.unlink')
    @patch('shutil.rmtree')
    @patch('builtins.print')
    def test_remove_app_success(self, mock_print, mock_rmtree, mock_unlink, mock_exists, mock_warn, mock_setup):
        # Arrange
        mock_setup.return_value = (Path("/home/test/.pget"), Path("/home/test/.pget/bin"))
        mock_exists.side_effect = [True, True]  # app_path exists, app_files_dir exists
        # Act
        remove_app("test-app")
        # Assert
        mock_unlink.assert_called_once()
        mock_warn.assert_not_called()
        mock_rmtree.assert_called()
    
    @patch('main.setup_pget_directories')
    @patch('warnings.warn')
    @patch('pathlib.Path.exists', return_value=False)
    def test_remove_app_not_installed(self, mock_exists, mock_warn, mock_setup):
        # Arrange
        mock_setup.return_value = (Path("/home/test/.pget"), Path("/home/test/.pget/bin"))
        # Act
        remove_app("test-app")
        # Assert
        mock_warn.assert_called_once()

class TestListApps(unittest.TestCase):
    @patch('main.setup_pget_directories')
    @patch('builtins.print')
    @patch('pathlib.Path.exists', return_value=True)
    @patch('pathlib.Path.iterdir')
    @patch('os.access', return_value=True)
    def test_list_apps_with_apps(self, mock_access, mock_iterdir, mock_exists, mock_print, mock_setup):
        # Arrange
        mock_setup.return_value = (Path("/home/test/.pget"), Path("/home/test/.pget/bin"))
        mock_app1 = MagicMock()
        mock_app1.name = "app1"
        mock_app1.is_file.return_value = True
        mock_app2 = MagicMock()
        mock_app2.name = "app2"
        mock_app2.is_file.return_value = True
        mock_iterdir.return_value = [mock_app1, mock_app2]
        # Act
        list_apps()
        # Assert
        mock_print.assert_called()
    
    @patch('main.setup_pget_directories')
    @patch('builtins.print')
    @patch('pathlib.Path.exists', return_value=False)
    def test_list_apps_no_apps(self, mock_exists, mock_print, mock_setup):
        # Arrange
        mock_setup.return_value = (Path("/home/test/.pget"), Path("/home/test/.pget/bin"))
        # Act
        list_apps()
        # Assert
        mock_print.assert_called_with("No applications installed.")

class TestUpgradeApp(unittest.TestCase):
    @patch('main.setup_pget_directories')
    @patch('main.download_github_repo')
    @patch('tempfile.TemporaryDirectory')
    @patch('zipfile.ZipFile')
    @patch('shutil.copytree')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.chmod')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.iterdir')
    @patch('pathlib.Path.read_text')
    @patch('builtins.print')
    @patch('sys.stderr.write')
    def test_upgrade_app_success(self, mock_stderr, mock_print, mock_read_text, mock_iterdir, mock_exists, mock_chmod, mock_file, mock_copytree, mock_zipfile, mock_tempdir, mock_download, mock_setup):
        # Arrange
        mock_setup.return_value = (Path("/home/test/.pget"), Path("/home/test/.pget/bin"))
        mock_download.return_value = b"fake zip content"
        mock_tempdir.return_value.__enter__.return_value = "/tmp/test"
        # Provide enough values for all exists() calls: app_path, app_dir, app_files_dir
        mock_exists.side_effect = [True, True, False]  # app_path exists, app_dir exists, app_files_dir doesn't exist
        mock_iterdir.return_value = [MagicMock(name="main.py")]
        mock_read_text.return_value = "print('Updated Hello World')"
        # Act
        result = upgrade_app("test-app")
        # Assert
        self.assertTrue(result)
        mock_file.assert_called()
        mock_chmod.assert_called()
        call_args = mock_chmod.call_args
        self.assertEqual(call_args[0][1], 0o755)
    
    @patch('main.setup_pget_directories')
    @patch('builtins.print')
    @patch('pathlib.Path.exists', return_value=False)
    def test_upgrade_app_not_installed(self, mock_exists, mock_print, mock_setup):
        # Arrange
        mock_setup.return_value = (Path("/home/test/.pget"), Path("/home/test/.pget/bin"))
        # Act
        result = upgrade_app("test-app")
        # Assert
        self.assertFalse(result)
        mock_print.assert_called()

if __name__ == '__main__':
    unittest.main() 