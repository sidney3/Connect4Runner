import argparse
import sys
import src.engine_runner as engine_runner

def main(args):
    pass

def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("executable",
            nargs="+",
            help="""\
            Executable to run. 
            Can be more than one string. 
            E.x. python3 my_connect4_engine.py")
            """)

    return parser.parse_args()
if __name__ == "__main__":
    main(parse_args())

