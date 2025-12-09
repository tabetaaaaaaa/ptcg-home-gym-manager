"""進化系統探索のヘルパー関数"""
from typing import Set, List
from .models import PokemonCard


def find_evolution_root(card_name: str) -> str:
    """
    対象カードから evolves_from を再帰的にたどり、
    進化系統の最も根元となる「たねポケモン」の名前を特定する。

    Args:
        card_name: 起点となるカード名

    Returns:
        進化系統の根元のカード名（たねポケモン）
    """
    visited = set()
    current_name = card_name

    while current_name and current_name not in visited:
        visited.add(current_name)

        # ポケモンカテゴリのカードのみを対象とする
        card = PokemonCard.objects.filter(
            name=current_name,
            category__slug='pokemon'
        ).values_list('evolves_from', flat=True).first()

        if card is None:
            # カードが見つからない場合は現在の名前を返す
            break

        evolves_from = card

        if not evolves_from:
            # 進化元がない = たねポケモン
            break

        current_name = evolves_from

    return current_name


def collect_evolution_line(root_name: str) -> Set[str]:
    """
    根元のカード名から出発して、関連するすべてのカード名を再帰的に収集する。
    進化先が複数ある場合（例: イーブイ）も網羅的に探索する。

    Args:
        root_name: 進化系統の根元となるカード名

    Returns:
        進化系統に含まれるすべてのカード名のセット
    """
    all_cards = set()
    to_process = [root_name]

    while to_process:
        current_name = to_process.pop()

        if current_name in all_cards:
            # 既に処理済み（循環参照対策）
            continue

        all_cards.add(current_name)

        # このカードから進化するカードをすべて取得
        evolved_cards = PokemonCard.objects.filter(
            evolves_from=current_name,
            category__slug='pokemon'
        ).values_list('name', flat=True)

        for evolved_name in evolved_cards:
            if evolved_name not in all_cards:
                to_process.append(evolved_name)

    return all_cards
