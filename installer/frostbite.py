import os
import shutil

from zipfile import ZipFile

from . import installer

class FrostbiteInstaller(installer.Installer):
    def __init__(self, entitlement_service, download_service):
        super().__init__(entitlement_service, download_service)

    def install_game(self, game_id, destination_path, remove_data=False):
        # Check if the user owns the game
        if not self._is_owned_game(game_id):
            raise Exception(f"This account is not entitled to {game_id}")

        # Download the game
        download_path = os.path.join(destination_path, "__Temp")
        archive_path = self._download_product(game_id, download_path)

        # Install the game
        self._extract_product(archive_path, destination_path)

        # Remove data
        if remove_data:
            shutil.rmtree(archive_path)

    def install_dlc(self, content_id, destination_path, remove_data=False):
        # Check if the user owns the DLC
        if not self._is_owned_dlc(content_id):
            raise Exception(f"This account is not entitled to {content_id}")

        # Download the DLC
        download_path = os.path.join(destination_path, "__Temp", "Updates")
        archive_path = self._download_product(content_id, download_path)

        # Get manifest content
        manifest = dict()
        with ZipFile(archive_path) as zip_file:
            with zip_file.open("package.mft") as manifest_file:
                for line in manifest_file:
                    args = str(line, "utf-8").split()
                    manifest[args[0]] = args[1]

        # Install the content
        install_path = os.path.join(destination_path, "Update", manifest["Name"])
        self._extract_product(archive_path, install_path)

        # Remove data
        if remove_data:
            shutil.rmtree(archive_path)