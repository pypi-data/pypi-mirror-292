import argparse

def helloworld():
    print("Hello world!")

def main():
    parser = argparse.ArgumentParser(description="openteleop CLI")
    subparsers = parser.add_subparsers(dest='command')

    subparsers.add_parser('helloworld')

    args = parser.parse_args()

    if args.command == 'helloworld':
        helloworld()

if __name__ == "__main__":
    main()
