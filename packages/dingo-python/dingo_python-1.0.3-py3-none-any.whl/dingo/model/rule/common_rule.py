import re
import jieba
import langid
import textstat

from typing import List, Tuple
from hanziconv import HanziConv
from nltk.tokenize import WordPunctTokenizer


from dingo.model.model import Model
from dingo.model.modelres import ModelRes
from dingo.model.rule.base import BaseRule
from dingo.model.rule.common.detect_lang import decide_language_by_str
from dingo.model.rule.common.util import (normalize, base_rps_frac_chars_in_dupe_ngrams, get_stop_words,
                                          split_paragraphs, TextSlice, Extractor)
from dingo.config.config import DynamicRuleConfig


@Model.rule_register('QUALITY_IRRELEVANCE', [])
class CommonPatternSearch(BaseRule):
    """let user input pattern to search"""
    custom_config = DynamicRuleConfig(pattern = "your pattern")

    @classmethod
    def eval(cls, input_data: List[str]) -> ModelRes:
        assert len(input_data) == 1
        res = ModelRes()
        matches = re.findall(cls.custom_config.pattern, input_data[0])
        if matches:
            res.error_status = True
            res.error_type = 'QUALITY_IRRELEVANCE'
            res.error_name = cls.__name__
            res.error_reason = ','.join(list(set(matches)))
        return res


@Model.rule_register('QUALITY_INCOMPLETENESS', ['default','sft','pretrain','benchmark'])
class CommonColonEnd(BaseRule):
    """check whether the last char is ':'"""
    custom_config = DynamicRuleConfig()

    @classmethod
    def eval(cls, input_data: List[str]) -> ModelRes:
        assert len(input_data) == 1
        res = ModelRes()
        if len(input_data[0]) <= 0:
            return res
        if input_data[0][-1] == ':':
            res.error_status = True
            res.error_type = 'QUALITY_INCOMPLETENESS'
            res.error_name = cls.__name__
            res.error_reason = 'Ends with a colon.'
        return res


@Model.rule_register('QUALITY_INEFFECTIVENESS', ['default','sft','pretrain','benchmark','text_base_all'])
class CommonContentNull(BaseRule):
    """check whether content is null"""
    custom_config = DynamicRuleConfig()

    @classmethod
    def eval(cls, input_data: List[str]) -> ModelRes:
        assert len(input_data) == 1
        res = ModelRes()
        count = len(input_data[0].strip())
        if count == 0:
            res.error_status = True
            res.error_type = 'QUALITY_INEFFECTIVENESS'
            res.error_name = cls.__name__
            res.error_reason = 'Content is empty.'
        return res


@Model.rule_register('QUALITY_DISSIMILARITY', ['default','sft','pretrain','benchmark','text_base_all'])
class CommonDocRepeat(BaseRule):
    """check whether content repeats"""
    custom_config = DynamicRuleConfig()

    @classmethod
    def eval(cls, input_data: List[str]) -> ModelRes:
        assert len(input_data) == 1
        res = ModelRes()
        repeat_score = base_rps_frac_chars_in_dupe_ngrams(6, input_data[0])
        if repeat_score >= 80:
            res.error_status = True
            res.error_type = 'QUALITY_DISSIMILARITY'
            res.error_name = cls.__name__
            res.error_reason = 'Repeatability of text is too high, with ratio： ' + str(repeat_score)
        return res


@Model.rule_register('QUALITY_IRRELEVANCE', ['default','sft','pretrain','benchmark','text_base_all'])
class CommonHtmlEntity(BaseRule):
    """check whether content has html entity"""
    custom_config = DynamicRuleConfig(key_list=[
        "nbsp",
        "lt",
        "gt",
        "amp",
        "quot",
        "apos",
        "hellip",
        "ndash",
        "mdash",
        "lsquo",
        "rsquo",
        "ldquo",
        "rdquo",
    ])

    @classmethod
    def eval(cls, input_data: List[str]) -> ModelRes:
        assert len(input_data) == 1
        res = ModelRes()
        content = input_data[0]

        entities = cls.custom_config.key_list
        full_entities_1 = [f"&{entity}；" for entity in entities]
        full_entities_2 = [f"&{entity};" for entity in entities]
        full_entities_3 = [f"＆{entity};" for entity in entities]
        full_entities_4 = [f"＆{entity}；" for entity in entities]
        full_entities = full_entities_1 + full_entities_2 + full_entities_3 + full_entities_4
        # half_entity_1 = [f"{entity}；" for entity in entities]
        half_entity_2 = [f"＆{entity}" for entity in entities]
        half_entity_3 = [f"&{entity}" for entity in entities]
        # half_entity_4 = [f"{entity};" for entity in entities]
        half_entities = half_entity_2 + half_entity_3
        # maked_entities = [f"{entity}" for entity in entities]
        all_entities = full_entities + half_entities

        error_entity = []
        for entity in all_entities:
            if entity in content:
                res.error_status = True
                res.error_type = 'QUALITY_IRRELEVANCE'
                res.error_name = cls.__name__
                error_entity.append(entity)
        if len(error_entity) != 0:
            res.error_reason = ','.join(list(set(error_entity)))
        return res


@Model.rule_register('QUALITY_INSECURITY', ['default','sft','pretrain','benchmark'])
class CommonIDCard(BaseRule):
    """check if the content contains ID card. """
    custom_config = DynamicRuleConfig(pattern = r"(身\s{0,10}份|id\s{0,10}number\s{0,10}|identification|identity|\s{0,10}ID\s{0,10}No\s{0,10}|id\s{0,10}card\s{0,10}|NRIC\s{0,10}number\s{0,10}|IC\s{0,10}number\s{0,10}|resident\s{0,10}registration\s{0,10}|I.D.\s{0,10}Number\s{0,10})")

    @classmethod
    def eval(cls, input_data: List[str]) -> ModelRes:
        assert len(input_data) == 1
        res = ModelRes()
        match = re.search(cls.custom_config.pattern, input_data[0], re.I)
        if match:
            person_id = Extractor().extract_id_card(input_data[0])
            if len(person_id) != 0:
                res.error_status = True
                res.error_type = 'QUALITY_INSECURITY'
                res.error_name = cls.__name__
                res.error_reason = "Contain ID card: " + str(person_id)
        return res


@Model.rule_register('QUALITY_DISFLUENCY', ['default','sft','pretrain','benchmark','text_base_all'])
class CommonNoPunc(BaseRule):
    """check whether content has paragraph without punctuations"""
    custom_config = DynamicRuleConfig()

    @classmethod
    def eval(cls, input_data: List[str]) -> ModelRes:
        assert len(input_data) == 1
        res = ModelRes()
        content = input_data[0]
        language = decide_language_by_str(content)
        if language != 'en':
            return res

        paragraphs = content.split('\n')
        longest_sentence = ''
        max_word_count = 0
        for paragraph in paragraphs:
            if len(paragraph.strip()) == 0:
                continue
            sentences = re.split("[-–.!?,;•/]", paragraph)
            for sentence in sentences:
                words = sentence.split()
                word_count = len(words)
                if word_count > max_word_count:
                    max_word_count = word_count
                    longest_sentence = sentence.strip()
        if int(max_word_count) > 56:
            res.error_status = True
            res.error_type = 'QUALITY_DISFLUENCY'
            res.error_name = cls.__name__
            res.error_reason = 'Paragraph without punctuation: ' + longest_sentence
        return res


@Model.rule_register('QUALITY_IRRELEVANCE', ['default','sft','pretrain','benchmark','text_base_all'])
class CommonSpecialCharacter(BaseRule):
    """check whether content has special characters. """
    custom_config = DynamicRuleConfig(
        key_list=[
            r"u200e",
            r"(\\\\;){3,}|(\{\}){3,}|(&nbsp;){3,}",
            r"&#247;|\? :",
            r"[�□]|\{\/U\}",
            r"U\+26[0-F][0-D]|U\+273[3-4]|U\+1F[3-6][0-4][0-F]|U\+1F6[8-F][0-F]"
        ]
    )

    @classmethod
    def eval(cls, input_data: List[str]) -> ModelRes:
        assert len(input_data) == 1
        res = ModelRes()
        content = input_data[0]

        matches = []
        for p in cls.custom_config.key_list:
            m = re.findall(p, content)
            matches = matches + m
        if len(matches) != 0:
            res.error_status = True
            res.error_type = 'QUALITY_IRRELEVANCE'
            res.error_name = cls.__name__
            res.error_reason = ','.join(list(set(matches)))
        return res


@Model.rule_register("QUALITY_IRRELEVANCE", [])
class CommonWatermark(BaseRule):
    """check whether content has watermarks."""
    custom_config = DynamicRuleConfig(key_list = [])

    @classmethod
    def eval(cls, input_data: List[str]) -> ModelRes:
        res = ModelRes()
        assert len(input_data) == 1
        matches = re.findall('|'.join(cls.custom_config.key_list), input_data[0])
        if matches:
            res.error_status = True
            res.error_type = 'QUALITY_IRRELEVANCE'
            res.error_name = cls.__name__
            res.error_reason = ','.join(list(set(matches)))
        return res


@Model.rule_register("QUALITY_INCOMPLETENESS", ['pretrain'])
class CommonWordNumber(BaseRule):
    """check whether the number of word in [20, 100000] """
    custom_config = DynamicRuleConfig()

    @classmethod
    def eval(cls, input_data: List[str]) -> ModelRes:
        assert len(input_data) == 1
        res = ModelRes()
        normalized_content = normalize(input_data[0])
        normalized_words = tuple(normalized_content.split())
        num_normalized_words = len(normalized_words)
        if num_normalized_words >= 20 and num_normalized_words < 100000:
            pass
        else:
            res.error_status = True
            res.error_type = 'QUALITY_INCOMPLETENESS'
            res.error_name = cls.__name__
            res.error_reason = "The number of word is: " + str(num_normalized_words)
        return res


@Model.rule_register('QUALITY_INEFFECTIVENESS', ['pretrain'])
class CommonMeanWordLength(BaseRule):
    """check whether the mean length of word in [3, 10] """
    custom_config = DynamicRuleConfig()

    @classmethod
    def eval(cls, input_data: List[str]) -> ModelRes:
        assert len(input_data) == 1
        res = ModelRes()
        normalized_content = normalize(input_data[0])
        normalized_words = tuple(normalized_content.split())
        num_normalized_words = len(normalized_words)
        if num_normalized_words == 0:
            return res

        num_chars = float(sum(map(len, normalized_words)))
        mean_length = num_chars / num_normalized_words
        mean_length = round(mean_length, 2)
        if mean_length >= 3 and mean_length < 10:
            pass
        else:
            res.error_status = True
            res.error_type = 'QUALITY_INEFFECTIVENESS'
            res.error_name = cls.__name__
            res.error_reason = "The mean length of word is: " + str(mean_length)
        return res


@Model.rule_register('QUALITY_INEFFECTIVENESS', ['sft','pretrain','benchmark'])
class CommonSymbolWordRatio(BaseRule):
    """check whether the ratio of symbol / word is > 0.1"""
    custom_config = DynamicRuleConfig(key_list = ["#", "...", "…"])

    @classmethod
    def eval(cls, input_data: List[str]) -> ModelRes:
        assert len(input_data) == 1
        res = ModelRes()
        raw_content = input_data[0]
        raw_words = tuple(WordPunctTokenizer().tokenize(raw_content))
        num_raw_words = len(raw_words)
        if num_raw_words == 0:
            return res

        num_words = num_raw_words
        num_symbols = float(sum(
            raw_content.count(x) for x in cls.custom_config.key_list
        ))

        ratio = num_symbols / num_words
        if ratio > 0.4:
            res.error_status = True
            res.error_type = 'QUALITY_INEFFECTIVENESS'
            res.error_name = cls.__name__
            res.error_reason = "The ratio of symbol / word is: " + str(ratio)
        return res


@Model.rule_register("QUALITY_INEFFECTIVENESS", ['pretrain'])
class CommonAlphaWords(BaseRule):
    """check whether the ratio of words that contain at least one alphabetic character > 0.6 """
    custom_config = DynamicRuleConfig()

    @classmethod
    def eval(cls, input_data: List[str]) -> ModelRes:
        assert len(input_data) == 1
        res = ModelRes()
        raw_content = input_data[0]
        raw_words = tuple(WordPunctTokenizer().tokenize(raw_content))
        num_raw_words = len(raw_words)
        if num_raw_words == 0:
            return res

        ALPHA_REGEX = re.compile(r"[a-zA-Z]")
        num_words = num_raw_words
        num_words_with_alpha = float(sum(
            int(ALPHA_REGEX.search(word) is not None)
            for word in raw_words
        ))
        ratio = num_words_with_alpha / num_words
        if ratio > 0.6:
            pass
        else:
            res.error_status = True
            res.error_type = 'QUALITY_INEFFECTIVENESS'
            res.error_name = cls.__name__
            res.error_reason = "The ratio of words that contain at least one alphabetic character is: " + str(ratio)
        return res


@Model.rule_register('QUALITY_INEFFECTIVENESS', ['pretrain'])
class CommonStopWord(BaseRule):
    """check whether the ratio of stop word > 2"""
    custom_config = DynamicRuleConfig()

    @classmethod
    def eval(cls, input_data: List[str]) -> ModelRes:
        assert len(input_data) == 1
        res = ModelRes()
        raw_content = input_data[0]
        raw_words = tuple(WordPunctTokenizer().tokenize(raw_content))
        num_raw_words = len(raw_words)
        if num_raw_words == 0:
            return res

        STOP_WORDS = get_stop_words("en")
        num_stop_words = sum(
            map(lambda w: w in STOP_WORDS, raw_words)
        )
        ratio = num_stop_words / num_raw_words
        if ratio < 0.06 or num_stop_words < 2:
            res.error_status = True
            res.error_type = 'QUALITY_INEFFECTIVENESS'
            res.error_name = cls.__name__
            res.error_reason = "The ratio of stop words is: " + str(ratio)
        return res


@Model.rule_register("QUALITY_INCOMPLETENESS", ['pretrain'])
class CommonSentenceNumber(BaseRule):
    """check whether the number of sentence >= 3 """
    custom_config = DynamicRuleConfig()

    @classmethod
    def eval(cls, input_data: List[str]) -> ModelRes:
        assert len(input_data) == 1
        res = ModelRes()
        raw_content = input_data[0]

        SENT_PATTERN = re.compile(r'\b[^.!?]+[.!?]*', flags=re.UNICODE)
        num_sentence = len(SENT_PATTERN.findall(raw_content))
        if num_sentence < 3 or num_sentence > 7500:
            res.error_status = True
            res.error_type = 'QUALITY_INCOMPLETENESS'
            res.error_name = cls.__name__
            res.error_reason = "The number of sentence is: " + str(num_sentence)
        return res


@Model.rule_register("QUALITY_DISUNDERSTANDABILITY", [])
class CommonCurlyBracket(BaseRule):
    """check whether content contains curly bracket: { or } """
    custom_config = DynamicRuleConfig(pattern = "[{}]")

    @classmethod
    def eval(cls, input_data: List[str]) -> ModelRes:
        assert len(input_data) == 1
        res = ModelRes()
        matches = re.findall(cls.custom_config.pattern, input_data[0])
        if matches:
            res.error_status = True
            res.error_type = 'QUALITY_DISUNDERSTANDABILITY'
            res.error_name = cls.__name__
            res.error_reason = ','.join(list(set(matches)))
        return res


@Model.rule_register("QUALITY_DISUNDERSTANDABILITY", ['pretrain'])
class CommonCapitalWords(BaseRule):
    """check whether capital words ratio > 0.3 """
    custom_config = DynamicRuleConfig()

    @classmethod
    def eval(cls, input_data: List[str]) -> ModelRes:
        assert len(input_data) == 1
        res = ModelRes()
        raw_content = input_data[0]
        raw_words = tuple(WordPunctTokenizer().tokenize(raw_content))
        num_raw_words = len(raw_words)
        if num_raw_words == 0:
            return res

        num_words = num_raw_words
        num_capital_words = sum([word.isupper() for word in raw_words])
        ratio = num_capital_words / num_words
        if ratio > 0.3 and ratio < 0.7:
            res.error_status = True
            res.error_type = 'QUALITY_DISUNDERSTANDABILITY'
            res.error_name = cls.__name__
            res.error_reason = "The ratio of capital words is: " + str(ratio)
        return res


@Model.rule_register("QUALITY_INEFFECTIVENESS", ['sft','pretrain','benchmark'])
class CommonLoremIpsum(BaseRule):
    """check whether the ratio of lorem ipsum < 3e-08 """
    custom_config = DynamicRuleConfig()

    @classmethod
    def eval(cls, input_data: List[str]) -> ModelRes:
        assert len(input_data) == 1
        res = ModelRes()
        normalized_content = normalize(input_data[0])
        num_normalized_content = len(normalized_content)
        if num_normalized_content == 0:
            return res

        SEARCH_REGEX = re.compile(r"lorem ipsum", re.IGNORECASE)
        num_occurrences = len(SEARCH_REGEX.findall(normalized_content))
        ratio = num_occurrences / num_normalized_content
        if ratio > 3e-08:
            res.error_status = True
            res.error_type = 'QUALITY_INEFFECTIVENESS'
            res.error_name = cls.__name__
            res.error_reason = "The ratio of lorem ipsum is: " + str(ratio)
        return res


@Model.rule_register("QUALITY_DISUNDERSTANDABILITY", ['pretrain'])
class CommonUniqueWords(BaseRule):
    """check whether the ratio of unique words > 0.1"""
    custom_config = DynamicRuleConfig()

    @classmethod
    def eval(cls, input_data: List[str]) -> ModelRes:
        assert len(input_data) == 1
        res = ModelRes()
        normalized_content = normalize(input_data[0])
        normalized_words = tuple(normalized_content.split())
        num_normalized_words = len(normalized_words)
        if num_normalized_words == 0:
            return res

        num_words = num_normalized_words
        num_unique_words = len(set(normalized_words))
        ratio = num_unique_words / num_words
        if ratio > 0.1:
            pass
        else:
            res.error_status = True
            res.error_type = 'QUALITY_DISUNDERSTANDABILITY'
            res.error_name = cls.__name__
            res.error_reason = "The ratio of unique words is: " + str(ratio)
        return res


@Model.rule_register("QUALITY_INEFFECTIVENESS", ['pretrain'])
class CommonCharNumber(BaseRule):
    """check whether the number of char > 100 """
    custom_config = DynamicRuleConfig(threshold = 100)

    @classmethod
    def eval(cls, input_data: List[str]) -> ModelRes:
        assert len(input_data) == 1
        res = ModelRes()
        text = input_data[0]
        text = text.strip()
        text = text.replace(" ", "")
        text = text.replace("\n", "")
        text = text.replace("\t", "")
        num_char = len(text)
        if num_char < cls.custom_config.threshold:
            res.error_status = True
            res.error_type = 'QUALITY_INEFFECTIVENESS'
            res.error_name = cls.__name__
            res.error_reason = "The number of char is: " + str(num_char)
        return res


@Model.rule_register("QUALITY_DISUNDERSTANDABILITY", ['sft','pretrain','benchmark'])
class CommonLineStartWithBulletpoint(BaseRule):
    """check whether lines start with bullet points. """
    custom_config = DynamicRuleConfig(key_list = [
        "\u2022",  # bullet point
        "\u2023",  # triangular bullet point
        "\u25B6",  # black right pointing triangle
        "\u25C0",  # black left pointing triangle
        "\u25E6",  # white bullet point
        "\u25A0",  # black square
        "\u25A1",  # white square
        "\u25AA",  # black small square
        "\u25AB",  # white small square
        "\u2013",  # en dash
    ])

    @classmethod
    def eval(cls, input_data: List[str]) -> ModelRes:
        assert len(input_data) == 1
        res = ModelRes()
        raw_content = input_data[0]
        raw_lines: Tuple[TextSlice] = split_paragraphs(
            text=raw_content, normalizer=lambda x: x, remove_empty=True
        )
        num_lines = len(raw_lines)
        if num_lines == 0:
            return res

        num_occurrences = sum([line.text.lstrip().startswith(tuple(cls.custom_config.key_list)) for line in raw_lines])
        ratio = num_occurrences / num_lines
        if ratio > 0.9:
            res.error_status = True
            res.error_type = 'QUALITY_DISUNDERSTANDABILITY'
            res.error_name = cls.__name__
            res.error_reason = "The ratio of lines start with bulletpoint is: " + str(ratio)
        return res


@Model.rule_register("QUALITY_INCOMPLETENESS", ['sft','pretrain','benchmark'])
class CommonLineEndWithEllipsis(BaseRule):
    """check whether lines end with ellipsis. """
    custom_config = DynamicRuleConfig(key_list = ["...", "…"])

    @classmethod
    def eval(cls, input_data: List[str]) -> ModelRes:
        assert len(input_data) == 1
        res = ModelRes()
        raw_content = input_data[0]
        raw_lines: Tuple[TextSlice] = split_paragraphs(
            text=raw_content, normalizer=lambda x: x, remove_empty=True
        )
        num_lines = len(raw_lines)
        if num_lines == 0:
            return res

        num_occurrences = sum([line.text.rstrip().endswith(tuple(cls.custom_config.key_list)) for line in raw_lines])
        ratio = num_occurrences / num_lines
        if ratio > 0.3:
            res.error_status = True
            res.error_type = 'QUALITY_INCOMPLETENESS'
            res.error_name = cls.__name__
            res.error_reason = "The ratio of lines end with ellipsis is: " + str(ratio)
        return res


@Model.rule_register("QUALITY_INCOMPLETENESS", ['pretrain'])
class CommonLineEndWithTerminal(BaseRule):
    """check whether lines end with terminal punctuation mark. """
    custom_config = DynamicRuleConfig(key_list = [".", "!", "?", "”", "\""])

    @classmethod
    def eval(cls, input_data: List[str]) -> ModelRes:
        assert len(input_data) == 1
        res = ModelRes()
        raw_content = input_data[0]
        raw_lines: Tuple[TextSlice] = split_paragraphs(
            text=raw_content, normalizer=lambda x: x, remove_empty=True
        )
        num_lines = len(raw_lines)
        if num_lines == 0:
            return res

        num_occurrences = sum([line.text.rstrip().endswith(tuple(cls.custom_config.key_list)) for line in raw_lines])
        ratio = num_occurrences / num_lines
        if ratio < 0.6:
            res.error_status = True
            res.error_type = 'QUALITY_INCOMPLETENESS'
            res.error_name = cls.__name__
            res.error_reason = "The ratio of lines end with terminal punctuation mark is: " + str(ratio)
        return res


@Model.rule_register("QUALITY_INEFFECTIVENESS", ['sft','pretrain','benchmark'])
class CommonLineWithJavascript(BaseRule):
    """check whether line with the word Javascript. """
    custom_config = DynamicRuleConfig()

    @classmethod
    def eval(cls, input_data: List[str]) -> ModelRes:
        assert len(input_data) == 1
        res = ModelRes()
        raw_content = input_data[0]
        normalized_lines: Tuple[TextSlice] = split_paragraphs(
            text=raw_content, normalizer=normalize, remove_empty=True
        )
        num_lines = len(normalized_lines)
        if num_lines == 0:
            return res

        num_occurrences = sum(['javascript' in line.text for line in normalized_lines])
        num_not_occur = num_lines - num_occurrences
        if num_not_occur < 3 and num_lines > 3:
            res.error_status = True
            res.error_type = 'QUALITY_INEFFECTIVENESS'
            res.error_name = cls.__name__
            res.error_reason = "The lines with the word Javascript is: " + str(num_occurrences)
        return res


if __name__ == '__main__':
    content = """
    yellowshark.com has alexa rank of #1,145,325 in the world, with roughly 630 daily unique visitors. This website has a Google PageRank of 4/10. It is a domain having .com extension and is hosted in Switzerland. yellowshark.com estimated worth is: $1,496.88 and have a daily income of around $4.16. As no active threats were reported recently, yellowshark.com is SAFE to browse.\\nTop Jobs in den Bereichen Scientific, Commercial, Technology und Construction Industry. Mit yellowshark® die nächste Anstellung finden!
    """
    tmp = CommonAlphaWords().eval([content])
    print(tmp)