from __future__ import annotations

import math
import operator
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from enum import EnumMeta
from enum import IntEnum
from enum import auto

from typing_extensions import Any
from typing_extensions import Callable
from typing_extensions import Iterable
from typing_extensions import Sequence
from typing_extensions import TypeVar

from ... import utils
from ...logger import LOGGER
from ...types.const import EquipmentTypes
from ...types.noro6 import AirbaseInfo
from ...types.noro6 import Fleet
from ...types.noro6 import FleetInfo
from ..translator.translator import Translator


class _ORDER_AIRBASE_TRANSLATE(IntEnum):
    A = 0
    B = 1
    C = 2
    U = 3


class _ORDER_AIRBASE_EQUIPMENT_TRANSLATE(IntEnum):
    A = 0
    B = 1
    C = 2
    D = 3


class _ORDER_EQUIPMENT_TRANSLATE(IntEnum):
    A = 0
    """Equipment 1"""
    B = 1
    """Equipment 2"""
    C = 2
    """Equipment 3"""
    D = 3
    """Equipment 4"""
    E = 4
    """Equipment 5"""
    X = 99
    """Equipment Extra Slots"""


class _ORDER_SHIP_TRANSLATE(IntEnum):
    A = 0
    """Single Fleet / JTF Flag Ship"""
    B = 1
    """Single Fleet / JTF 2nd ship"""
    C = 2
    """Single Fleet / JTF 3rd ship"""
    D = 3
    """Single Fleet / JTF 4th ship"""
    E = 4
    """Single Fleet / JTF 5th ship"""
    F = 5
    """Single Fleet / JTF 6th ship"""
    G = 6
    """Single Fleet Vanguard 7th ship"""
    U = 6
    """JTF Escort Fleet Flag Ship"""
    V = 7
    """JTF Escort Fleet 2nd Ship"""
    W = 8
    """JTF Escort Fleet 3rd Ship"""
    X = 9
    """JTF Escort Fleet 4th Ship"""
    Y = 10
    """JTF Escort Fleet 5th Ship"""
    Z = 11
    """JTF Escort Fleet 6th Ship"""


@dataclass(slots=True)
class OrderTranslate:
    _T = TypeVar("_T")
    _OptionT = TypeVar("_OptionT", tuple[str, ...], set[str])

    @classmethod
    def airbase(cls, _t: type[_OptionT]) -> _OptionT:
        return _t((*cls.airbaseName(_t), *cls.airbaseValue(_t)))

    @classmethod
    def airbaseName(cls, _t: type[_OptionT]) -> _OptionT:
        return _t(cls._extractName(_ORDER_AIRBASE_TRANSLATE))

    @classmethod
    def airbaseValue(cls, _t: type[_OptionT]) -> _OptionT:
        return _t(cls._extractValue(_ORDER_AIRBASE_TRANSLATE))

    @classmethod
    def airbaseEquipment(cls, _t: type[_OptionT]) -> _OptionT:
        return _t((*cls.airbaseName(_t), *cls.airbaseValue(_t)))

    @classmethod
    def airbaseEquipmentName(cls, _t: type[_OptionT]) -> _OptionT:
        return _t(cls._extractName(_ORDER_AIRBASE_EQUIPMENT_TRANSLATE))

    @classmethod
    def airbaseEquipmentValue(cls, _t: type[_OptionT]) -> _OptionT:
        return _t(cls._extractValue(_ORDER_AIRBASE_EQUIPMENT_TRANSLATE))

    @classmethod
    def equipment(cls, _t: type[_OptionT]) -> _OptionT:
        return _t((*cls.equipmentName(_t), *cls.equipmentValue(_t)))

    @staticmethod
    def equipmentName(_t: type[_OptionT]) -> _OptionT:
        return _t(k for k in _ORDER_EQUIPMENT_TRANSLATE.__members__.keys())

    @staticmethod
    def equipmentValue(_t: type[_OptionT]) -> _OptionT:
        return _t(str(k) for k in _ORDER_EQUIPMENT_TRANSLATE.__members__.values())

    @classmethod
    def ship(cls, _t: type[_OptionT]) -> _OptionT:
        return _t((*cls.shipName(_t), *cls.shipValue(_t)))

    @staticmethod
    def shipName(_t: type[_OptionT]) -> _OptionT:
        return _t(k for k in _ORDER_SHIP_TRANSLATE.__members__.keys())

    @staticmethod
    def shipValue(_t: type[_OptionT]) -> _OptionT:
        return _t(str(k) for k in _ORDER_SHIP_TRANSLATE.__members__.values())

    @staticmethod
    def _extract(_i: Iterable[Any], _t: Callable[[Any], _T] = str) -> Iterable[_T]:
        return (_t(v) for v in _i)

    @classmethod
    def _extractName(cls, _e: EnumMeta, _t: Callable[[Any], _T] = str) -> Iterable[_T]:
        return (_t(v) for v in _e.__members__.keys())

    @classmethod
    def _extractValue(cls, _e: EnumMeta, _t: Callable[[Any], _T] = str) -> Iterable[_T]:
        return (_t(v) for v in _e.__members__.values())


class MacroValueType(Enum):
    MNEMONIC = auto()
    ATTRIBUTE_ACCESS = auto()
    UNKNOWN = auto()


@dataclass(slots=True)
class Macro:
    value: str = ""
    type: MacroValueType = MacroValueType.UNKNOWN


def isValidMacro(val: str) -> Macro | None:
    if len(val) < 2:
        return None

    if val[0] != "<" and val[-1] != ">":
        return None

    macroStr = val.removeprefix("<").removesuffix(">")

    if all(v.isupper() or v == "_" for v in macroStr):
        # <MNEMONIC>
        return Macro(
            macroStr,
            (
                MacroValueType.MNEMONIC
                if all(len(v) for v in macroStr.split("_"))
                else MacroValueType.UNKNOWN
            ),
        )

    if len(macroStr) < 2:
        return None

    if macroStr[0] != "<" and macroStr[-1] != ">":
        return None

    macroStr = macroStr.removeprefix("<").removesuffix(">")

    if all(v in utils.ASCII_LETTER_SET or v == "." or v.isdecimal() for v in macroStr):
        # <<ATTRIBUTE.ACCESS>>
        return Macro(
            macroStr,
            (
                MacroValueType.ATTRIBUTE_ACCESS
                if all(len(v) for v in macroStr.split("_"))
                else MacroValueType.UNKNOWN
            ),
        )

    return Macro(val, MacroValueType.UNKNOWN)


def attrAccess(fleetInfo: FleetInfo, macro: Macro) -> str:
    if macro.type is not MacroValueType.ATTRIBUTE_ACCESS:
        return ""

    result: str = ""

    match macroSplit := macro.value.split("."):
        case ["Ship", posRaw, *attrs] if posRaw in OrderTranslate.ship(set) and len(
            attrs
        ):
            LOGGER.debug(f"get Ship[{posRaw = }. {attrs = }]")

            pos = (
                getattr(_ORDER_SHIP_TRANSLATE, posRaw)
                if posRaw in OrderTranslate.shipName(set)
                else _ORDER_SHIP_TRANSLATE(int(posRaw))
            )

            targetShip = (
                fleetInfo.unionFleet.ships[pos]
                if fleetInfo.isUnion and fleetInfo.unionFleet is not None
                else fleetInfo.mainFleet().ships[pos]
            )

            match attrs:
                case ["slot", equipmentPosRaw] if equipmentPosRaw in {
                    v for v in OrderTranslate.equipment(set) if not (v in {"X", "99"})
                }:
                    equipmentPos = (
                        getattr(_ORDER_EQUIPMENT_TRANSLATE, equipmentPosRaw)
                        if equipmentPosRaw in OrderTranslate.equipmentName(set)
                        else _ORDER_EQUIPMENT_TRANSLATE(int(equipmentPosRaw))
                    )
                    LOGGER.debug(f"{equipmentPos = }")

                    _r = None

                    LOGGER.debug(f"{targetShip.data.slots = }")

                    try:
                        targetSlot = targetShip.data.slots[equipmentPos]
                    except IndexError as e:
                        LOGGER.debug(f"{e = }")
                        targetSlot = None

                    LOGGER.debug(f"{targetSlot = }")

                    _r = str(targetSlot) if isinstance(targetSlot, int) else None
                    result = _r if _r is not None else ""

                case [
                    "equipment",
                    equipmentPosRaw,
                    *equipmentAttrs,
                ] if equipmentPosRaw in OrderTranslate.equipment(set) and len(
                    equipmentAttrs
                ) >= 1:
                    LOGGER.debug(f"{equipmentPosRaw = } {equipmentAttrs = }")
                    equipmentPos = (
                        getattr(_ORDER_EQUIPMENT_TRANSLATE, equipmentPosRaw)
                        if equipmentPosRaw in OrderTranslate.equipmentName(set)
                        else _ORDER_EQUIPMENT_TRANSLATE(int(equipmentPosRaw))
                    )

                    _r = None

                    targetEquipment = (
                        targetShip.items[equipmentPos]
                        if equipmentPosRaw != "X"
                        or equipmentPos != _ORDER_EQUIPMENT_TRANSLATE.X
                        else targetShip.exItem
                    )
                    LOGGER.debug(f"{targetEquipment = }")

                    try:
                        _r = operator.attrgetter(".".join(equipmentAttrs))(
                            targetEquipment
                        )
                    except Exception as e:
                        LOGGER.error(f"{e}")
                        _r = None

                    if _r is not None:
                        result = str(_r) if not isinstance(_r, str) else _r
                        if isinstance(_r, EquipmentTypes):
                            result = str(_r.value)
                        LOGGER.debug(f"{result = }")
                case _:
                    _r = None

                    try:
                        _r = operator.attrgetter(".".join(attrs))(targetShip)
                    except Exception as e:
                        LOGGER.error(f"{e = }")
                        _r = None

                    if _r is not None:
                        result = str(_r) if not isinstance(_r, str) else _r
                        LOGGER.debug(f"{result = }")

        case ["Fleet", fleet, *attrs] if fleet in {"A", "B", "U"} and len(attrs):
            if not fleetInfo.isUnion and fleet == "U":
                LOGGER.debug("Try to access union fleet but there isn't!")
                return ""

            targetFleet = {
                "A": fleetInfo.fleets[0],
                "B": fleetInfo.fleets[1],
                "C": fleetInfo.fleets[2],
                "D": fleetInfo.fleets[3],
                "U": fleetInfo.unionFleet,
            }.get(fleet)

            if targetFleet is None:
                LOGGER.error(f"Unknown {targetFleet = }")
                return ""

            match attrs:
                case ["los", level] if level in {"A", "B", "C", "D"}:
                    _lookUpSplit = {"A": 0, "B": 1, "C": 2, "D": 3}.get(level, None)

                    if _lookUpSplit is None:
                        LOGGER.error(f"unknown {level = }")
                        result = ""
                    else:
                        result = (
                            str(
                                Fleet.getUnionScoutScore(
                                    targetFleet, fleetInfo.admiralLevel
                                )[_lookUpSplit]
                            )
                            if fleetInfo.isUnion
                            else str(
                                Fleet.getScoutScore(
                                    targetFleet.ships, fleetInfo.admiralLevel
                                )[_lookUpSplit]
                            )
                        )
                        LOGGER.debug(f"{result = }")
                case _:
                    try:
                        _r = operator.attrgetter(".".join(attrs))(targetFleet)
                    except Exception as e:
                        LOGGER.error(e)
                        _r = None

                    if _r is not None:
                        result = str(_r) if not isinstance(_r, str) else _r
                        LOGGER.debug(f"{result = }")

        case _:
            LOGGER.debug(f"unknown pattern: {macroSplit!r}")

    return result


class _AttrAccessAirbase:
    @classmethod
    def access(cls, airbaseInfo: AirbaseInfo, macro: Macro) -> str:
        if macro.type is not MacroValueType.ATTRIBUTE_ACCESS:
            return ""

        result: str = ""

        match macroSplit := macro.value.split("."):
            case [
                "Airbase",
                airbasePos,
                "equipment",
                equipmentPos,
                *attrs,
            ] if airbasePos in OrderTranslate.airbaseName(
                set
            ) and equipmentPos in OrderTranslate.airbaseEquipmentName(
                set
            ):
                _abPos = {v.name: v.value for v in _ORDER_AIRBASE_TRANSLATE}.get(
                    airbasePos, None
                )

                if _abPos is None:
                    return ""

                LOGGER.debug(f"{equipmentPos = }")

                _ePos = {
                    v.name: v.value for v in _ORDER_AIRBASE_EQUIPMENT_TRANSLATE
                }.get(equipmentPos, None)
                if _ePos is None:
                    return ""

                targetAirbase = airbaseInfo.airbases[_abPos]
                targetEquipment = targetAirbase.items[_ePos]

                LOGGER.debug(f"{targetAirbase = }")
                LOGGER.debug(f"{targetEquipment = }")

                try:
                    _r = operator.attrgetter(".".join(attrs))(targetEquipment)
                except Exception as e:
                    LOGGER.error(e)
                    _r = None

                LOGGER.debug(f"{type(_r) = }")

                if _r is not None:
                    if isinstance(_r, Enum):
                        result = str(_r.value)
                    elif not isinstance(_r, str):
                        result = str(_r)
                    else:
                        result = _r

                    LOGGER.debug(f"{result = }")

            case [
                "Airbase",
                airbasePos,
                *attrs,
            ] if airbasePos in OrderTranslate.airbaseName(set):
                _lookUpPos = {v.name: v.value for v in _ORDER_AIRBASE_TRANSLATE}.get(
                    airbasePos, None
                )
                if _lookUpPos is None:
                    return ""

                if _lookUpPos == 0:
                    result = cls._accessInfoGeneral(airbaseInfo, attrs)
                else:
                    result = cls._accessGeneral(airbaseInfo, _lookUpPos, attrs)

            case _:
                LOGGER.debug(f"unknown pattern: {macroSplit!r}")

        return result

    @classmethod
    def _accessGeneral(
        cls, airbaseInfo: AirbaseInfo, pos: int, attrs: Sequence[str]
    ) -> str:
        targetAirbase = airbaseInfo.airbases[pos]
        result: str = ""

        try:
            _r = operator.attrgetter(".".join(attrs))(targetAirbase)
        except Exception as e:
            LOGGER.error(e)
            _r = None

        if _r is not None:
            # result = str(_r) if not isinstance(_r, str) else _r

            if isinstance(_r, Enum):
                result = str(_r.value)
            elif not isinstance(_r, str):
                result = str(_r)
            else:
                result = _r

            LOGGER.debug(f"{result = }")

        return result

    @classmethod
    def _accessInfoGeneral(cls, airbaseInfo: AirbaseInfo, attrs: Sequence[str]) -> str:
        result: str = ""

        try:
            _r = operator.attrgetter(".".join(attrs))(airbaseInfo)
        except Exception as e:
            LOGGER.error(e)
            _r = None

        if _r is not None:
            # result = str(_r) if not isinstance(_r, str) else _r

            if isinstance(_r, Enum):
                result = str(_r.value)
            elif not isinstance(_r, str):
                result = str(_r)
            else:
                result = _r

            LOGGER.debug(f"{result = }")

        return result


class _AttrAccessFleet: ...


class AttrAccess:
    Airbase = _AttrAccessAirbase()
    Fleet = _AttrAccessFleet()


@dataclass(slots=True)
class PreDefineMacro:
    fleetInfo: FleetInfo
    airbaseInfo: AirbaseInfo
    translator: Translator

    _macroLookUpCache: dict[str, str] = field(init=False)
    _latexLookUpCache: dict[str, str] = field(init=False)

    def __post_init__(self):
        self._macroLookUpCache = {}
        self._latexLookUpCache = {}

        self._define_airbase()
        self._define_airbase_equipment()
        self._define_fleet()
        self._define_ship()
        self._define_equipment()

    @property
    def macroLookUp(self) -> dict[str, str]:
        return self._macroLookUpCache

    @property
    def latexLoopUp(self) -> dict[str, str]:
        return self._latexLookUpCache

    def _attrAccess(self, macro: Macro):
        if macro.value.startswith("Airbase"):
            return AttrAccess.Airbase.access(self.airbaseInfo, macro)

        return attrAccess(self.fleetInfo, macro)

    def _define_template(
        self,
        _pos: str,
        _latex: str,
        _macro: str,
        _access: str,
        _default: str = "",
        _functionWrapper: Callable[[Any], str] | None = None,
    ):
        _latex = _latex.format(_pos)
        _macro = _macro.format(_pos)
        _access = _access.format(_pos)

        LOGGER.debug(f"{_latex = }, {_macro = }, {_access = }")

        _accessResult: str = ""

        try:
            _attrAccessResult = self._attrAccess(
                Macro(_access, MacroValueType.ATTRIBUTE_ACCESS)
            )
            _accessResult = (
                _attrAccessResult
                if _functionWrapper is None
                else _functionWrapper(_attrAccessResult)
            )
            LOGGER.debug(f"{_accessResult = }")
        except IndexError as e:
            LOGGER.debug(f"{e = } {_pos = }")
        finally:
            self._macroLookUpCache.update({_macro: _accessResult})
            self._latexLookUpCache.update({_latex: _accessResult})

    def _define_airbase(self):
        for airbasePos in OrderTranslate.airbaseName(tuple):
            LOGGER.debug(f"{airbasePos = }")

            def _base(_l: str, _m: str, _a: str) -> tuple[str, str, str]:
                return (
                    rf"\airbase{airbasePos}{_l}",
                    f"AIRBASE_{airbasePos}_{_m}",
                    f"Airbase.{airbasePos}.{_a}",
                )

            self._define_template(
                airbasePos, *_base("fullAirPower", "FULL_AIRPOWER", "fullAirPower")
            )
            self._define_template(
                airbasePos,
                *_base("defenseAirPower", "DEFENSE_AIRPOWER", "defenseAirPower"),
            )
            self._define_template(
                airbasePos,
                *_base(
                    "highDefenseAirPower",
                    "HIGH_DEFENSE_AIRPOWER",
                    "highDefenseAirPower",
                ),
            )
            self._define_template(
                airbasePos,
                *_base(
                    "mode",
                    "MODE",
                    "mode",
                ),
            )
            self._define_template(
                airbasePos,
                *_base(
                    "radius",
                    "RADIUS",
                    "radius",
                ),
            )

    def _define_airbase_equipment(self):
        for airbasePos in OrderTranslate.airbaseName(tuple):
            LOGGER.debug(f"{airbasePos = }")

            for equipmentPos in OrderTranslate.airbaseEquipmentName(tuple):
                LOGGER.debug(f"{equipmentPos = }")

                def _base(_l: str, _m: str, _a: str) -> tuple[str, str, str]:
                    return (
                        rf"\airbase{airbasePos}equipment{equipmentPos}{_l}",
                        f"AIRBASE_{airbasePos}_EQUIPMENT_{equipmentPos}_{_m}",
                        f"Airbase.{airbasePos}.equipment.{equipmentPos}.{_a}",
                    )

                self._define_template(
                    airbasePos,
                    *_base(
                        "nameJp",
                        "NAME_JP",
                        "data.name",
                    ),
                )
                self._define_template(
                    airbasePos,
                    *_base(
                        "nameEn",
                        "NAME_EN",
                        "data.name",
                    ),
                    _functionWrapper=self.translator.translate_equipment,
                )
                self._define_template(
                    airbasePos,
                    *_base(
                        "remodel",
                        "REMODEL",
                        "remodel",
                    ),
                )
                self._define_template(
                    airbasePos,
                    *_base(
                        "levelAlt",
                        "LEVEL_ALT",
                        "levelAlt",
                    ),
                )
                self._define_template(
                    airbasePos,
                    *_base(
                        "id",
                        "ID",
                        "data.id",
                    ),
                )
                self._define_template(
                    airbasePos,
                    *_base(
                        "typeid",
                        "TYPEDID",
                        "data.apiTypeId",
                    ),
                )

                self._define_template(
                    airbasePos,
                    *_base(
                        "iconid",
                        "ICONID",
                        "data.iconTypeId",
                    ),
                )
                self._define_template(
                    equipmentPos,
                    *_base("equipped", "EQUIPPED", "data.id"),
                    _functionWrapper=lambda v: str(int(bool(int(v)))),
                )

    def _define_fleet(self):
        for fleetPos in ("A", "B", "C", "D", "U"):
            LOGGER.debug(f"{fleetPos = }")

            def _base(_l: str, _m: str, _a: str) -> tuple[str, str, str]:
                return (
                    rf"\fleet{fleetPos}{_l}",
                    f"FLEET_{fleetPos}_{_m}",
                    f"Fleet.{fleetPos}.{_a}",
                )

            for losPos in ("A", "B", "C", "D"):
                LOGGER.debug(f"{losPos = }")

                self._define_template(
                    losPos,
                    *_base(r"los{}", r"LOS_{}", r"los.{}"),
                    _functionWrapper=lambda v: str(
                        math.floor(100 * utils.convert(v, float, 0)) / 100
                    ),
                )

            self._define_template(
                fleetPos, *_base("fullAirPower", "FULL_AIRPOWER", "fullAirPower")
            )

            self._define_template(
                fleetPos, *_base("speedKanji", "SPEED_KANJI", "fleetSpeed")
            )

            self._define_template(
                fleetPos,
                *_base("speedNum", "SPEED_NUM", "fleetSpeed"),
                _functionWrapper=lambda v: str(
                    {
                        "最速": 20,
                        "高速+": 15,
                        "高速": 10,
                        "低速統一": 5,
                        "低速": 1,
                    }.get(v, 0)
                ),
            )

    def _define_ship(self):
        for shipPos in OrderTranslate.shipName(tuple):

            def _base(_l: str, _m: str, _a: str) -> tuple[str, str, str]:
                return (
                    rf"\ship{{}}{_l}",
                    f"SHIP_{{}}_{_m}",
                    f"Ship.{{}}.{_a}",
                )

            LOGGER.debug(f"{shipPos = }")

            self._define_template(shipPos, *_base("nameJp", "NAME_JP", "data.name"))
            self._define_template(
                shipPos,
                *_base("nameEn", "NAME_EN", "data.name"),
                _functionWrapper=self.translator.translate_ship,
            )
            self._define_template(shipPos, *_base("level", "LEVEL", "level"))
            self._define_template(
                shipPos, *_base("fullAirPower", "FULL_AIRPOWER", "fullAirPower")
            )

            self._define_template(shipPos, *_base("id", "ID", "data.id"))

            # Display Status
            self._define_template(
                shipPos,
                *_base(
                    "displayStatusHp",
                    "DISPLAYSTATUS_HP",
                    "displayStatus.HP",
                ),
            )
            self._define_template(
                shipPos,
                *_base(
                    "displayStatusFirePower",
                    "DISPLAYSTATUS_FIREFPOWER",
                    "displayStatus.firePower",
                ),
            )
            self._define_template(
                shipPos,
                *_base(
                    "displayStatusArmor",
                    "DISPLAYSTATUS_ARMOR",
                    "displayStatus.armor",
                ),
            )
            self._define_template(
                shipPos,
                *_base(
                    "displayStatusTorpedo",
                    "DISPLAYSTATUS_TORPEDO",
                    "displayStatus.torpedo",
                ),
            )
            self._define_template(
                shipPos,
                *_base(
                    "displayStatusAvoid",
                    "DISPLAYSTATUS_AVOID",
                    "displayStatus.avoid",
                ),
            )
            self._define_template(
                shipPos,
                *_base(
                    r"displayStatusAntiAir",
                    "DISPLAYSTATUS_ANTIAIR",
                    "displayStatus.antiAir",
                ),
            )
            self._define_template(
                shipPos,
                *_base(
                    "displayStatusAsw",
                    "DISPLAYSTATUS_ASW",
                    "displayStatus.asw",
                ),
            )
            self._define_template(
                shipPos,
                *_base(
                    r"displayStatusLos",
                    "DISPLAYSTATUS_LOS",
                    "displayStatus.LoS",
                ),
            )
            self._define_template(
                shipPos,
                *_base(
                    "displayStatusLuck",
                    "DISPLAYSTATUS_LUCK",
                    "displayStatus.luck",
                ),
            )
            self._define_template(
                shipPos,
                *_base(
                    "displayStatusRange",
                    "DISPLAYSTATUS_RANGE",
                    "displayStatus.range",
                ),
            )
            self._define_template(
                shipPos,
                *_base(
                    "displayStatusAccuracy",
                    "DISPLAYSTATUS_ACCURACY",
                    "displayStatus.accuracy",
                ),
            )
            self._define_template(
                shipPos,
                *_base(
                    "displayStatusBomber",
                    "DISPLAYSTATUS_BOMBER",
                    "displayStatus.bomber",
                ),
            )

            for equipmentPos in (
                v for v in OrderTranslate.equipmentName(tuple) if v != "X"
            ):
                self._define_template(
                    shipPos,
                    *_base(
                        f"slot{equipmentPos}",
                        f"SLOT_{equipmentPos}",
                        f"slot.{equipmentPos}",
                    ),
                )

    def _define_equipment(self):
        for shipPos in OrderTranslate.shipName(tuple):
            LOGGER.debug(f"{shipPos = }")

            def _base(_l: str, _m: str, _a: str) -> tuple[str, str, str]:
                return (
                    rf"\ship{shipPos}equipment{{}}{_l}",
                    f"SHIP_{shipPos}_EQUIPMENT_{{}}_{_m}",
                    f"Ship.{shipPos}.equipment.{{}}.{_a}",
                )

            for equipmentPos in OrderTranslate.equipmentName(set):

                LOGGER.debug(f"{equipmentPos = }")

                self._define_template(
                    equipmentPos, *_base("nameJp", "NAME_JP", "data.name")
                )
                self._define_template(
                    equipmentPos,
                    *_base("nameEn", f"NAME_EN", f"data.name"),
                    _functionWrapper=self.translator.translate_equipment,
                )
                self._define_template(
                    equipmentPos, *_base("remodel", f"REMODEL", f"remodel")
                )
                self._define_template(
                    equipmentPos, *_base("levelAlt", "LEVEL_ALT", "levelAlt")
                )
                self._define_template(equipmentPos, *_base("id", "ID", "data.id"))
                self._define_template(
                    equipmentPos, *_base("typeid", "TYPEID", "data.apiTypeId")
                )
                self._define_template(
                    equipmentPos, *_base("iconid", "ICONID", "data.iconTypeId")
                )
                self._define_template(
                    equipmentPos,
                    *_base("equipped", "EQUIPPED", "data.id"),
                    _functionWrapper=lambda v: str(int(bool(int(v)))),
                )
