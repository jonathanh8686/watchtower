from functools import reduce
import json
import os
from structs import Card, CardSuit, Player


class HandParser:
    @staticmethod
    def parse_folder(folder_path: str) -> list[dict[Player, tuple[Card, Card]]]:
        file_names = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f))
        ]

        individual_dicts = [HandParser.parse_file(fn) for fn in file_names]
        res: list[dict[Player, tuple[Card, Card]]] = []
        for hand_num in range(len(individual_dicts[0])):
            best_knowledge: dict[Player, tuple[Card, Card]] = {}
            for indiv_num in range(len(individual_dicts)):
                best_knowledge.update(individual_dicts[indiv_num][hand_num])
            res.append(best_knowledge)
        return res
            
    @staticmethod
    def parse_file(file_path: str) -> list[dict[Player, tuple[Card, Card]]]:
        with open(file_path, "r") as f:
            raw_data = f.read()
        hand_data = json.loads(raw_data)["hands"]
    
        def parse_hand(raw_hand: list[str]) -> tuple[Card, Card]:
            SUITS = {
                "s": CardSuit.SPADES,
                "h": CardSuit.HEARTS,
                "d": CardSuit.DIAMONDS,
                "c": CardSuit.CLUBS
            }
            FACE_VALUE: dict[str, int] = {"A": 1, "K": 13, "Q": 12, "J": 11, "T": 10}

            # lol
            c1_rank = -1
            if raw_hand[0][0] in FACE_VALUE:
                c1_rank = FACE_VALUE[raw_hand[0][0]]
            else:
                c1_rank = int(raw_hand[0][0])
            c1_suit = SUITS[raw_hand[0][1]]

            c2_rank = -1
            if raw_hand[1][0] in FACE_VALUE:
                c2_rank = FACE_VALUE[raw_hand[1][0]]
            else:
                c2_rank = int(raw_hand[1][0])
            c2_suit = SUITS[raw_hand[1][1]]

            return (Card(c1_rank, c1_suit), Card(c2_rank, c2_suit))

        rtn = []
        for hand in hand_data:
            player_data = hand["players"]
            current_data = {}
            for player in player_data:
                p = Player(username=player["name"], uid=player["id"])
                if "hand" in player:
                    current_data[p] = parse_hand(player["hand"])
            rtn.append(current_data)
        return rtn