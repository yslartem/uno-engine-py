from __future__ import annotations

import random
from typing import List, Optional

from ..engine.card import Card, CardColor
from ..player.player import Player, PlayerAction


class DemonHomeBot(Player):

    def __init__(self, name: str, player_id: int):
        super().__init__(name, player_id)
        self._top_card: Optional[Card] = None
        self._current_color: Optional[CardColor] = None

    def update_game_state(
            self,
            playable_cards: List[Card],
            top_card: Card,
            current_color: CardColor
    ) -> None:
        self._top_card = top_card
        self._current_color = current_color

    def choose_action(self) -> PlayerAction:
        valid_cards = [
            card for card in self.hand
            if card.can_play_on(self._top_card, self._current_color)
        ]

        if not valid_cards:
            return PlayerAction(draw_card=True)

        hand_size = len(self.hand)

        color_counts = {
            CardColor.RED: 0,
            CardColor.BLUE: 0,
            CardColor.GREEN: 0,
            CardColor.YELLOW: 0,
        }

        for card in self.hand:
            if card.color in color_counts:
                color_counts[card.color] += 1

        dominant_color = max(color_counts.items(), key=lambda x: x[1])[0]

        selection = None

        # Разная стратегия в зависимости от размера руки
        if hand_size > 4:
            # Когда много карт, играем по классической тактике
            for card in valid_cards:
                if hasattr(card.label, 'DRAW_TWO') and card.label.DRAW_TWO:
                    selection = card
                    break

            if selection is None:
                for card in valid_cards:
                    if hasattr(card.label, 'SKIP') and card.label.SKIP:
                        selection = card
                        break

            if selection is None:
                for card in valid_cards:
                    if hasattr(card.label, 'REVERSE') and card.label.REVERSE:
                        selection = card
                        break

            if selection is None:
                num_cards = [card for card in valid_cards if
                             hasattr(card.label, 'value') and 0 <= card.label.value <= 9]
                if num_cards:
                    same_color_cards = [card for card in num_cards if card.color == dominant_color]
                    if same_color_cards:
                        selection = max(same_color_cards, key=lambda c: c.label.value)

            if selection is None:
                for card in valid_cards:
                    if hasattr(card.label, 'WILD_DRAW_FOUR') and card.label.WILD_DRAW_FOUR:
                        selection = card
                        break

            if selection is None:
                for card in valid_cards:
                    if hasattr(card.label, 'WILD') and card.label.WILD:
                        selection = card
                        break
        else:
            # Когда карт мало, стараемся закончить игру
            for card in valid_cards:
                if hasattr(card.label, 'WILD_DRAW_FOUR') and card.label.WILD_DRAW_FOUR:
                    selection = card
                    break

            if selection is None:
                for card in valid_cards:
                    if hasattr(card.label, 'WILD') and card.label.WILD:
                        selection = card
                        break

            if selection is None:
                for card in valid_cards:
                    if hasattr(card.label, 'DRAW_TWO') and card.label.DRAW_TWO:
                        selection = card
                        break

            if selection is None:
                for card in valid_cards:
                    if hasattr(card.label, 'SKIP') and card.label.SKIP:
                        selection = card
                        break

            if selection is None:
                for card in valid_cards:
                    if hasattr(card.label, 'REVERSE') and card.label.REVERSE:
                        selection = card
                        break

            if selection is None:
                num_cards = [card for card in valid_cards if
                             hasattr(card.label, 'value') and 0 <= card.label.value <= 9]
                if num_cards:
                    # При малом количестве карт играем самую маленькую числовую
                    selection = min(num_cards, key=lambda c: c.label.value)

        if selection is None and valid_cards:
            selection = valid_cards[0]

        return PlayerAction(selection, draw_card=False)

    def choose_color(self, wild_card: Card) -> CardColor:
        color_counts = {
            CardColor.RED: 0,
            CardColor.BLUE: 0,
            CardColor.GREEN: 0,
            CardColor.YELLOW: 0,
        }

        for card in self.hand:
            if not hasattr(card.label, 'WILD') and not hasattr(card.label, 'WILD_DRAW_FOUR'):
                if card.color in color_counts:
                    color_counts[card.color] += 1

        max_color = max(color_counts.items(), key=lambda x: x[1])[0]

        if sum(color_counts.values()) == 0:
            return CardColor.RED

        return max_color

    def decide_say_uno(self) -> bool:
        return len(self.hand) == 1

    def should_play_drawn_card(self, drawn_card: Card) -> bool:
        return drawn_card.can_play_on(self._top_card, self._current_color)