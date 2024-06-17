from os import environ
from pathlib import Path
from shlex import split
from argparse import ArgumentParser, RawDescriptionHelpFormatter

import webpolicies
import versions


class _Null:
    def __bool__(self):
        return False

    def __len__(self):
        return 0


Null = _Null()


parser = ArgumentParser(
    prog="showcase",
    formatter_class=RawDescriptionHelpFormatter,
    description="This minimalistic program turns any website or other document into a stand-alone application.",
    epilog=versions.__versions_msg__,
    argument_default=Null,
)

parser.add_argument(
    "url",
    action="store",
    help="The content url. If several are passed, the tab widget is "
         "automatically added and makes `--wg-tabs' redundant.",
    nargs="*",
    type=str
)

parser.add_argument(
    "-v", "--version",
    action="store_true",
    help="exit with the version of ShowCase Browser"
)

parser.add_argument(
    "-V", "--versions",
    action="store_true",
    help="exit with a detailed versions message"
)

parser.add_argument(
    "-U", "--skip-upgrades",
    action="store_true",
    help="skip the check for upgrades"
)

basic_wg_group = parser.add_argument_group(
    "Basic Widgets",
    description="Add optional basic widgets.",
)
basic_ks_group = parser.add_argument_group(
    "Basic Key Sequences",
    description="Add and define optional basic key sequences. "
                "The argument is passed as a string to a PyQt6.QKeySequence. "
                "Visit https://doc.qt.io/qt-6/qkeysequence.html#details for more information.",
)
home_group = parser.add_argument_group(
    "Home",
    "Add and define the Home functions.",
)
taps_group = parser.add_argument_group(
    "Tabs",
    description="Add and define the Tabs functions."
)
window_group = parser.add_argument_group(
    "Window",
    description="Window parameters"
)
com_group = parser.add_argument_group(
    "Communicator",
    description="Create a communicator for showcase."
)
com_addr_group = parser.add_argument_group(
    "Communicator Address",
    description="Define the communicator address. "
                "For the transmission or the server. "
                "The default is `127.0.0.3:51001'."
)
com_url_group = parser.add_argument_group(
    "Communicator Url Handle",
    description=""
)
com_ex_group = parser.add_argument_group(
    "Communicate Commands",
    description="Send the command and exit."
)
com_ex_group = com_ex_group.add_mutually_exclusive_group()
behavior_group = parser.add_argument_group(
    "Behavior",
    description="Web engine behavior attributes."
)
profile_group = parser.add_argument_group(
    "Local Profiles",
    description="Load the parameterization from a local file or environment variable. "
                "The text contained in a file, with the exception of lines beginning with "
                "`#', `*' or `:', is loaded as command line parameterization. Line breaks "
                "represent a parameter/argument separator, as do spaces."
)

try:
    basic_wg_group.add_argument(
        "--wg-url",
        action="store_true",
        help="Add the url entry.",
    )
    basic_wg_group.add_argument(
        "--wg-back",
        action="store_true",
        help="Add the back button.",
    )
    basic_wg_group.add_argument(
        "--wg-forward",
        action="store_true",
        help="Add the forward button.",
    )
    basic_wg_group.add_argument(
        "--wg-refresh",
        action="store_true",
        help="Add the refresh button.",
    )
    basic_wg_group.add_argument(
        "--wg-stop",
        action="store_true",
        help="Add the stop button.",
    )
except Exception:
    raise

try:
    basic_ks_group.add_argument(
        "--ks-url",
        action="store",
        help="Add a key sequence to put the focus on the url widget "
             "(e.g. `Ctrl+L').",
        metavar="<key sequence>",
    )
    basic_ks_group.add_argument(
        "--ks-back",
        action="store",
        help="Add a key sequence to trigger the back function "
             "(e.g. `Ctrl+Backspace').",
        metavar="<key sequence>",
    )
    basic_ks_group.add_argument(
        "--ks-forward",
        action="store",
        help="Add a key sequence to trigger the forward function "
             "(e.g. `Ctrl+Shift+Backspace').",
        metavar="<key sequence>",
    )
    basic_ks_group.add_argument(
        "--ks-refresh",
        action="store",
        help="Add a key sequence to trigger the refresh function "
             "(e.g. `Ctrl+R').",
        metavar="<key sequence>",
    )

    basic_ks_group.add_argument(
        "--ks-stop",
        action="store",
        help="Add a key sequence to trigger the stop load function "
             "(e.g. `Ctrl+X').",
        metavar="<key sequence>",
    )
except Exception:
    raise

try:
    home_group.add_argument(
        "--wg-home",
        action="store_true",
        help="Add the home button.",
    )
    home_group.add_argument(
        "--ks-home",
        action="store",
        help="Add a key sequence to trigger the home function "
             "(e.g. `Ctrl+H').",
        metavar="<key sequence>",
    )
    home_group.add_argument(
        "--home-url",
        action="store",
        help="Define the home url. [*] required for the upper functions",
        metavar="<url>",
    )
except Exception:
    raise

try:
    taps_group.add_argument(
        "--wg-tabs",
        action="store_true",
        help="Add the tabs widget.",
    )
    taps_group.add_argument(
        "--wg-tabs-close",
        action="store_true",
        help="Add the close button for each tab.",
    )
    taps_group.add_argument(
        "--ks-tabs-close",
        action="store",
        help="Add a key sequence to trigger the tab close function "
             "(e.g. `Ctrl+-').",
        metavar="<key sequence>",
    )
    taps_group.add_argument(
        "--wg-tabs-add",
        action="store_true",
        help="Add the add tab button.",
    )
    taps_group.add_argument(
        "--ks-tabs-add",
        action="store",
        help="Add a key sequence to trigger the tab add function "
             "(e.g. `Ctrl++').",
        metavar="<key sequence>",
    )
    taps_group.add_argument(
        "--tabs-default-url",
        action="store",
        help="Add a key sequence to trigger the tab close function "
             "(e.g. `Ctrl+-').",
    )
    taps_group.add_argument(
        "--tabs-default-label",
        action="store",
        help="Define a default tab label.",
    )
    taps_group.add_argument(
        "--tabs-dynamic-labels",
        action="store_true",
        help="Tablabels are obtained from the loaded pages.",
    )
    taps_group.add_argument(
        "--tabs-keep-last",
        action="store_true",
        help="It is not possible to close the last tab.",
    )
except Exception:
    raise

try:
    window_group.add_argument(
        "--window-title",
        action="store",
        help="Define the window title.",
    )
    window_group.add_argument(
        "--window-icon",
        action="store",
        help="Define the path to the window icon.",
    )
    window_group.add_argument(
        "--window-maxsize",
        action="store_true",
        help="Maximize the window at startup.",
    )
except Exception:
    raise

try:
    com_group.add_argument(
        "--com",
        action="store_true",
    )

    com_addr_group.add_argument(
        "--com-host",
        action="store",
        metavar="xxx.xxx.xxx.xxx",
    )
    com_addr_group.add_argument(
        "--com-port",
        action="store",
        metavar="port-number",
        type=int,
    )

    com_url_group.add_argument(
        "--com-try",
        action="store_true",
        help="Try to transfer the url to a communicator, "
             "start a showcase with the url and a communicator "
             "if not possible. "
             "With this flag only one url is allowed.",
    )
    com_url_group.add_argument(
        "--com-tab-append",
        action="store_true",
        help="If `--com-try' is successful and the tab widget is active, "
             "add the url as a new tab.",
    )
    com_url_group.add_argument(
        "--com-tab-index",
        action="store",
        help="If `--com-try' is successful and the tab widget is active, "
             "overwrite the url of tab `n'.",
        metavar="n",
        type=int,
    )

    com_ex_group.add_argument(
        "--com-back",
        action="store_true",
        help="Trigger the back function.",
    )
    com_ex_group.add_argument(
        "--com-forward",
        action="store_true",
        help="Trigger the forward function.",
    )
    com_ex_group.add_argument(
        "--com-reload",
        action="store_true",
        help="Trigger the reload function.",
    )
    com_ex_group.add_argument(
        "--com-home",
        action="store_true",
        help="Trigger the home function.",
    )
    com_ex_group.add_argument(
        "--com-stop-load",
        action="store_true",
        help="Trigger the stop load function.",
    )
    com_ex_group.add_argument(
        "--com-quit",
        action="store_true",
        help="Trigger the quit function.",
    )
    com_ex_group.add_argument(
        "--com-tab-change",
        action="store",
        help="Change the focus to tab `n'.",
        metavar="n",
        type=int,
    )
    com_ex_group.add_argument(
        "--com-tab-close",
        action="store",
        help="Close the tab on index `n'. "
             "Use -1 to close the focused tab.",
        metavar="n",
        type=int,
    )
    com_ex_group.add_argument(
        "--com-exec",
        action="store_true",
        help="Execute the string that is passed at the position of the "
             "url with the python exec function.",
    )
    com_ex_group.add_argument(
        "--com-ping",
        action="store_true",
        help="Try to connect with the communicator. "
             "The program exits with code 0 if successful.",
    )
except Exception:
    raise

try:
    behavior_group.add_argument(
        "--link-target",
        action="store",
        choices=("showcase", "browser"),
        help="By default, hyperlinks are rejected. Use this to define whether "
             "the url should be opened in the showcase or the standard browser instead.",
    )
    behavior_group.add_argument(
        "--javascript",
        action="store_true",
        help="Set all available Javascript policies to True "
             "(JavascriptEnabled, JavascriptCanOpenWindows, "
             "JavascriptCanAccessClipboard, JavascriptCanPaste, "
             "AllowWindowActivationFromJavaScript).",
    )
    behavior_group.add_argument(
        "--no-scrollbars",
        action="store_true",
        help="Do not generate a scrollbar for scrollable html containers "
             "(ShowScrollBars policy).",
    )
    behavior_group.add_argument(
        "--scroll-animator",
        action="store_true",
        help="Activate a smooth scroll animation "
             "(ScrollAnimatorEnabled).",
    )
    behavior_group.add_argument(
        "--policies-set",
        action="store",
        choices=webpolicies.MAP,
        metavar="<policy>",
        nargs="+",
        help="Enable the named policies "
             "(See `--policies-help' for further information).",
    )
    behavior_group.add_argument(
        "--policies-unset",
        action="store",
        choices=webpolicies.MAP,
        metavar="<policy>",
        nargs="+",
        help="Disable the named policies "
             "(See `--policies-help' for further information).",
    )
    behavior_group.add_argument(
        "--policies-help",
        action="store_true",
        help="Show an overview of the available policies and their default values "
             "and exit.",
    )
except Exception:
    raise

try:
    profile_group.add_argument(
        "-p", "--profile",
        action="store",
        metavar="<profile>",
        help="Searches for an environment variable with pattern `SHOWCASE_<profile>', "
             "a file in the home directory with pattern `.<profile>.showcase' "
             "or `<profile>.showcase' (in this order). At the first hit, the "
             "search is interrupted and the text contained is loaded. "
             "This is overwritten by parameterization that are additionally passed.",
    )
    profile_group.add_argument(
        "-f", "--file",
        action="store",
        metavar="<path>",
        help="Load a defined file for parameterization. "
             "This is overwritten by parameterization that are additionally passed.",
    )
except Exception:
    raise

_args = parser.parse_args()


def _parse_string(string: str):
    parse = ""
    for line in string.splitlines():
        if line.startswith('#'):
            continue
        parse += line + " "
    return parser.parse_args(split(parse))


def _profile():
    env = "SHOWCASE_" + _args.profile
    f1 = Path(f"{Path.home().__str__()}/.{_args.profile}.showcase")
    f2 = Path(f"{Path.home().__str__()}/{_args.profile}.showcase")
    if p := environ.get(env):
        return _parse_string(p)
    elif f1.exists():
        with open(p) as f:
            return _parse_string(f.read())
    elif f2.exists():
        with open(p) as f:
            return _parse_string(f.read())
    else:
        raise RuntimeError(f"""\
Could not find `{_args.profile}' (
    - environ[{env}]
    - {f1}
    - {f2}
)
""")


def _file():
    with open(_args.file) as f:
        return _parse_string(f.read())


if _args.profile:
    __args__ = _profile()
    if _args.file:
        args_d = _file().__dict__
        url = args_d.pop("url")
        if not __args__.url:
            __args__.url = url
        __args__.__dict__.update({k: v for k, v in args_d.items() if v is not Null})
    args_d = _args.__dict__
    url = args_d.pop("url")
    if not __args__.url:
        __args__.url = url
    __args__.__dict__.update({k: v for k, v in args_d.items() if v is not Null})
elif _args.file:
    __args__ = _file()
    args_d = _args.__dict__
    url = args_d.pop("url")
    if not __args__.url:
        __args__.url = url
    __args__.__dict__.update({k: v for k, v in args_d.items() if v is not Null})
else:
    __args__ = _args

print("[PARAMS]")
for k, v in __args__.__dict__.items():
    if v is not Null:
        print(f"  {k}={v}")
print()
