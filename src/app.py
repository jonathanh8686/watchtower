from history_parser import Parser
import argparse

arg_parser = argparse.ArgumentParser("PokerNow history parser")
arg_parser.add_argument(
    "--file_path",
    "-f",
    help="A path to a .csv file given by PokerNow to parse",
    type=str,
)

args = arg_parser.parse_args()

print(Parser().parse_file(args.file_path))
