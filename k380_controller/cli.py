"""K380 keyboard command-line interface."""

from __future__ import annotations

import argparse
import sys
import traceback

from k380_controller.core import (
    K380Device,
    K380Mode,
    DeviceNotFoundError,
    DeviceConnectionError,
    DeviceCommunicationError
)


def parse_args() -> argparse.Namespace:
    """Command line arguments parser."""
    parser = argparse.ArgumentParser(
        prog="k380-ctl",
        description="K380 Fn Lock Controller — toggles Fn Lock mode on the Logitech K380 keyboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --detect     # Detect K380 keyboard
  %(prog)s --fn-keys    # Fn Lock On (Pressing F1-F12 triggers F-keys without pressing the Fn key by default)
  %(prog)s --media-keys # Fn Lock Off (Pressing F1-F12 triggers the alternate (media) functions without pressing the Fn key by default)
        """,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-d", "--detect",
        action="store_true",
        help="detect K380 keyboard",
    )
    group.add_argument(
        "-f", "--fn-keys",
        action="store_true",
        help="Fn Lock On (F-keys by default)",
    )
    group.add_argument(
        "-m", "--media-keys",
        action="store_true",
        help="Fn Lock Off (Media-keys by default)",
    )

    return parser.parse_args()


def main() -> int:
    """CLI entry point."""
    args = parse_args()
    set_mode = False if args.detect else True
    mode = K380Mode.K380_MODE_FN_KEYS if args.fn_keys else K380Mode.K380_MODE_MEDIA_KEYS

    try:
        with K380Device() as k380:
            print("K380 device found:")
            k380.print_info()

            if set_mode:
                k380.set_mode(mode)
                
                if mode == K380Mode.K380_MODE_FN_KEYS:
                    print("Set function keys as default (Fn Lock On)")
                else:
                    print("Set media keys as default (Fn Lock Off)")
            
            print("Done!")

    except DeviceNotFoundError:
        print("Error: K380 device not found!", file=sys.stderr)
        return 1

    except (DeviceConnectionError, DeviceCommunicationError) as err:
        traceback.print_exc(file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
