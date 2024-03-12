import re

from dateutil import parser as date_parser

from actions import Call, Check, Collected, Fold, PostBig, PostSmall, Raise
from structs import Card, CardSuit, Player, Ply, PokerEvent


class HistoryParser:
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
        FACE_VALUE: dict[str, int] = {"A": 1, "K": 13, "Q": 12, "J": 11}

        curr_ply = Ply()
        for i, event in enumerate(events):
            if "ending hand" in event.entry:
                return curr_ply, events[i + 1 :]
            
            if "starting hand" in event.entry:
                id_match = re.findall(r'\(id: ([a-z\d]+)\)', event.entry)
                if(id_match is None):
                    raise ValueError(f"Could not find id in: {event.entry}")

                dealer: Player | None = None
                if "dead button" not in event.entry:
                    dealer_matches = re.search(r'dealer: ""([^"]+) @ ([^"]+)""', event.entry)
                    if dealer_matches is None:
                        raise ValueError(f"Could not find dealer: {event.entry}")
                    username, uid = dealer_matches.groups()
                    dealer = Player(username, uid)
               
                curr_ply.process_start(id_match[0], dealer)

            if "Player stacks" in event.entry:
                pattern = r'""([^"]+) @ ([^"]+)"" \((\d+.\d+)\)'
                matches = re.findall(pattern, event.entry)
                stacks = {
                    Player(match[0], match[1]): float(match[2]) for match in matches
                }
                curr_ply.process_stacks(stacks)

                if(curr_ply.dealer is not None):
                    player_matches = [(match[0], match[1]) for match in matches]
                    dealer_index = player_matches.index((curr_ply.dealer.username, curr_ply.dealer.uid))
                    positions: dict[Player, int] = {}
                    for i, (p_name, p_uid, _) in enumerate(matches):
                        p = Player(p_name, p_uid)
                        positions[p] = ((i - dealer_index) + len(matches)) % len(matches)
                    curr_ply.set_positions(positions)

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

                players = list(curr_ply.stacks.keys())
                sb_index = players.index(player)
                dealer_index = ((sb_index - 1) + len(players)) % len(players)
                positions = {}
                for i, (p_name, p_uid, _) in enumerate(matches):
                    p = Player(p_name, p_uid)
                    positions[p] = ((i - dealer_index) + len(matches)) % len(matches)
                curr_ply.set_positions(positions)

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
                    r'""([^"]+) @ ([^"]+)"" calls ([+-]?(?:[0-9]*[.])?[0-9]+)',
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
                river_match = re.compile(r"\[([2-9]|10|[JQKA])([♠♥♦♣])\]")
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
                river_match = re.compile(r"\[([2-9]|10|[JQKA])([♠♥♦♣])\]")
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
                river_match = re.compile(r"\[([2-9]|10|[JQKA])([♠♥♦♣])\]")
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
                    r'""([^"]+) @ ([^"]+)"" collected ([+-]?(?:[0-9]*[.])?[0-9]+)',
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

            if "shows" in event.entry:
                pi_match = re.search(
                    r'""([^"]+) @ ([^"]+)"" shows a ([2-9]|10|[JQKA])([♠♥♦♣]), ([2-9]|10|[JQKA])([♠♥♦♣]).',
                    event.entry,
                )
                if pi_match is None:
                    raise ValueError(
                        f"Could not find username/id in event: {event.entry}"
                    )
                (
                    username,
                    uid,
                    card1_rank,
                    card1_suit,
                    card2_rank,
                    card2_suit,
                ) = pi_match.groups()
                parse_card_rank = (
                    lambda rank: int(rank)
                    if rank not in FACE_VALUE
                    else FACE_VALUE[rank]
                )

                player = Player(username, uid)
                curr_ply.add_card_data(
                    player,
                    (
                        Card(parse_card_rank(card1_rank), CardSuit(card1_suit)),
                        Card(parse_card_rank(card2_rank), CardSuit(card2_suit)),
                    ),
                )

        return curr_ply, []  # last hand may not reach "ending" message

    @staticmethod
    def parse_file(file_path: str) -> list[Ply]:
        raw_data: list[str] | None = None
        with open(file_path, "r") as f:
            raw_data = f.readlines()

        if raw_data is None:
            raise ValueError(f"No data found in {file_path}")
        raw_data = raw_data[1:]  # drop the header

        events = list(map(HistoryParser.__parse_to_pokerevent, raw_data))
        events.sort(key=lambda e: e.order)  # sort by the order field

        parsed_ply = []
        while len(events) != 0:
            ply, events = HistoryParser.__build_ply(events)
            parsed_ply.append(ply)
        return parsed_ply
