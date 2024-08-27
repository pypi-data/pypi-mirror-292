import json
from typing import Optional, Dict


class Replacement(dict):
    """A span of text that has been detected as a named entity.

    Attributes
    ----------
    start : int
        The start index of the entity in the original text
    end : int
        The end index of the entity in the original text. The end index is exclusive.
    python_start : Optional[int]
        The start index in Python (if different from start)
    python_end : Optional[int]
        The end index in Python (if different from end)
    label : str
        The label of the entity
    text : str
        The substring of the original text that was detected as an entity
    new_text : Optional[str]
        The new text to replace the original entity
    score : float
        The confidence score of the detection
    example_redaction : Optional[str]
        An example redaction for the entity
    json_path : Optional[str]
        The JSON path of the entity in the original JSON document. This is only
        present if the input text was a JSON document.
    """

    def __init__(
        self,
        start: int,
        end: int,
        label: str,
        text: str,
        score: float,
        new_text: Optional[str] = None,
        example_redaction: Optional[str] = None,
        json_path: Optional[str] = None,
    ):
        self.start = start
        self.end = end
        self.label = label
        self.text = text
        self.newText = new_text
        self.score = score
        self.exampleRedaction = example_redaction
        self.jsonPath = json_path

        dict.__init__(
            self,
            start=start,
            end=end,
            label=label,
            text=text,
            score=score,
            **({} if new_text is None else {"newText": new_text}),
            **({} if example_redaction is None else {"exampleRedaction": example_redaction}),
            **({} if json_path is None else {"jsonPath": json_path}),
        )

    def describe(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_dict(self) -> Dict:
        out = {
            "start": self.start,
            "end": self.end,
            "label": self.label,
            "text": self.text,
            "score": self.score,
        }
        if self.newText is not None:
            out["newText"] = self.newText
        if self.exampleRedaction is not None:
            out["exampleRedaction"] = self.exampleRedaction
        if self.jsonPath is not None:
            out["jsonPath"] = self.jsonPath
        return out
