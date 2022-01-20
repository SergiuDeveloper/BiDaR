import spacy

from spacy.language import Language
from spacy_langdetect import LanguageDetector


class TextProcessor:
    __SPACY_LANGUAGE_MAP = {
        'ca': 'ca_core_news_sm',
        'zh': 'zh_core_web_sm',
        'da': 'da_core_news_sm',
        'nl': 'nl_core_news_sm',
        'en': 'en_core_web_sm',
        'fr': 'fr_core_news_sm',
        'de': 'de_core_news_sm',
        'el': 'el_core_news_sm',
        'it': 'it_core_news_sm',
        'ja': 'ja_core_news_sm',
        'lt': 'lt_core_news_sm',
        'mk': 'mk_core_news_sm',
        'nb': 'nb_core_news_sm',
        'pl': 'pl_core_news_sm',
        'pt': 'pt_core_news_sm',
        'ro': 'ro_core_news_sm',
        'ru': 'ru_core_news_sm',
        'es': 'es_core_news_sm'
    }

    @staticmethod
    def extract_nouns(text):
        language = TextProcessor.__SPACY_LANGUAGE_MAP.get(
            TextProcessor.detect_language(text),
            TextProcessor.__SPACY_LANGUAGE_MAP.get('en')
        )
        nlp = spacy.load(language)
        
        doc = nlp(text)
        nouns = [word.lemma_ for word in doc if word.pos_ in ['NOUN', 'PROPN']]

        return nouns

    @staticmethod
    def detect_language(text, nlp=None):
        if nlp is None:
            nlp = spacy.load('en_core_web_sm')
            Language.factory('language_detector', func=TextProcessor.language_detector)
            nlp.add_pipe('language_detector', last=True)

        doc = nlp(text)

        return doc._.language['language']

    @staticmethod
    def detect_languages(texts, nlp=None):
        if nlp is None:
            nlp = spacy.load('en_core_web_sm')
            Language.factory('language_detector', func=TextProcessor.language_detector)
            nlp.add_pipe('language_detector', last=True)

        docs = list(nlp.pipe(texts))

        return [doc._.language['language'] for doc in docs]

    @staticmethod
    @Language.factory('language_detector')
    def language_detector(nlp, name):
        return LanguageDetector()
