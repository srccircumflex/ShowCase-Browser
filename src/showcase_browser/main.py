try:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent))
except Exception:
    raise

from args import __args__, Null
from showcase import Showcase
from communicate import Client
from __init__ import __version__
import webpolicies
import versions


def run():

    if __args__.version:
        exit(__version__)
    if __args__.versions:
        exit(versions.get_available_msg())
    if __args__.policies_help:
        exit(print(webpolicies.about()))

    if not __args__.skip_upgrades and (v := versions.check_msg()):
        print(v, flush=True)

    if len(__args__.url) == 1:
        url = __args__.url[0]
    else:
        url = __args__.url

    com_address = (__args__.com_host or "127.0.0.3", __args__.com_port or 51_001)

    if __args__.com_exec:
        exit(Client(com_address).com(str(" ").join(__args__.url).encode()))
    elif __args__.com_back:
        exit(Client(com_address).com_back())
    elif __args__.com_forward:
        exit(Client(com_address).com_forward())
    elif __args__.com_reload:
        exit(Client(com_address).com_reload())
    elif __args__.com_home:
        exit(Client(com_address).com_home())
    elif __args__.com_stop_load:
        exit(Client(com_address).com_stop_load())
    elif __args__.com_quit:
        exit(Client(com_address).com_quit())
    elif __args__.com_tab_change is not Null:
        exit(Client(com_address).com_tab_change(__args__.com_tab_change))
    elif __args__.com_tab_close is not Null:
        exit(Client(com_address).com_tab_close(__args__.com_tab_close))
    elif __args__.com_try:
        try:
            exit(Client(com_address).com_load(url, __args__.com_tab_index, __args__.com_tab_append))
        except ConnectionRefusedError:
            pass
    elif __args__.com_ping:
        exit(not Client(com_address).com_ping())

    if __args__.com or __args__.com_try:
        print(f"\n"
              f"[*]  Serving Communicator at {com_address[0]}:{com_address[1]}\n")
    else:
        com_address = None

    showcase = Showcase(
        url or '',
        __args__.wg_url,
        __args__.ks_url,
        __args__.wg_back,
        __args__.ks_back,
        __args__.wg_forward,
        __args__.ks_forward,
        __args__.wg_refresh,
        __args__.ks_refresh,
        __args__.wg_home,
        __args__.ks_home,
        __args__.home_url,
        __args__.wg_stop,
        __args__.ks_stop,
        __args__.wg_tabs,
        __args__.wg_tabs_close,
        __args__.ks_tabs_close,
        __args__.wg_tabs_add,
        __args__.ks_tabs_add,
        __args__.tabs_default_url,
        __args__.tabs_default_label,
        __args__.tabs_dynamic_labels,
        __args__.tabs_keep_last,
        __args__.window_title,
        __args__.window_icon,
        __args__.window_maxsize,
        com_address,
        __args__.link_target,
        __args__.javascript,
        __args__.no_scrollbars,
        __args__.scroll_animator,
        {name: True for name in __args__.policies_set or ()}
        | {name: False for name in __args__.policies_unset or ()}
    )

    showcase.exec()


if __name__ == "__main__":
    run()
