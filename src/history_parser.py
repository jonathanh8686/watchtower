from typing import Generator
from actions import Call, Check, Collected, Fold, PostBig, PostSmall, Raise
from structs import Card, CardSuit, Player, Ply, PokerEvent
import re
from dateutil import parser as date_parser


class Parser:
    @staticmethod
    def __parse_to_pokerevent(event: str) -> PokerEvent:
        event_desc = event.split(",")
        return PokerEvent(
            ",".join(event_desc[:-2]),
            date_parser.parse(event_desc[-2]),
            int(event_desc[-1].strip()),
        )

    @staticmethod
    def __build_ply(events: list[PokerEvent]) -> tuple[Ply, list[PokerEvent]]:
        FACE_VALUE: dict[str, int] = {
            "A": 1,
            "K": 13,
            "Q": 12,
            "J": 11
        }
        
        curr_ply = Ply()
        for i, event in enumerate(events):
            if "ending hand" in event.entry:
                return curr_ply, events[i + 1 :]

            if "posts a small blind" in event.entry:
                pi_match = re.search(
                    r'""([^"]+) @ ([^"]+)"" posts a small blind of ([+-]?(?:[0-9]*[.])?[0-9]+)',
                    event.entry,
                )
                if pi_match is None:
                    raise ValueError(
                        f"Could not find username/id in event: {event.entry}"
                    )
                username, uid, amount = pi_match.groups()
                amount = float(amount)
                assert isinstance(amount, float)

                player = Player(username, uid)
                curr_ply.add_action(player, PostSmall(player=player, amount=amount))

            if "posts a big blind" in event.entry:
                pi_match = re.search(
                    r'""([^"]+) @ ([^"]+)"" posts a big blind of ([+-]?(?:[0-9]*[.])?[0-9]+)',
                    event.entry,
                )
                if pi_match is None:
                    raise ValueError(
                        f"Could not find username/id in event: {event.entry}"
                    )
                username, uid, amount = pi_match.groups()
                amount = float(amount)
                assert isinstance(amount, float)

                player = Player(username, uid)
                curr_ply.add_action(player, PostBig(player=player, amount=amount))

            if "folds" in event.entry:
                pi_match = re.search(r'""([^"]+) @ ([^"]+)"" folds', event.entry)
                if pi_match is None:
                    raise ValueError(
                        f"Could not find username/id in event: {event.entry}"
                    )
                username, uid = pi_match.groups()

                player = Player(username, uid)
                curr_ply.add_action(player, Fold(player=player))

            if "check" in event.entry:
                pi_match = re.search(r'""([^"]+) @ ([^"]+)"" checks', event.entry)
                if pi_match is None:
                    raise ValueError(
                        f"Could not find username/id in event: {event.entry}"
                    )
                username, uid = pi_match.groups()

                player = Player(username, uid)
                curr_ply.add_action(player, Check(player=player))

            if "calls" in event.entry:
                pi_match = re.search(
                    r'""([^"]+) @ ([^"]+)"" calls ([+-]?[[0-9]*[.]]?[0-9]+)',
                    event.entry,
                )
                if pi_match is None:
                    raise ValueError(
                        f"Could not find username/id in event: {event.entry}"
                    )
                username, uid, amount = pi_match.groups()
                amount = float(amount)
                assert isinstance(amount, float)

                player = Player(username, uid)
                curr_ply.add_action(player, Call(player=player, amount=amount))

            if "raises" in event.entry or "bets" in event.entry:
                pi_match = re.search(
                    r'""([^"]+) @ ([^"]+)"" (?:bets|raises to) (\d+[\.\d+]?)',
                    event.entry,
                )

                if pi_match is None:
                    raise ValueError(
                        f"Could not find username/id in event: {event.entry}"
                    )
                username, uid, amount = pi_match.groups()
                amount = float(amount)
                assert isinstance(amount, float)

                player = Player(username, uid)
                curr_ply.add_action(
                    player,
                    Raise(player=player, amount=amount, all_in="all in" in event.entry),
                )

            if "Flop: " in event.entry:
                river_match = re.compile(r'\[([2-9]|10|[JQKA])([♠♥♦♣])\]')
                if river_match is None:
                    raise ValueError(f"Flop could not match cards: {event.entry}")
                cards = []
                for card_match in river_match.finditer(event.entry):
                    rank, suit_char = card_match.groups()
                    if rank not in FACE_VALUE:
                        rank = int(rank)
                    else:
                        rank = FACE_VALUE[rank]
                    assert isinstance(rank, int)

                    suit = CardSuit(suit_char)
                    cards.append(Card(rank, suit))
                curr_ply.process_flop(cards)

            if "Turn: " in event.entry:
                river_match = re.compile(r'\[([2-9]|10|[JQKA])([♠♥♦♣])\]')
                if river_match is None:
                    raise ValueError(f"Turn did not match cards: {event.entry}")
                cards = []
                for card_match in river_match.finditer(event.entry):
                    rank, suit_char = card_match.groups()
                    if rank not in FACE_VALUE:
                        rank = int(rank)
                    else:
                        rank = FACE_VALUE[rank]

                    assert isinstance(rank, int)

                    suit = CardSuit(suit_char)
                    cards.append(Card(rank, suit))
                
                assert len(cards) == 1
                curr_ply.process_turn(cards[0])

            if "River: " in event.entry:
                river_match = re.compile(r'\[([2-9]|10|[JQKA])([♠♥♦♣])\]')
                if river_match is None:
                    raise ValueError(f"River could not match cards: {event.entry}")
                cards = []
                for card_match in river_match.finditer(event.entry):
                    rank, suit_char = card_match.groups()
                    if rank not in FACE_VALUE:
                        rank = int(rank)
                    else:
                        rank = FACE_VALUE[rank]

                    assert isinstance(rank, int)

                    suit = CardSuit(suit_char)
                    cards.append(Card(rank, suit))
                assert len(cards) == 1
                curr_ply.process_river(cards[0])

            if "collected" in event.entry:
                pi_match = re.search(
                    r'""([^"]+) @ ([^"]+)"" posts a big blind of ([+-]?(?:[0-9]*[.])?[0-9]+)',
                    event.entry,
                )
                if pi_match is None:
                    raise ValueError(
                        f"Could not find username/id in event: {event.entry}"
                    )
                username, uid, amount = pi_match.groups()
                amount = float(amount)
                assert isinstance(amount, float)

                player = Player(username, uid)
                curr_ply.add_action(player, Collected(player, amount=amount))

        return curr_ply, []  # last hand may not reach "ending" message

    @staticmethod
    def parse_file(file_path: str) -> list[Ply]:
        raw_data: list[str] | None = None
        with open(file_path, "r") as f:
            raw_data = f.readlines()

        if raw_data is None:
            raise ValueError(f"No data found in {file_path}")
        raw_data = raw_data[1:]  # drop the header

        events = list(map(Parser.__parse_to_pokerevent, raw_data))
        events.sort(key=lambda e: e.order)  # sort by the order field

        parsed_ply = []
        while len(events) != 0:
            ply, events = Parser.__build_ply(events)
            parsed_ply.append(ply)
        return parsed_ply
