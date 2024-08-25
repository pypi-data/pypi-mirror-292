import argparse
import json
import logging
import sys
from dataclasses import asdict
from dataclasses import dataclass
from importlib.metadata import version
from io import TextIOWrapper

from typing_extensions import Literal
from typing_extensions import Sequence

from . import database
from .logger import LOGGER
from .services.preprocessor.process import Process
from .services.translator.translator import Translator
from .services.translator.translator import TranslatorBuilder
from .types import Convert


def argumentParser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kancolatex",
        description="a tool generate latex from AirDefense Calculator",
    )

    parser.add_argument(
        "-m",
        "--mode",
        metavar="mode",
        type=str,
        choices=["default", "export", "translate"],
        default="default",
        help="operation Mode, option: [default, export, translate]",
    )

    parser.add_argument(
        "-n",
        "--noro",
        metavar="fleet.json",
        type=argparse.FileType("r"),
        help="path to the fleet json.",
    )

    parser.add_argument(
        "-t",
        "--template",
        metavar="template.tex",
        type=argparse.FileType("r"),
        help="path to the template latex file.",
    )

    parser.add_argument(
        "-o",
        "--output",
        metavar="output.tex",
        type=argparse.FileType("w"),
        help="path to the output latex file. If not specific the result will be display to stdout.",
    )

    parser.add_argument(
        "--update",
        action="store_true",
        help="update ship, equipment and fit bonus.",
    )

    parser.add_argument(
        "--reset",
        action="store_true",
        help="reset the database. Old record will be missing.",
    )

    parser.add_argument("--debug", action="store_true", help="enable debug message")

    parser.add_argument(
        "-tse",
        "--translation-ships-en",
        metavar="translation_ships_en.json",
        type=argparse.FileType("r"),
        help="path to the json of english translation for ships",
    )

    parser.add_argument(
        "-tee",
        "--translation-equipments-en",
        metavar="translation_equipment_en.json",
        type=argparse.FileType("r"),
        help="path to the json of english translation for equipments",
    )

    parser.add_argument("--version", action="store_true", help="current version")

    parser.add_argument(
        "--export-type",
        metavar="export_type",
        type=str,
        choices=["airbase", "fleet"],
        help="target type want to export, option: [airbase, fleet]",
    )

    parser.add_argument(
        "--translate-type",
        metavar="translate_type",
        type=str,
        choices=["ship", "equipment"],
        help="target type want to translate, option: [ship, equipment]",
    )

    parser.add_argument(
        "--translate-target",
        metavar="translate_target",
        type=str,
        help="target want to translate",
    )

    return parser


@dataclass(slots=True)
class Args:
    mode: Literal["default", "export", "translate"]
    noro: TextIOWrapper | None
    template: TextIOWrapper | None
    output: TextIOWrapper | None
    update: bool
    reset: bool
    debug: bool
    translation_ships_en: TextIOWrapper | None
    translation_equipments_en: TextIOWrapper | None
    version: bool
    export_type: Literal["airbase", "fleet"] | None
    translate_type: Literal["ship", "equipment"] | None
    translate_target: str | None


_SUCCESS = 0
_ERROR = 1


class _Helper:
    @classmethod
    def mode_Default(cls, args: Args) -> int:
        if args.noro and args.template:

            fleetInfo = cls._createFleetInfo(args.noro)
            if fleetInfo is None:
                return _ERROR

            args.noro.seek(0)

            airbaseInfo = cls._createAirbaseInfo(args.noro)
            if airbaseInfo is None:
                return _ERROR

            _translator = cls._createTranslator(
                args.translation_ships_en, args.translation_equipments_en
            )

            p = Process(fleetInfo, airbaseInfo, args.template, _translator)
            result = p.process()
            if not p.errorCount:
                cls._write(args, result.getvalue())

        elif args.noro and args.template is None:
            LOGGER.info("Please provide a template.")
            return _ERROR
        elif args.noro is None and args.template:
            LOGGER.info("Please provide a deck builder json.")
            return _ERROR

        return _SUCCESS

    @classmethod
    def mode_Export(cls, args: Args) -> int:
        if args.noro is None:
            LOGGER.info("Please provide a deck builder json.")
            return _ERROR

        import pydantic

        class _J(json.JSONEncoder):
            def default(self, o: object):
                if isinstance(o, pydantic.BaseModel):
                    return o.model_dump()

                return super().default(o)

        if args.export_type is None:
            LOGGER.info("Please provide a target to export.")
            return _ERROR

        if args.export_type == "fleet":
            fleetInfo = cls._createFleetInfo(args.noro)
            if fleetInfo is None:
                return _ERROR
            else:
                cls._write(
                    args, json.dumps(asdict(fleetInfo), cls=_J, ensure_ascii=False)
                )
        elif args.export_type == "airbase":
            airbaseInfo = cls._createAirbaseInfo(args.noro)
            if airbaseInfo is None:
                return _ERROR

            else:
                cls._write(
                    args, json.dumps(asdict(airbaseInfo), cls=_J, ensure_ascii=False)
                )
        return _SUCCESS

    @classmethod
    def mode_Translate(cls, args: Args) -> int:
        if args.translate_target is None:
            LOGGER.info("Please provide a target to translate.")
            return _ERROR

        _translator = cls._createTranslator(
            args.translation_ships_en, args.translation_equipments_en
        )

        _translateResult: str = ""
        if args.translate_type == "ship":
            _translateResult = _translator.translate_ship(args.translate_target)
        elif args.translate_type == "equipment":
            _translateResult = _translator.translate_equipment(args.translate_target)

        cls._write(args, _translateResult)

        return _SUCCESS

    @classmethod
    def _createFleetInfo(cls, _f: TextIOWrapper):
        fleetInfo = Convert.loadDeckBuilderToFleetInfo(_f.read())

        if fleetInfo is None:
            LOGGER.fatal("fleetInfo is None")
            return None

        return fleetInfo

    @classmethod
    def _createAirbaseInfo(cls, _f: TextIOWrapper):
        airbaseInfo = Convert.loadDeckBuilderToAirbaseInfo(_f.read())

        if airbaseInfo is None:
            LOGGER.fatal("airbaseInfo is None")
            return None

        return airbaseInfo

    @classmethod
    def _createTranslator(cls, _s: TextIOWrapper | None, _e: TextIOWrapper | None):
        return Translator(
            builder=TranslatorBuilder(
                (json.loads(_s.read()) if _s is not None else dict()),
                (json.loads(_e.read()) if _e is not None else dict()),
            )
        )

    @staticmethod
    def _write(args: Args, value: str):
        if args.output:
            args.output.write(value)
        else:
            print(value)


def _main(argv: Sequence[str] | None = None) -> int:

    parser = argumentParser()
    _parsedResult = parser.parse_args(argv)
    args = Args(**vars(_parsedResult))

    if args.debug:
        LOGGER.setLevel(logging.DEBUG)
        setattr(_parsedResult, "debug", False)
    setattr(_parsedResult, "mode", "")

    LOGGER.debug(f"{args = }")

    if all(not v for v in vars(_parsedResult).values()):
        parser.print_help()

    if args.version:
        print(version("kancolatex"))
        return _SUCCESS

    if args.reset:
        try:
            database.dbReset()
        except Exception as e:
            LOGGER.fatal(e)
            return _ERROR

    if args.update:
        try:
            database.dbUpdate()
        except Exception as e:
            LOGGER.fatal(e)
            return _ERROR

    if args.mode == "default":
        return _Helper.mode_Default(args)
    elif args.mode == "export":
        return _Helper.mode_Export(args)
    elif args.mode == "translate":
        return _Helper.mode_Translate(args)

    return _SUCCESS


def main():
    sys.exit(_main())
