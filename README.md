# OTool
OTool is designed as an open source command-line utility for downloading your Battlefield 3 and the associated expansion packs for Venice Unleashed. It allows you to easily download and install your purchased products from the Origin platform without needing to have Origin installed on your system.

This lightweight and simple interface means you do not need to have X servers, or out-of-date versions of Origin installed on your Linux system in order to use it.

## What you can do
- Install Battlefield 3 and associated expansion packs from the Origin platform

## What you cannot do
- Download/play games that you are not entitled to
- Play games without having Origin installed
- Perform updates on downloaded games

## How to use it
There are a few prerequisites that must be satisfied in order to use this application. As a first step, you must ensure that a version of Python 3 is installed on your system. Furthermore, you must install the required Python packages found in `requirements.txt`. This can be done through `pip3` using `pip3 install -r requirements.txt`.

## Usage
In order to use this application, you must provide your Origin email address and password. This can be done using the `-E` and `-P` flags. If you do not provide these flags in the command-line, you will be prompted at startup to enter them. You must also provide a path to the directory you wish to download and install BF3 and the DLCs to. This can be done using the `-d` flag. Optionally, you can remove the temporary files after downloading using the `-r` flag.
- `python3 otool.py -E <email> -P <password> -d <path>`
- `python3 otool.py -d <path>`

If you have Two-Factor Authentication enabled on the account, you will be prompted to select the method you wish to receive the code with. Once you select the method, you must wait to receive the code and enter it once you have received it.

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
