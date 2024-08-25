from __future__ import annotations

import math
from dataclasses import InitVar
from dataclasses import dataclass
from dataclasses import field

from typing_extensions import MutableSequence
from typing_extensions import Optional

from ...const import DIFFICULTY_LEVEL
from ...const import AirBaseActionKind
from ..air_calc_result import AirCalcResult
from ..item import Item
from ..item import ItemBuilder
from .airbase import Airbase
from .airbase import AirbaseBuilder


@dataclass(slots=True)
class AirbaseInfoBuilder:
    info: Optional[AirbaseInfo] = None
    airbases: Optional[MutableSequence[Airbase]] = None
    isDefense: Optional[bool] = None
    difficultyLevel: Optional[DIFFICULTY_LEVEL] = None


@dataclass(slots=True)
class AirbaseInfo:
    builder: InitVar[AirbaseInfoBuilder]

    airbases: MutableSequence[Airbase] = field(default_factory=list)
    difficultyLevel: DIFFICULTY_LEVEL = DIFFICULTY_LEVEL.HARD
    defenseAirPower: int = 0
    highDefenseCoefficient: float = 0
    highDefenseAirPower: int = 0
    superHighAirRaidCorrA: float = 0
    superHighAirRaidCorrB: float = 0
    superHighAirRaidCorrC: float = 0
    superHighAirRaidRocketCoefficientA: float = 0
    superHighAirRaidRocketCoefficientB: float = 0
    superHighAirRaidRocketCoefficientC: float = 0
    superHighAirRaidCoefficient: float = 0
    fullSuperHighDefenseAirPower: int = 0
    superHighAirRaidResults: MutableSequence[AirCalcResult] = field(
        default_factory=list
    )
    superHighDefenseAirPower: int = 0
    isDefense: bool = False
    calculated: bool = False
    ignoreHistory: bool = False

    def __post_init__(self, builder: AirbaseInfoBuilder):
        if builder.info:
            self.airbases = (
                builder.airbases
                if builder.airbases is not None
                else [*builder.info.airbases]
            )
            self.isDefense = (
                builder.isDefense
                if builder.isDefense is not None
                else builder.info.isDefense
            )
            self.difficultyLevel = (
                builder.difficultyLevel
                if builder.difficultyLevel is not None
                else builder.info.difficultyLevel
            )
        else:
            self.airbases = builder.airbases if builder.airbases is not None else list()
            self.isDefense = (
                builder.isDefense if builder.isDefense is not None else False
            )
            self.difficultyLevel = (
                builder.difficultyLevel
                if builder.difficultyLevel is not None
                else DIFFICULTY_LEVEL.HARD
            )

        if len(self.airbases) < 3:
            sub = 3 - len(self.airbases)
            for _ in range(sub):
                self.airbases.append(Airbase(AirbaseBuilder()))

        self.defenseAirPower = 0
        self.highDefenseAirPower = 0
        self.superHighDefenseAirPower = 0
        self.superHighAirRaidRocketCoefficientA = 0
        self.superHighAirRaidRocketCoefficientB = 0

        rocketCount: int = 0
        sumSuperHighAirRaidTypeAItemCount: int = 0
        sumSuperHighAirRaidTypeBItemCount: int = 0
        sumSuperHighAirRaidTypeCItemCount: int = 0
        for airbase in self.airbases:
            if airbase.mode == AirBaseActionKind.AIR_DEFENSE:
                self.defenseAirPower += airbase.defenseAirPower
                rocketCount += airbase.rocketCount
                sumSuperHighAirRaidTypeAItemCount += (
                    airbase.superHighAirRaidTypeAItemCount
                )
                sumSuperHighAirRaidTypeBItemCount += (
                    airbase.superHighAirRaidTypeBItemCount
                )
                sumSuperHighAirRaidTypeCItemCount += (
                    airbase.superHighAirRaidTypeCItemCount
                )

        # 重爆補正
        self.highDefenseCoefficient = 1
        isHardOrMedium = (
            self.difficultyLevel is DIFFICULTY_LEVEL.HARD
            or self.difficultyLevel is DIFFICULTY_LEVEL.MEDIUM
        )
        if rocketCount >= 3:
            self.highDefenseCoefficient = 1.2
        elif rocketCount == 2:
            self.highDefenseCoefficient = 1.1
        elif rocketCount == 1 and isHardOrMedium:
            self.highDefenseCoefficient = 0.8
        elif rocketCount == 0 and isHardOrMedium:
            self.highDefenseCoefficient = 0.5
        self.highDefenseAirPower = math.floor(
            self.defenseAirPower * self.highDefenseCoefficient
        )

        # 超重爆補正計算
        # 超重爆補正A
        self.superHighAirRaidCorrA = sumSuperHighAirRaidTypeAItemCount * 0.07

        # 超重爆補正B
        self.superHighAirRaidCorrB = {
            0: 0,
            1: 0.11,
            2: 0.14,
            # 3以上、不明
        }.get(sumSuperHighAirRaidTypeBItemCount, 0.14)

        # 超重爆補正C
        self.superHighAirRaidCorrC = {
            0: 0,
            1: 0.177,
            2: 0.287,
            # 3以上、不明
        }.get(sumSuperHighAirRaidTypeCItemCount, 0.397)
        (
            self.superHighAirRaidRocketCoefficientA,
            self.superHighAirRaidRocketCoefficientB,
        ) = {
            0: (
                0.5,
                0.3,
            ),
            1: (
                0.95,
                0.55,
            ),
            2: (
                1,  # 不明
                0.85,
            ),
            3: (
                1,
                1,
            ),
            4: (
                1,
                1.11,
            ),
        }.get(
            rocketCount,
            (  # 5以上
                1,  # 不明
                1.11,
            ),
        )

        # 補正合計
        self.superHighAirRaidCoefficient = (
            (
                self.superHighAirRaidCorrA
                + self.superHighAirRaidCorrB
                + self.superHighAirRaidCorrC
            )
            * self.superHighAirRaidRocketCoefficientA
            + self.superHighAirRaidRocketCoefficientB
        )
        # 超重爆最終制空値
        self.superHighDefenseAirPower = math.floor(
            self.defenseAirPower * self.superHighAirRaidCoefficient
        )
        self.fullSuperHighDefenseAirPower = self.superHighDefenseAirPower
        self.superHighAirRaidResults = [
            AirCalcResult(),
            AirCalcResult(),
            AirCalcResult(),
        ]

    def shootDownByAirRaid(self):
        """基地空襲被害を各航空隊に発生させる"""
        for i, airbase in enumerate(self.airbases):
            if airbase.mode is AirBaseActionKind.STANDBY or airbase.mode in {
                AirBaseActionKind.REST,
                AirBaseActionKind.TAKE_COVER,
                AirBaseActionKind.NONE,
            }:
                continue

            count = 4
            items = airbase.items
            for j, item in enumerate(items):
                if not item.data.id:
                    continue

                if count >= item.data.airbaseMaxSlot:
                    # 最大搭載数以上に削られる場合は1機残す
                    items[j] = Item(ItemBuilder(item=item, slot=1))
                    count -= item.data.airbaseMaxSlot - 1
                else:
                    # 受けきれる
                    items[j] = Item(
                        ItemBuilder(item=item, slot=item.data.airbaseMaxSlot - count)
                    )
                    count = 0

            self.airbases[i] = Airbase(AirbaseBuilder(airbase=airbase, items=items))
