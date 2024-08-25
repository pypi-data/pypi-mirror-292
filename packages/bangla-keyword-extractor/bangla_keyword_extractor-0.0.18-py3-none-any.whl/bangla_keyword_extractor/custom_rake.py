from rake_nltk import Rake

class BanglaRake(Rake):
    def _tokenize_text_to_sentences(self, text):
        text = text.replace('\n', ' ')
        tokens = []
        s = ""
        bangla_fullstop = '0964'
        for c in text:
            g = c.encode("unicode_escape")
            g = g.upper()
            g = g[2:]
            g = g.decode('utf-8')
            if g == bangla_fullstop:
                tokens.append(s)
                s = ""
                continue
            s += c
        if len(s) > 0:
            tokens.append(s)
        return tokens
    def _tokenize_sentence_to_words(self, sentence):
        tokens = sentence.split()
        return tokens