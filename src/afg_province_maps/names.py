"""Province name matching.

Data files and boundary files spell province names differently. Every name is
reduced to a comparison key: lower case, ASCII only, punctuation removed, suffixes
such as "Province" dropped, then known variants mapped to one canonical spelling.
Add a variant to ALIASES if a file fails to match.
"""
import re
import unicodedata

# variant (after normalisation) -> canonical key
ALIASES = {
    "ghanzi": "ghazni",  # geoBoundaries spelling of Ghazni
    "hilmand": "helmand",
    "nimroz": "nimruz",
    "kabol": "kabul",
    "sar e pol": "sar e pul",
    "bamiyan": "bamyan",
    "dai kundi": "daykundi",
    "daikundi": "daykundi",
    "nooristan": "nuristan",
    "jawzjan": "jowzjan",
    "jozjan": "jowzjan",
    "panjsher": "panjshir",
    "khowst": "khost",
    "wardag": "wardak",
    "zabol": "zabul",
    "paktya": "paktia",
    "urozgan": "uruzgan",
    "nangrahar": "nangarhar",
    "maidan wardak": "wardak",  # OCHA spelling of Wardak
}

_SUFFIX = re.compile(r"\s+(province|wilayat|wilayet)$")


def norm_name(name: str) -> str:
    """Return the comparison key for a province name."""
    text = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()
    text = _SUFFIX.sub("", text)
    return ALIASES.get(text, text)
