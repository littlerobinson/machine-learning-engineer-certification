import re
import string
import unicodedata
import contractions


class TextProcessing:
    """
    The TextProcessing class is designed to provide various text processing methods.
    It includes functionalities to clean, standardize, and transform text to prepare it
    for further analysis, such as natural language processing (NLP).
    """

    emojis = {':)': 'smile', ':-)': 'smile', ';d': 'wink', ':-E': 'vampire', ':(': 'sad',
          ':-(': 'sad', ':-<': 'sad', ':P': 'raspberry', ':O': 'surprised',
          ':-@': 'shocked', ':@': 'shocked',':-$': 'confused', ':\\': 'annoyed',
          ':#': 'mute', ':X': 'mute', ':^)': 'smile', ':-&': 'confused', '$_$': 'greedy',
          '@@': 'eyeroll', ':-!': 'confused', ':-D': 'smile', ':-0': 'yell', 'O.o': 'confused',
          '<(-_-)>': 'robot', 'd[-_-]b': 'dj', ":'-)": 'sadsmile', ';)': 'wink',
          ';-)': 'wink', 'O:-)': 'angel','O*-)': 'angel','(:-D': 'gossip', '=^.^=': 'cat'}

    def standardize(self, input_text):
        """
        This method takes raw text as input and applies a series of transformations to standardize it.
        The standardize steps include:
        1. Converting all characters to lowercase.
        2. Removing all occurrences of HTML tags'.
        3. Removing mentions (@) and hashtags (#).
        4. Removing punctuation.
        """
        # Transform all characters to lowercase
        sanitize_text = self.to_lowercase(input_text)

        # Remove all occurrences of the string '<br />'
        sanitize_text = self.strip_html(sanitize_text)
        
        # Replace emojis
        sanitize_text = self.standardize_emojis(sanitize_text)

        # Remove mentions (@) and hashtags (#)
        sanitize_text = self.remove_mentions_and_tags(sanitize_text)

        # Remove punctuation
        sanitize_text = self.remove_punctuation(sanitize_text)


        return sanitize_text

    def to_lowercase(self, text):
        """
        This function takes a text as input and returns the text with all characters converted to lowercase.
        """
        return text.lower()

    def standardize_accented_chars(self, text):
        """
        This function takes a text as input and returns the text with accented characters standardized.
        """
        return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')

    def strip_html(self, text):
        """
        This function takes a text as input and returns the text with all HTML tags removed.
        """
        return re.sub(r'<[^>]*>', '', text)

    def remove_url(self, text):
        """
        This function takes a text as input and returns the text with all URLs removed.
        """
        return re.sub(r'https?:\S*', '', text)

    def remove_mentions_and_tags(self, text):
        """
        This function takes a text as input and returns the text with all mentions (@) and hashtags (#) removed.
        """
        text = re.sub(r'@\S*', '', text)
        return re.sub(r'#\S*', '', text)

    def remove_special_characters(self, text):
        """
        This function takes a text as input and returns the text with all special characters removed.
        """
        pat = r'[^a-zA-z0-9.,!?/:;\"\'\s]'
        return re.sub(pat, '', text)

    def remove_numbers(self, text):
        """
        This function takes a text as input and returns the text with all numbers removed.
        """
        pattern = r'[^a-zA-z.,!?/:;\"\'\s]'
        return re.sub(pattern, '', text)

    def remove_punctuation(self, text):
        """
        This function takes a text as input and returns the text with all punctuation removed.
        """
        return ''.join([c for c in text if c not in string.punctuation])

    def expand_contractions(self, text):
        """
        This function takes a text as input and returns the text with all contractions expanded.
        """
        expanded_words = []
        for word in text.split():
            expanded_words.append(contractions.fix(word))
        return ' '.join(expanded_words)
    
    def standardize_emojis(self, text):
        """
        This function replace emojis with textual emojis. :) --> EMOJIsmile
        """
        for emoji in self.emojis.keys():
            text = text.replace(emoji, "EMOJI" + self.emojis[emoji])
        return text

    def lemmatize(self, text, nlp):
        """
        This function takes a text and a language processing object (nlp) as input and returns the text with all words lemmatized.
        """
        doc = nlp(text)
        lemmatized_text = []
        for token in doc:
            lemmatized_text.append(token.lemma_)
        return ' '.join(lemmatized_text)
