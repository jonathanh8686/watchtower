import argparse

from hand_parser import HandParser
from history_parser import HistoryParser

arg_parser = argparse.ArgumentParser("PokerNow history parser")
arg_parser.add_argument(
    "--file_path",
    "-f",
    help="A path to a .csv file given by PokerNow to parse",
    type=str,
)

args = arg_parser.parse_args()
# print(HandParser().parse_folder(args.file_path))
print(HistoryParser.parse_file(args.file_path))
