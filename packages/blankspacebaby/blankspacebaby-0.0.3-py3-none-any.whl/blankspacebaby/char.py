
class Char:
    def __init__(self, character):
        if not isinstance(character, str) or len(character) != 1:
            raise ValueError("Input must be a single character string.")
        self.character = character
        self.language = self.detect_language()

    def is_ascii(self):
        return ord(self.character) < 128

    def detect_language(self):
        ascii_value = ord(self.character)

        # Check for punctuation
        if 33 <= ascii_value <= 47 or \
           58 <= ascii_value <= 64 or \
           91 <= ascii_value <= 96 or \
           123 <= ascii_value <= 126:
            return "English Punctuation"
        
        if self.character in "，。；：、‘’“”「」『』？！—（）【】｛｝《》…～＋＝＿＠＃＄％＾＆＊．":
            return "Chinese Punctuation"
        
        if ascii_value < 32:
            return "Control Character"
        
        if ascii_value == 32:
            return "Space"

        # Check for standard ASCII characters
        if 33 <= ascii_value <= 127:
            return "English"

        # Characters outside the above ranges
        return "Non-English"

    def __repr__(self):
        return self.character

    def __str__(self):
        return self.character
    
en_zh_punctuation = {"(": "（", ")": "）", "[": "【", "]": "】", "{": "｛", "}": "｝"}    
zh_en_punctuation = {zh_punc : en_punc for en_punc, zh_punc in en_zh_punctuation.items()}
    
en_zh_punctuation_full = {"(": "（", ")": "）", "[": "【", "]": "】", "{": "｛", "}": "｝", "<": "《", ">": "》", "+": "＋", "=": "＝", "_": "＿", "@": "＠", "#": "＃", "$": "＄", "%": "％", "^": "＾", "&": "＆", "*": "＊", ".": "．"}
zh_en_punctuation_full = {zh_punc : en_punc for en_punc, zh_punc in en_zh_punctuation_full.items()}