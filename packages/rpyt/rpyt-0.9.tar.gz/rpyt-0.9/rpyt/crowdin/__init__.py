import json
import os
import re
import shutil
from typing import Any, cast

import rpyt
from rpyt.common import hash_object, load_from_module, read_tab, rreplace
from rpyt.crowdin.common import (
    CROWDIN_INPUTS_DIR,
    CROWDIN_OUTPUTS_DIR,
    GAME_COMMON,
    GAME_DIALOGUE,
    GAME_DIR,
    GAME_TL_DIR,
    RENPY_COMMON_DIR,
    RENPY_COMMON_NAME,
    RENPY_RPY_EXTENSION,
    RENPY_RPYM_EXTENSION,
    DialogueEntry,
)
from rpyt.crowdin.processor import Processor

CWD = os.path.dirname(rpyt.__file__)

RESOURCES_DIR = f"{CWD}/resources"
RESOURCES_COMMON_RPYM = (
    f"{RESOURCES_DIR}/{RENPY_COMMON_NAME}.{RENPY_RPYM_EXTENSION}.txt"
)
CROWDIN_DEFAULT_PROCESSOR: type[Processor] | str = (
    "rpyt.crowdin.json_with_context_processor.JsonWithContextProcessor"
)


def read_common(file=GAME_COMMON):
    if not os.path.exists(file):
        file = RESOURCES_COMMON_RPYM
    with open(file, encoding="utf-8") as fo:
        common = fo.read()
    pattern = r"^.*#\s(.+):(\d+)\n.*old\s['\"](.*)['\"]$"
    matches = re.findall(pattern, common, re.MULTILINE)
    rv: list[DialogueEntry] = []
    for match in matches:
        tpl = (None, None, match[2], match[0], int(match[1]), None)
        rv.append(DialogueEntry(hash_object(tpl), *tpl))
    return rv


def read_dialogue(file=GAME_DIALOGUE):
    rows = read_tab(file, "header")
    rows.pop(0)
    dialogue = list(
        map(
            lambda e: DialogueEntry(hash_object(e), *e),
            rows,
        )
    )
    return dialogue


def create_inputs(
    dir=CROWDIN_INPUTS_DIR,
    dialogue=GAME_DIALOGUE,
    common=GAME_COMMON,
    processor=CROWDIN_DEFAULT_PROCESSOR,
    **kwargs: Any,
):
    cdialogue = read_common(common)
    mdialogue = read_dialogue(dialogue)
    adialouge = cdialogue + mdialogue

    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir, exist_ok=True)

    files: dict[str, dict[str, Any]] = {}

    if isinstance(processor, str):
        processor = cast(type[Processor], load_from_module(processor))
    iprocessor = processor(**kwargs)

    for de in adialouge:
        path = de.filename
        if path.startswith(RENPY_COMMON_DIR):
            path = f"{dir}/{RENPY_COMMON_NAME}.{RENPY_RPY_EXTENSION}.json"
        else:
            path = rreplace(
                path.removeprefix(GAME_DIR + "/"),
                RENPY_RPYM_EXTENSION,
                RENPY_RPY_EXTENSION,
                1,
            )
            path = f"{dir}/{path}.json"
        if path not in files:
            file = files[path] = {}
        else:
            file = files[path]
        file[de.hash] = iprocessor.dump(de)

    totstrs = 0

    for path, content in files.items():
        dirname = os.path.dirname(path)
        os.makedirs(dirname, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fo:
            json.dump(content, fo, indent=4)
            totstrs += len(content)
            print(f"dumped {len(content)} string(s) into '{path}'")

    print(f"created {len(files)} file(s); dumped {totstrs} string(s)")


def translate(
    file: str,
    language: str,
    indent=4,
    dialogue: str | list[DialogueEntry] = GAME_DIALOGUE,
    common: str | list[DialogueEntry] = GAME_COMMON,
    processor=CROWDIN_DEFAULT_PROCESSOR,
    **kwargs: Any,
):
    cdialogue = read_common(common) if isinstance(common, str) else common
    mdialogue = (
        read_dialogue(dialogue) if isinstance(dialogue, str) else dialogue
    )
    adialouge = cdialogue + mdialogue

    with open(file, "r", encoding="utf-8") as fo:
        data: dict[str, Any] = json.load(fo)

    dstring_temp = """# {file}:{line}
translate {lang} {ident}:

{indent}# {oscript}
{indent}{nscript}
"""
    nstring_temp = """{indent}# {file}:{line}
{indent}old "{old}"
{indent}new "{new}"
"""

    strings: list[str] = []
    ndes: list[tuple[Any, DialogueEntry]] = []

    if isinstance(processor, str):
        processor = cast(type[Processor], load_from_module(processor))
    iprocessor = processor(**kwargs)

    for hkey, value in data.items():
        de = next((de for de in adialouge if de.hash == hkey), None)
        if de:
            if de.identifier and de.renpy_script:
                strings.append(
                    dstring_temp.format(
                        file=de.filename,
                        line=de.line_number,
                        lang=language,
                        ident=de.identifier,
                        oscript=rreplace(
                            de.renpy_script, "[what]", de.dialogue, 1
                        ),
                        nscript=rreplace(
                            de.renpy_script,
                            "[what]",
                            iprocessor.load(value),
                            1,
                        ),
                        indent=" " * indent,
                    )
                )
            else:
                ndes.append((value, de))

    if ndes:
        strings.append(f"translate {language} strings:\n")

    for value, de in ndes:
        if (not de.identifier) and (not de.renpy_script):
            strings.append(
                nstring_temp.format(
                    file=de.filename,
                    line=de.line_number,
                    old=de.dialogue,
                    new=iprocessor.load(value),
                    indent=" " * indent,
                )
            )

    return "\n".join(strings)


def translate_outputs(
    dir=CROWDIN_OUTPUTS_DIR,
    languages: dict[str, str] | list[str] | None = None,
    tl=GAME_TL_DIR,
    inputs=CROWDIN_INPUTS_DIR,
    dialogue=GAME_DIALOGUE,
    common=GAME_COMMON,
    processor=CROWDIN_DEFAULT_PROCESSOR,
    **kwargs: Any,
):
    cdialogue = read_common(common)
    mdialogue = read_dialogue(dialogue)

    alangs = list(
        map(lambda e: e.name, (e for e in os.scandir(dir) if e.is_dir()))
    )
    lmap: dict[str, str] = {}
    if languages is None:
        lmap.update({lang: lang for lang in alangs})
    elif isinstance(languages, list):
        lmap.update({lang: lang for lang in languages})
    else:
        lmap.update(languages)

    files: dict[str, str] = {}

    for inlang, outlang in lmap.items():
        inlangdir = f"{dir}/{inlang}"
        outlangdir = f"{tl}/{outlang}"

        nested_inlangdir = f"{inlangdir}/{inputs}"

        for dirpath, _, filenames in os.walk(inlangdir):
            dirpath = dirpath.replace("\\", "/")
            if dirpath.startswith(nested_inlangdir):
                for filename in filenames:
                    if filename.endswith(
                        (
                            f"{RENPY_RPY_EXTENSION}.json",
                            f"{RENPY_RPYM_EXTENSION}.json",
                        )
                    ):
                        file = f"{dirpath}/{filename}"
                        outpath = f"{outlangdir}/{dirpath.removeprefix(nested_inlangdir)[1:]}/{filename}".replace(
                            "//", "/"
                        ).removesuffix(".json")
                        files[outpath] = translate(
                            file,
                            outlang,
                            dialogue=mdialogue,
                            common=cdialogue,
                            processor=processor,
                            **kwargs,
                        )

    for path, content in files.items():
        dirname = os.path.dirname(path)
        os.makedirs(dirname, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fo:
            fo.write(content)
            print(f"created '{path}'")

    print(f"created {len(files)} file(s)")
