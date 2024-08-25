import argparse
from .commands import build, venvmanager

def main():
    parser = argparse.ArgumentParser(description="BLKMRLN CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Build command
    build_parser = subparsers.add_parser('build', help='Build the project')
    build_parser.add_argument('-n', '--name', required=True, help='Name of the project')
    build_parser.add_argument('-e', '--env', required=True, help='venvmanager directory path')


    # VenvManager command
    rename_parser = subparsers.add_parser('venvmanager', help='Manage Virtual Environments')
    rename_parser.add_argument('-p', '--project', required=False, help='Name of the project')
    rename_parser.add_argument('-d', '--dep_flag', action='store_true', help='Flag to include dep')

    #Test command
    test_parser = subparsers.add_parser('test', help='Test the project')
    test_parser.add_argument('-n', '--name', required=True, help='Name of the project')

    # Parse arguments
    args = parser.parse_args()

    if args.command == 'build':
        build.execute(args)
    elif args.command == 'venvmanager':
        venvmanager.execute(args)

if __name__ == "__main__":
    main()