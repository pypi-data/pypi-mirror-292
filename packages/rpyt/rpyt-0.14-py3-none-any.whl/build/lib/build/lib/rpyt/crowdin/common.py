from typing import NamedTuple


class DialogueEntry(NamedTuple):
    hash: str
    identifier: str | None
    character: str | None
    dialogue: str
    filename: str
    line_number: int
    renpy_script: str | None


RENPY_COMMON_NAME = "common"
RENPY_RPY_EXTENSION = "rpy"
RENPY_RPYM_EXTENSION = f"{RENPY_RPY_EXTENSION}m"
RENPY_COMMON_DIR = f"renpy/{RENPY_COMMON_NAME}"
GAME_DIR = "game"
GAME_TL_DIR = f"{GAME_DIR}/tl"
GAME_COMMON = f"{GAME_TL_DIR}/None/{RENPY_COMMON_NAME}.{RENPY_RPYM_EXTENSION}"
GAME_DIALOGUE = "dialogue.tab"
CROWDIN_DIR = "crowdin"
CROWDIN_INPUTS_DIR = f"{CROWDIN_DIR}/inputs"
CROWDIN_OUTPUTS_DIR = f"{CROWDIN_DIR}/outputs"
