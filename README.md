# OTool
OTool is designed as an open source command-line utility for downloading your Origin games. It allows you to easily view, download and install your purchased products from the Origin platform without needing to have Origin installed on your system.

This lightweight and simple interface means you do not need to have X servers, or out-of-date versions of Origin installed on your Linux system in order to use it.

## What you can do
- View owned games and their IDs
- View all products, including DLCs on Origin and their IDs
- Install products from the Origin platform

## What you cannot do
- Download/play games that you are not entitled to
- Play games without having Origin installed
- Perform updates on downloaded games

## How to use it
There are a few prerequisites that must be satisfied in order to use this application. As a first step, you must ensure that a version of Python 3 is installed on your system. Furthermore, you must install the required Python packages found in `requirements.txt`. This can be done through `pip3` using `pip3 install -r requirements.txt`.

## Logging in
In order to use this application, you must provide your Origin email address and password. This can be done using the `-E` and `-P` flags.
- `python3 otool.py -E <email> -P <password> <command>`

If you do not provide your credentials through the command-line flags, you will be prompted to once the utility has started.
- `python3 otool.py <command>`

If you have Two-Factor Authentication enabled on the account, you will be prompted to select the method you wish to receive the code with. Once you select the method, you must wait to receive the code and enter it once you have received it.

## Commands
There are a few commands provided by the application:
- `games` provides you with a list of the base games (and their IDs) entitled to your Origin account.
  - `python3 otool.py games`
- `entitlements` provides you with a list of games and DLCs (with their IDs) that you are entitled to on your Origin account.
  - `python3 otool.py entitlements -w <wildcard>`
  - An example command to find DLC entitlements looks like this:
    - `python3 otool.py entitlements -w BF3:PC:XPACK*`
- `allgames` provides you with a list of all games (and their IDs) available on the Origin platform. This can be used to obtain a list of DLCs for a certain game.
  - `python3 otool.py allgames`
- `install` allows you to install a game and its DLCs provided you have the respective IDs. 
  - `python3 otool.py install -i <installer> -g "<game_id>" -e "<dlc_id1>" "<dlc_id2>" ... -d <installation_path>`
  - The available installer options are:
    - Frostbite (`fb`)
  - An example installation command for `BF3` looks like this:
    - `python3 otool.py install -i "fb" -g "DR:225064100" -e "OFB-EAST:50631" "OFB-EAST:51080" "OFB-EAST:55172" "OFB-EAST:109546437" -d "~/bf3"`
      - `OFB-EAST:50631`: Close Quarters (XPACK2 - Non-premium)
      - `OFB-EAST:51080`: Armored Kill (XPACK3 - Non-premium)
      - `OFB-EAST:55172`: Aftermath (XPACK4 - Non-premium)
      - `OFB-EAST:109546437`: End Game (XPACK5 - Non-premium)
    - You can use the `entitlements` command provided above to find the DLC IDs for your account.


## Disclaimer
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.

#
All trademarks and registered trademarks are the property of their respective owners.
