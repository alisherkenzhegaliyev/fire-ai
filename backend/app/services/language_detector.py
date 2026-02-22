"""
Rule-augmented language detector using lingua-language-detector.
Returns 'RU', 'KZ', or 'ENG'.
"""
import logging
import re

from lingua import Language, LanguageDetectorBuilder

log = logging.getLogger(__name__)

detector = LanguageDetectorBuilder.from_languages(
    Language.RUSSIAN,
    Language.KAZAKH,
    Language.ENGLISH
).build()

KZ_CHARS = set('әғқңөұүһіӘҒҚҢӨҰҮҺІ')

KZ_FUNCTION_WORDS = {
    'және', 'бұл', 'мен', 'бар', 'деп', 'үшін', 'бір', 'не',
    'да', 'де', 'ол', 'біз', 'сіз', 'жоқ', 'болды', 'бола',
    'туралы', 'дейін', 'егер', 'немесе', 'себебі'
}

ENGLISH_COMMON_WORDS = {
    'i', 'the', 'is', 'are', 'you', 'my', 'me', 'we', 'it',
    'to', 'in', 'of', 'and', 'a', 'an', 'this', 'that', 'for',
    'not', 'can', 'do', 'have', 'please', 'hello', 'hi', 'hey',
    'your', 'with', 'from', 'been', 'was', 'am', 'be', 'but',
    'they', 'there', 'what', 'how', 'why', 'when', 'will', 'no'
}

LANG_MAP = {
    Language.RUSSIAN: 'RU',
    Language.KAZAKH: 'KZ',
    Language.ENGLISH: 'ENG'
}

HIGH_CONFIDENCE = 0.8
LOW_CONFIDENCE = 0.4
ENG_MIN_CONFIDENCE = 0.90
KZ_CHAR_NOISE_THRESHOLD = 0.03
KZ_CHAR_STRONG_THRESHOLD = 0.15


def _preprocess(text: str) -> str:
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'FW:|RE:', '', text)
    return text.strip()


def _kz_char_ratio(text: str) -> float:
    alpha_chars = [c for c in text if c.isalpha()]
    if not alpha_chars:
        return 0.0
    kz_count = sum(1 for c in alpha_chars if c in KZ_CHARS)
    return kz_count / len(alpha_chars)


def _has_kz_function_words(text: str) -> bool:
    words = set(text.lower().split())
    return bool(words & KZ_FUNCTION_WORDS)


def _has_english_words(text: str) -> bool:
    words = set(text.lower().split())
    return bool(words & ENGLISH_COMMON_WORDS)


def detect_language(text: str) -> str:
    if not text or not text.strip():
        return 'RU'

    text = _preprocess(text)
    kz_ratio = _kz_char_ratio(text)
    has_kz_words = _has_kz_function_words(text)

    confidence_values = detector.compute_language_confidence_values(text)
    confidence_map = {LANG_MAP[cv.language]: cv.value for cv in confidence_values}

    top_lang = max(confidence_map, key=confidence_map.get)
    top_conf = confidence_map[top_lang]

    log.debug("Language confidences: %s", confidence_map)

    if top_conf >= HIGH_CONFIDENCE:
        if top_lang == 'ENG' and (top_conf < ENG_MIN_CONFIDENCE or not _has_english_words(text)):
            return 'RU'
        return top_lang

    if LOW_CONFIDENCE <= top_conf < HIGH_CONFIDENCE:
        if kz_ratio >= KZ_CHAR_STRONG_THRESHOLD or has_kz_words:
            return 'KZ'
        if top_lang == 'KZ' and top_conf < 0.55 and kz_ratio < KZ_CHAR_NOISE_THRESHOLD and not has_kz_words:
            ru_conf = confidence_map.get('RU', 0)
            eng_conf = confidence_map.get('ENG', 0)
            return 'ENG' if eng_conf > ru_conf else 'RU'
        return top_lang

    if kz_ratio >= KZ_CHAR_STRONG_THRESHOLD or has_kz_words:
        return 'KZ'

    return 'RU'
