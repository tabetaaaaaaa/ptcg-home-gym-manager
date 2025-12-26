"""
マスタデータ初期投入用カスタム管理コマンド

このコマンドはコンテナ起動時に自動実行され、
マスタデータが存在しない場合のみfixturesからデータを投入します。

Usage:
    python manage.py seed_master_data
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from cards.models import (
    CardCategory,
    Type,
    EvolutionStage,
    SpecialFeature,
    MoveType,
    TrainerType,
    SpecialTrainer,
)


class Command(BaseCommand):
    help = 'マスタデータを初期投入します（既存データがある場合はスキップ）'

    def handle(self, *args, **options):
        # 各マスタテーブルの存在チェック
        master_models = [
            ('CardCategory', CardCategory),
            ('Type', Type),
            ('EvolutionStage', EvolutionStage),
            ('SpecialFeature', SpecialFeature),
            ('MoveType', MoveType),
            ('TrainerType', TrainerType),
            ('SpecialTrainer', SpecialTrainer),
        ]

        # いずれかのマスタテーブルにデータがあればスキップ
        # （通常、マスタデータは一括で投入されるため）
        for name, model in master_models:
            if model.objects.exists():
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ マスタデータは既に存在します（{name}にデータあり）。スキップします。'
                    )
                )
                return

        # すべてのマスタテーブルが空の場合、fixturesからデータを投入
        self.stdout.write('マスタデータを投入中...')
        try:
            call_command('loaddata', 'master_data.json', verbosity=1)
            self.stdout.write(
                self.style.SUCCESS('✓ マスタデータの投入が完了しました。')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ マスタデータの投入に失敗しました: {e}')
            )
            raise
