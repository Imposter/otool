import os
import string

from time import sleep
from getpass import getpass
from inspect import getfullargspec
from platform import platform
from fnmatch import fnmatch

from api.session import APISession
from api.services.entitlements import EntitlementService
from api.services.downloads import DownloadService

from installer.frostbite import FrostbiteInstaller

class OriginCLI(object):
    def __init__(self):
        parser.add_argument("-E", "--email",
                            type=str,
                            help="Origin Account Email",
                            required=False)
        parser.add_argument("-P", "--password",
                            type=str,
                            help="Origin Account Password",
                            required=False)
        parser.add_argument("-v", "--verbose",
                            type=str,
                            help="Verbosity",
                            required=False)

        self._args = parser.parse_args()

        # Create API instance
        self._api = APISession()

    def run(self):
        if self._args.command is None:
            parser.print_help()
            return

        # Get account details if they were not provided in the command-line
        if not self._args.email:
            self._args.email = input("Origin email: ")
        if not self._args.password:
            self._args.password = input("Origin password: ")

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

        # Run command
        func = self._args.func
        func_args = getfullargspec(func).args[1:]
        valid_args = dict(filter(lambda x: x[0] in func_args, vars(self._args).items()))
        func(self, **valid_args)

    @subcommand(description="Get a list of owned games and their IDs")
    def games(self):
        # Select games
        owned_games = self._entitlement_service.get_owned_games()
        owned_games = list(filter(lambda x: x["@offerType"] == "Base Game", owned_games["offers"]["offer"]))

        print("Owned games: ")
        for game in owned_games:
            game_id = game["@offerId"]
            game_name = game["localizableAttributes"]["displayName"]
            print(f"- {game_name} (ID: {game_id})")

    @subcommand(description="Get a list of entitlements matching a wildcard", args=[
        argument("-w", "--wildcard", type=str, help="Wildcard to match", required=True),
    ])
    def entitlements(self, wildcard):
        # Get entitlements
        entitlements = self._entitlement_service.get_entitlements()["entitlements"]

        print("Entitled to products: ")
        for entitlement in entitlements:
            if "entitlementTag" in entitlement and "productId" in entitlement:
                tag = entitlement["entitlementTag"]
                product_id = entitlement["productId"]
                if fnmatch(tag, wildcard):
                    print(f"- {tag} (ID: {product_id})")

    @subcommand(description="Get a list of all games and their IDs")
    def allgames(self):
        # Get all standard and premium games
        standard_games = self._entitlement_service.get_standard_games()
        premium_games = self._entitlement_service.get_premium_games()

        def print_vault_games(games):
            for game in standard_games["game"]:
                if len(game["basegames"]["basegame"]) > 0:
                    game_id = game["basegames"]["basegame"][0]
                    game_name = game["displayName"]
                    print(f"- {game_name} (ID: {game_id})")
                    if "extracontent" in game["extracontents"]:
                        game_content = game["extracontents"]["extracontent"]
                        print("- Extra Content: ")
                        for content in game_content:
                            print(f"\t- {content}")

        print("Standard games: ")
        print_vault_games(standard_games)
        print("")

        print("Premium games: ")
        print_vault_games(premium_games)
        print("")

    @subcommand(description="Install Origin game and extra content by ID", args=[
        argument("-i", "--installer", type=str, help="Installer to use (fb)", required=True),
        argument("-g", "--game", type=str, help="Game Product ID", required=True),
        argument("-d", "--path", type=str, help="Download path", required=True),
        argument("-e", "--extracontent", type=str, nargs="+", help="Extra Content IDs", required=False),
        argument("-r", "--remove", type=bool, help="Remove downloaded content after installation", required=False)
    ])
    def install(self, installer, game, path, extracontent, remove=False):
        # Check if a valid installer was provided
        installer_instance = None
        if installer == "fb":
            installer_instance = FrostbiteInstaller(self._entitlement_service, self._download_service)

        if not installer_instance:
            print(f"Invalid installer {installer}")
            return

        # Install base game
        installer_instance.install_game(game, path, remove)

        # Install DLCs
        for content in extracontent or list():
            installer_instance.install_dlc(content, path, remove)

        print("Installation complete")

if __name__ == "__main__":
    print("===============================================================")
    print("OTool")
    print("By Imposter")
    print("===============================================================")
    print("")

    cli = OriginCLI()
    cli.run()
