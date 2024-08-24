from rpyt.crowdin.common import DialogueEntry
from rpyt.crowdin.processor import Processor


class StringProcessor(Processor):
    def dump(self, dialogue_entry: DialogueEntry):
        return dialogue_entry.dialogue

    def load(self, value: str):
        return value
