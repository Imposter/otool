import os
import string

from argparse import ArgumentParser
from time import sleep
from getpass import getpass
from inspect import getfullargspec
from platform import platform
from fnmatch import fnmatch

from lib import utils

from api import origin
from api.session import APISession
from api.services.entitlements import EntitlementService
from api.services.downloads import DownloadService

from installer.frostbite import FrostbiteInstaller

class VOToolCLI(object):
    def __init__(self):
        parser = ArgumentParser()
        parser.add_argument("-E", "--email",
                            type=str,
                            help="Origin Account Email",
                            required=True)
        parser.add_argument("-P", "--password",
                            type=str,
                            help="Origin Account Password",
                            required=True)
        parser.add_argument("-d", "--path",
                            type=str,
                            help="BF3 installation path",
                            required=True)
        parser.add_argument("-r", "--remove",
                            type=bool,
                            help="Removes downloaded data after installation",
                            required=False)
        parser.add_argument("-v", "--verbose",
                            type=str,
                            help="Verbosity",
                            required=False)

        self._args = parser.parse_args()

        # Create API instance
        self._api = APISession()

    def run(self):
        # Login using provided email and password
        print(f"Logging in as: {self._args.email}")
        print("")

        def mfa_method_select(methods):
            print("Two-Factor Authentication is enabled on the account. Please choose one of the following methods:")
            for method in methods:
                print(f"- {method}")
            
            return input("Method: ")

        def mfa_key_select(method):
            return input("Security Code: ")

        self._api.login(self._args.email, self._args.password, mfa_method_select, mfa_key_select)
        print("Successfully logged in!")

        if self._args.verbose:
            print("NOTE: Please do not share the following access token with ANYONE under any circumstances. This is purely listed for development purposes.")
            print(f"Access Token: {self._api.access_token}")
            print("")

        # Create services
        self._entitlement_service = EntitlementService(self._api)
        self._download_service = DownloadService(self._api)

        # Get a list of all the games the account is entitled to
        owned_games = self._entitlement_service.get_owned_games()
        owned_games = list(filter(lambda x: x["@offerType"] == "Base Game", owned_games["offers"]["offer"]))

        bf3_game_id = None
        for game in owned_games:
            game_id = game["@offerId"]
            game_name = game["localizableAttributes"]["displayName"]

            # If the game is Battlefield 3, store the ID
            if game_name == "Battlefield 3™":
                bf3_game_id = game_id
                break

        if bf3_game_id is None:
            print("Could not find a copy of Battlefield 3 on this account.")
            return

        # Get entitlements for the account
        entitlements = self._entitlement_service.get_entitlements()["entitlements"]

        # Select the expansion packs that the account is entitled to
        bf3_xpack_ids = list()
        for entitlement in entitlements:
            if "entitlementTag" in entitlement and "productId" in entitlement:
                tag = entitlement["entitlementTag"]
                product_id = entitlement["productId"]
                if fnmatch(tag, "BF3:PC:XPACK*"):
                    bf3_xpack_ids.append(product_id)

        # Create an installer instance
        installer_instance = FrostbiteInstaller(self._entitlement_service, self._download_service)

        # Install base game
        installer_instance.install_game(bf3_game_id, self._args.path, self._args.remove)

        # Install DLCs
        for bf3_xpack_id in bf3_xpack_ids:
            installer_instance.install_dlc(bf3_xpack_id, self._args.path, self._args.remove)

        print("Installation complete")

if __name__ == "__main__":
    print("===============================================================")
    print("OTool by Imposter")
    print("This edition of OTool is designed for Venice Unleashed")
    print("Get VU at www.playvu.com")
    print("===============================================================")
    print("")

    cli = VOToolCLI()
    cli.run()