import json
import os
import re
from typing import Any, NotRequired, TypedDict

from rpyt.crowdin.common import CROWDIN_DIR, DialogueEntry
from rpyt.crowdin.processor import Processor


# as specified in: https://crowdin.com/store/apps/json-with-context
class Data(TypedDict):
    text: str
    crowdinContext: str


class Context(TypedDict):
    content: str
    values: NotRequired[dict[str, dict[str, Any]]]


class Contexts(TypedDict):
    standard: Context
    dialogue: Context


class JsonWithContextProcessor(Processor):
    CONTEXTS = f"{CROWDIN_DIR}/contexts.json"

    def __init__(self, contexts: str | None = None):
        if contexts is None and os.path.exists(self.CONTEXTS):
            contexts = self.CONTEXTS
        if contexts:
            with open(contexts, encoding="utf-8") as fo:
                self.contexts = Contexts(**json.load(fo))
        else:
            self.contexts = None

    def dump(self, dialogue_entry: DialogueEntry):
        ctx: Context | None = (
            (
                self.contexts["dialogue"]
                if dialogue_entry.identifier
                else self.contexts["standard"]
            )
            if self.contexts
            else None
        )
        if not ctx:
            return dialogue_entry.dialogue
        return Data(
            text=dialogue_entry.dialogue,
            crowdinContext=ctx["content"].format(
                **self.get_values(dialogue_entry, ctx.get("values", {}))
            ),
        )

    def load(self, value: Data):
        return value["text"]

    def get_values(
        self, dialogue_entry: DialogueEntry, values: dict[str, dict[str, Any]]
    ):
        de = dialogue_entry._asdict()
        for k, v in de.items():
            if k in values:
                key = next(
                    filter(lambda e: re.search(e, str(v)), values[k]), None
                )
                if key:
                    aval = values[k][key]
                    de[k] = (
                        str.format(aval, **de)
                        if isinstance(aval, str)
                        else aval
                    )
        return de
