"""
Jumanを継承して無理やり引用句の問題を解決したJuman2のコード
"""

import six
import re
from pyknp import Juman
from pyknp import JUMAN_FORMAT
from pyknp import MList
from pyknp import Morpheme

class Morpheme2(Morpheme):
    def _parse_spec(self, spec):
        parts = []
        part = ''
        inside_quotes = False
        if spec.startswith(' '):
            spec = '\\%s' % spec
        if(spec.startswith('\  \  \  特殊 1 空白 6 * 0 * 0')):
            parts = ['\ ','\ ','\ ','特殊','1','空白','6','*','0','*','0','NIL']
        else:
            for char in spec:
                if char == '"':
                    if not inside_quotes:
                        inside_quotes = True
                    else:
                        inside_quotes = False
                # If "\"" proceeds " ", it would be not inside_quotes, but "\"".
                #if inside_quotes and char == ' ' and part == '"':
                if inside_quotes and char == ' ' and part[-1] == '"':
                    inside_quotes = False
                if part != "" and char == ' ' and not inside_quotes:
                    #if part.startswith('"') and part.endswith('"') and len(part) > 1:
                    if part.startswith('"') and part.endswith('"') and len(part) > 1 and len(parts) > 2:
                        parts.append(part[1:-1])
                    else:
                        parts.append(part)
                    part = ''
                else:
                    part += char
            parts.append(part)

        try: # FIXME KNPの場合と同様、EOSをきちんと判定する
            self.midasi = parts[0]
            self.yomi = parts[1]
            self.genkei = parts[2]
            self.hinsi = parts[3]
            self.hinsi_id = int(parts[4])
            self.bunrui = parts[5]
            self.bunrui_id = int(parts[6])
            self.katuyou1 = parts[7]
            self.katuyou1_id = int(parts[8])
            self.katuyou2 = parts[9]
            self.katuyou2_id = int(parts[10])
            self.imis = parts[11].lstrip("\"").rstrip("\"")
            self.fstring = parts[12]
        except IndexError:
            pass
        # Extract 代表表記
        match = re.search(r"代表表記:([^\"\s]+)", self.imis)
        if match:
            self.repname = match.group(1)

class MList2(MList):
    def __init__(self, spec="", juman_format=JUMAN_FORMAT.DEFAULT):
        self._mrph = []
        self._readonly = False
        self.comment = ""
        mid = 1
        if spec != "":
            for line in spec.split("\n"):
                if line.strip() == "":
                    continue
                elif line.startswith('#'):
                    self.comment += line
                elif line.startswith('@') and not line.startswith('@ @'):
                    self._mrph[-1].push_doukei(Morpheme(line[2:], mid, juman_format))
                    mid += 1
                else:
                    mrph = Morpheme2(line, mid, juman_format)
                    if juman_format == JUMAN_FORMAT.LATTICE_TOP_ONE:
                        if 1 not in mrph.ranks:
                            continue
                        elif self._mrph and self._mrph[-1].mrph_id == mrph.mrph_id:
                            self._mrph[-1].push_doukei(mrph)
                            continue
                    self.push_mrph(mrph)
                    mid += 1

class Juman2(Juman):
    def juman(self, input_str, juman_format=JUMAN_FORMAT.DEFAULT):
        """ analysis関数と同じ """
        assert(isinstance(input_str, six.text_type))
        result = MList2(self.juman_lines(input_str), juman_format)
        return result

if __name__ == "__main__":
    t = Juman2(jumanpp=False)
    text = "彼は\"Hello!\"と言った。"
    print("Input : {}".format(text))
    tokens = [token.midasi for token in t.analysis(text).mrph_list()]
print("Tokenized : {}".format(tokens))
