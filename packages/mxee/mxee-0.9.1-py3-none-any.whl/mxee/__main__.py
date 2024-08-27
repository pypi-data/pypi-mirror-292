import argparse
import sys
import mxee

parser = argparse.ArgumentParser(prog="mxee", description="mxee", epilog="Making things easier.")
parser.add_argument("--bookmarks", action="store_true", help="test")
parser.add_argument("--test", action="store_true", help="test")


args = parser.parse_args()


if args.bookmarks:
    print("Die Tagersschau https://www.google.com")
    sys.exit(0)


if args.test:
    print(mxee.config("main.user"))
    sys.exit(0)
