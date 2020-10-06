import os

from abc import ABC, abstractmethod
from platform import platform
from tqdm import tqdm

from lib import zip_extractor

class Installer(ABC):
    def __init__(self, entitlement_service, download_service):
        self._entitlement_service = entitlement_service
        self._download_service = download_service

        self._cache_data()

    def _cache_data(self):
        self._owned_games = self._entitlement_service.get_owned_games()
        self._entitlements = self._entitlement_service.get_entitlements()

    def _is_owned_game(self, game_id):
        owned_games = self._entitlement_service.get_owned_games()
        owned_games = list(filter(lambda x: x["@offerType"] == "Base Game", owned_games["offers"]["offer"]))
        for game in owned_games:
            if game["@offerId"] == game_id:
                return True
        return False

    def _is_owned_dlc(self, content_id):
        for entitlement in self._entitlements["entitlements"]:
            if "productId" in entitlement and entitlement["productId"] == content_id and entitlement["status"] == "ACTIVE":
                return True
        return False

    def _download_product(self, product, path):
        path = os.path.abspath(path)
        if not os.path.isdir(path):
            os.makedirs(path)

        print(f"Downloading {product} to {path}...")

        # Create download
        download = self._download_service.create_download(product, path)
        if os.path.isfile(download.path):
            print(f"Found existing file \"{download.path}\", resuming...")

        # Start downloading
        progress = tqdm(total=download.size-download.offset, unit='B', unit_scale=True, position=0, leave=True)
        for bytes_downloaded in download.start():
            progress.update(bytes_downloaded)
        progress.close()

        print()
        print("Download complete")

        return download.path

    def _extract_product(self, archive_path, destination_path):
        print(f"Extracting {archive_path} to {destination_path}...")
        if not os.path.isdir(destination_path):
            os.makedirs(destination_path)
        
        extractor = zip_extractor.ZipExtractor(archive_path)
        progress = tqdm(total=extractor.uncompressed_size, unit='B', unit_scale=True, position=0, leave=True)
        for bytes_extracted in extractor.start(destination_path):
            progress.update(bytes_extracted)
        progress.close()

        print()
        print("Extraction complete")

        return archive_path

    # TODO: Registry support
    # ...

    @abstractmethod
    def install_game(self, game_id, destination_path, remove_data):
        return

    @abstractmethod
    def install_dlc(self, content_id, destination_path, remove_data):
        return