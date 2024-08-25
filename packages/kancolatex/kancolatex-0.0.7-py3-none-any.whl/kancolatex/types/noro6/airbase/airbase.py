from __future__ import annotations

import math
from dataclasses import InitVar
from dataclasses import dataclass
from dataclasses import field

from typing_extensions import Optional
from typing_extensions import Sequence
from typing_extensions import TypedDict

from .... import utils
from ....logger import LOGGER
from ...const import AirBaseActionKind
from ..air_calc_result import AirCalcResult
from ..item import Item
from ..item import ItemBuilder


@dataclass(slots=True)
class AirbaseBuilder:
    airbase: Optional[Airbase] = None
    items: Optional[list[Item]] = None
    """装備 未指定ならshipの装備で作成"""
    mode: Optional[AirBaseActionKind] = None
    """基地お札"""
    battleTarget: Optional[tuple[int, int]] = None
    """基地出撃戦闘番号"""


@dataclass(slots=True)
class Airbase:
    builder: InitVar[AirbaseBuilder]

    items: list[Item] = field(default_factory=list)
    mode: AirBaseActionKind = AirBaseActionKind.STANDBY
    battleTarget: tuple[int, int] = field(default_factory=lambda: (0, 0))
    isSeparate: bool = False
    radius: int = 0
    fullAirPower: int = 0
    reconCorr: float = 0
    defenseAirPower: int = 0
    reconCorrDefense: float = 0
    rocketCount: int = 0
    hasJet: bool = False
    fuel: int = 0
    ammo: int = 0
    steel: int = 0
    bauxite: int = 0
    superHighAirRaidTypeAItemCount: int = 0
    superHighAirRaidTypeBItemCount: int = 0
    superHighAirRaidTypeCItemCount: int = 0
    resultWave1: AirCalcResult = field(default_factory=lambda: AirCalcResult())
    resultWave2: AirCalcResult = field(default_factory=lambda: AirCalcResult())
    airPower: int = 0
    needShootDown: bool = False
    totalSupplyFuel: int = 0
    totalSupplyBauxite: int = 0
    totalUsedSteel: int = 0

    def __post_init__(self, builder: AirbaseBuilder = AirbaseBuilder()):
        if builder.airbase:
            self.items = (
                builder.items if builder.items is not None else [*builder.airbase.items]
            )
            self.mode = (
                builder.mode if builder.mode is not None else builder.airbase.mode
            )
            self.battleTarget = (
                builder.battleTarget
                if builder.battleTarget is not None
                else builder.airbase.battleTarget
            )
        else:
            self.items = builder.items if builder.items is not None else list()
            self.mode = (
                builder.mode if builder.mode is not None else AirBaseActionKind.STANDBY
            )
            self.battleTarget = (
                builder.battleTarget if builder.battleTarget is not None else (0, 0)
            )

        itemCount = len(self.items)
        if itemCount < 4:
            for _ in range(4 - itemCount):
                self.items.append(Item(ItemBuilder()))

        # 半径取得
        self.radius = self._getRadius()

        # 制空値とか
        self.fullAirPower = 0
        self.defenseAirPower = 0
        self.rocketCount = 0
        self.hasJet = False
        self.reconCorr = 1
        self.reconCorrDefense = 1
        self.superHighAirRaidTypeAItemCount = 0
        self.superHighAirRaidTypeBItemCount = 0
        self.superHighAirRaidTypeCItemCount = 0
        self.fuel = 0
        self.ammo = 0
        self.steel = 0
        self.bauxite = 0
        self.isSeparate = self.battleTarget[0] != self.battleTarget[1]

        for item in self.items:
            if item.fullSlot > 0:
                LOGGER.debug(f"{item.fullAirPower = }, {item.defenseAirPower = }")
                LOGGER.debug(f"{item.slot = }")

                self.fullAirPower += item.fullAirPower
                self.defenseAirPower += item.defenseAirPower
            if item.data.isRocket:
                self.rocketCount += 1
            if not self.hasJet and item.data.isJet:
                self.hasJet = True

            # この航空隊の偵察機補正を取得
            if self.reconCorr < item.reconCorr:
                # 最大の補正値にする
                self.reconCorr = item.reconCorr
            if self.reconCorrDefense < item.reconCorrDefense:
                # 最大の補正値にする
                self.reconCorrDefense = item.reconCorrDefense

            # 超重爆A補正 => 屠龍(445) / 雷電(175) / 烈風改(333) / 飛燕244(177)
            if item.data.id in {445, 175, 333, 177}:
                self.superHighAirRaidTypeAItemCount += 1
            # 超重爆補正B該当機の数加算 => 紫電343(263) / Fw190(354)
            if item.data.id in {263, 354}:
                self.superHighAirRaidTypeBItemCount += 1
            # 超重爆補正C該当機の数加算 => 烈風改(三五二/熟練)(334) / キ96(452) / 屠龍丙(446)
            if item.data.id in {334, 452, 446}:
                self.superHighAirRaidTypeCItemCount += 1

            self.fuel += item.fuel
            self.ammo += item.ammo
            self.steel += item.steel
            self.bauxite += item.bauxite

        # 補正値で更新
        self.fullAirPower = math.floor(self.fullAirPower * self.reconCorr)
        self.defenseAirPower = math.floor(self.defenseAirPower * self.reconCorrDefense)
        self.airPower = self.fullAirPower

        # 装備なんもないとか、なんか変な札になってたらなら自動で待機にする
        if not any(v.data.id > 0 for v in self.items) or not self.mode in {
            AirBaseActionKind.STANDBY,
            AirBaseActionKind.MISSION,
            AirBaseActionKind.AIR_DEFENSE,
        }:
            self.mode = AirBaseActionKind.STANDBY

    def _getRadius(self) -> int:
        """航空隊の半径を返却"""

        minRadius: int = 999
        maxReconRadius: int = 1
        for item in self.items:
            if item.data.id and item.fullSlot:
                # 最も短い半径を更新
                minRadius = (
                    item.data.radius if item.data.radius < minRadius else minRadius
                )

                # 偵察機の中で最も長い半径を取得
                if item.data.isRecon and maxReconRadius < item.data.radius:
                    maxReconRadius = item.data.radius

        # 対潜哨戒機が存在したら半径延長無効
        containAswPlane = any(
            v.data.isAswPlane and not v.data.isAttacker for v in self.items
        )
        if not containAswPlane and maxReconRadius > minRadius:
            # 偵察機による半径拡張
            return round(minRadius + min(math.sqrt(maxReconRadius - minRadius), 3))

        return 0 if minRadius == 999 else minRadius

    @staticmethod
    def supply(airbase: Airbase):
        """計算で減衰した各種値を戻す 計算用"""

        airbase.airPower = airbase.fullAirPower
        for i, item in enumerate(airbase.items):
            item.deathRate += 1 if item.slot == 0 else 0

            lossSlot = item.fullSlot - item.slot
            airbase.totalSupplyFuel += 3 * lossSlot
            airbase.totalSupplyBauxite += 5 * lossSlot
            Item.supply(airbase.items[i])

    def getContactRates(self):
        """この艦隊の触接情報テーブルを取得"""
        return Item.getContactRates(self.items)

    def putItem(
        self,
        item: Item,
        slot: int,
        initialLevels: Sequence[_InitialLevels],
        isDefense: bool = False,
        lastBattle: int = 0,
    ) -> Airbase:
        """装備をセット"""
        if slot < len(self.items):
            level: int = 0
            if initialLevels:
                initData = utils.find(
                    initialLevels, lambda v, _: v.get("id", 0) == item.data.apiTypeId
                )
                if initData:
                    level = initData.get("level", 0)

            itemBuilder: ItemBuilder = ItemBuilder(
                master=item.data,
                slot=item.data.airbaseMaxSlot,
                level=level,
                remodel=item.remodel,
            )
            self.items[slot] = Item(itemBuilder)

        airbaseBuilder: AirbaseBuilder = AirbaseBuilder(airbase=self)
        if self.mode is AirBaseActionKind.STANDBY and any(
            v.data.id > 0 and v.fullSlot > 0 for v in self.items
        ):
            # 待機札だった場合
            # 出撃か防空札に変更
            airbaseBuilder.mode = (
                AirBaseActionKind.AIR_DEFENSE
                if isDefense
                else AirBaseActionKind.MISSION
            )
            # 派遣先を最終戦闘にオート設定
            airbaseBuilder.battleTarget = (lastBattle, lastBattle)

        return Airbase(airbaseBuilder)

    def expandPreset(
        self,
        items: Sequence[Item],
        initialLevels: Sequence[_InitialLevels],
        isDefense: bool = False,
        lastBattle: int = 0,
    ) -> Airbase:
        # もともとここに配備されていた装備情報を抜き取る
        newItems = [*items]
        # 装備搭載可否情報マスタ
        for slotIndex, _ in enumerate(self.items):
            if slotIndex < len(items):
                newItem = items[slotIndex]
                if newItem and newItem.data.isPlane:
                    # 初期熟練度設定
                    level: int = 0
                    # 設定情報より初期熟練度を解決
                    initData = utils.find(
                        initialLevels,
                        lambda v, _: v.get("id", 0) == newItem.data.apiTypeId,
                    )
                    if initData:
                        level = initData.get("level", 0)

                    newItems[slotIndex] = Item(
                        ItemBuilder(
                            master=newItem.data,
                            item=newItems[slotIndex],
                            slot=newItem.data.airbaseMaxSlot,
                            level=level,
                            remodel=newItem.remodel,
                        )
                    )
                else:
                    newItems[slotIndex] = Item(ItemBuilder())

        builder: AirbaseBuilder = AirbaseBuilder(airbase=self, items=newItems)
        if self.mode is AirBaseActionKind.STANDBY and any(
            v.data.id > 0 and v.fullSlot > 0 for v in self.items
        ):
            # 待機札だった場合
            # 出撃か防空札に変更
            builder.mode = (
                AirBaseActionKind.AIR_DEFENSE
                if isDefense
                else AirBaseActionKind.MISSION
            )
            # 派遣先を最終戦闘にオート設定
            builder.battleTarget = (lastBattle, lastBattle)

        # 再インスタンス化し更新
        return Airbase(builder)

    def bulkUpdateAllItem(
        self, builder: ItemBuilder, onlyFighter: bool = False
    ) -> Airbase:
        """全装備を一括更新した新しいAirbaseインスタンスを返却"""
        items = self.items
        for j, item in enumerate(items):
            if not onlyFighter or (onlyFighter and item.data.isFighter):
                slot = item.slot
                level = builder.level
                if item.data.isPlane and builder.slot is not None:
                    slot = min(item.data.airbaseMaxSlot, builder.slot)
                items[j] = Item(
                    ItemBuilder(
                        item=item,
                        slot=slot,
                        remodel=builder.remodel if item.data.canRemodel else None,
                        level=level,
                    )
                )

        return Airbase(AirbaseBuilder(airbase=self))


class _InitialLevels(TypedDict):
    id: int
    level: int
