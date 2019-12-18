import sys
import re

features_of_phoneme = {}
feature_set = set()
input_phonemes = set()
output_phonemes = set()
within_set_lst = []
forall_lst = []

pair_weight_dict = {}

def deduce_weights():
    for insym in sorted(input_phonemes):
        insym_feat_set = features_of_phoneme[insym]
        for outsym in sorted(output_phonemes):
            outsym_feat_set = features_of_phoneme[outsym]
            if (insym_feat_set <= outsym_feat_set) or \
               (insym_feat_set >= outsym_feat_set):
                weight_lst = [(0, frozenset(), 0)]
            else:
                weight_lst = []
                #print("within_set_lst:", within_set_lst) ###
                for within_set, w, i in within_set_lst:
                    infea = insym_feat_set & within_set
                    outfea = outsym_feat_set & within_set
                    fea = frozenset(infea | outfea)
                    if infea and outfea:
                        if len(fea) > max(len(infea), len(outfea)):
                            weight_lst.append((w, fea, i))
            if weight_lst:
                wdict = {}
                for w, s, i in weight_lst:
                    if not s in wdict:
                        wdict[s] = w
                    else:
                        wdict[s] = min(wdict[s], w)
                sum = 0
                for s, w in wdict.items():
                    sum += w
                #print(insym, outsym, sum, wdict) ###
                pair_weight_dict[(insym, outsym)] = sum
    return

def read_alphabet(file_name):
    from collections import deque
    af = open(file_name, "r")
    line_lst = deque([])
    for line_nl in af:
        if line_nl.strip().startswith("#"):
            continue            # skip comments
        line = line_nl.strip().split("#")[0].strip()
        if line:
            line_lst.append(line) # skip empty lines
    keywords = {"ALPHABET", "WITHIN", "FOR ALL", "EXCEPTIONS", "END"}
    line = line_lst.popleft()
    while line_lst:
        if line == "ALPHABET":
            line = line_lst.popleft()
            while line not in keywords and line_lst:
                sym, equal, feat_str = line.partition("=")
                sym = sym.strip()
                if len(sym) == 2:
                    if sym.startswith(":"):
                        sym = sym[1:]
                        output_phonemes.add(sym)
                    elif sym.endswith(":"):
                        sym = sym[:-1]
                        input_phonemes.add(sym)
                elif len(sym) == 1:
                    input_phonemes.add(sym)
                    output_phonemes.add(sym)
                else:
                    print(line)
                    sys.exit("*** THE LEFT HAND PART NOT ONE CHAR LONG")
                if equal == "=":
                    lst = feat_str.split()
                    for feat in lst:
                        feature_set.add(feat)
                    feat_set = set(lst)
                    features_of_phoneme[sym] = feat_set
                    line = line_lst.popleft()
                else:
                    sys.exit("*** NO = ON LINE: " + line)
            #print(features_of_phoneme) ###
            #print("input_phonemes:", sorted(input_phonemes)) ###
            #print("output_phonemes:", sorted(output_phonemes)) ###
        elif line == "WITHIN":
            line = line_lst.popleft()
            i = 0
            while line not in keywords and line_lst:
                feat_str, equal, weight = line.partition("=")
                if not equal:
                    sys.exit("*** NO = ON LINE:", line)
                w = int(weight.strip())
                feat_lst = feat_str.strip().split()
                for feat in feat_lst:
                    if feat not in feature_set:
                        sys.exit("FEATURE '" + feat + "' NOT DEFINED: " + line)
                i += 1
                within_set_lst.append((frozenset(feat_lst), w, i))
                line = line_lst.popleft()
            #print("within_set_lst:", within_set_lst) ###
            deduce_weights()
        elif line == "FOR ALL":
            all_var = "X"
            line = line_lst.popleft()
            while line not in keywords and line_lst:
                sym_pair_str, equal, w = line.partition("=")
                sym_pair_lst = sym_pair_str.strip().split()
                w1 = int(w)
                if not "X" in line or not w:
                    sys.exit("*** X MISSING: " + line)
                s = set()
                for (insym, outsym), w2 in pair_weight_dict.items():
                    new_lst = []
                    for sym_pair in sym_pair_lst:
                        pre, x, post = sym_pair.partition("X")
                        #print(pre, x, post) ###
                        if not pre and x and not post:
                            if insym == outsym:
                                new_lst.append(insym)
                        elif not x:
                            new_lst.append(sym_pair)
                        elif pre == ":":
                            new_lst.append(insym + ":" + outsym)
                        elif pre.endswith(":"):
                            new_lst.append(pre + outsym)
                        elif post == ":":
                            new_lst.append(insym + ":" + outsym )
                        elif post.startswith(":"):
                            new_lst.append(insym + post)
                        else:
                            sys.exit("*** INCORRECT " + sym_pair + " IN FOR ALL LINE:\n" + line)
                    ww = w1 if len(sym_pair_lst) <= 1 else w1 + w2
                    symstr = " ".join(new_lst) + "::" + str(ww)
                    s.add(symstr)
                    #print(symstr) ###
                for symstr in s:
                    forall_lst.append(symstr)
                line = line_lst.popleft()
        elif line == "EXCEPTIONS":
            line = line_lst.popleft()
            while line not in keywords and line_lst:
                strg, equal, w = line.partition("=")
                lin = re.sub(r" *= *", "::", line)
                forall_lst.append(lin)
                line = line_lst.popleft()

    return

def main():
    import argparse
    arpar = argparse.ArgumentParser(
        description="Builds a distance metric FST")
    arpar.add_argument(
        "alphabet",
        help="An alphabet definition with features and similarity sets")
    arpar.add_argument(
        "metrics",
        help="FST which contains weights for preferring alternative alignments")
    arpar.add_argument(
        "-d", "--delimiter",
        help="Delimiter between the two words to be aligned",
        default=":")
    args = arpar.parse_args()

    read_alphabet(args.alphabet)
    pair_weight_lst = []
    for insym, outsym in pair_weight_dict.keys():
        w = pair_weight_dict[(insym, outsym)]
        pair_weight_lst.append("{}:{}::{}".format(insym, outsym, w))
    pair_weight_str = "|".join(pair_weight_lst)
    #print(pair_weight_str) ###
    forall_str = "|".join(forall_lst)
    #print(forall_str) ###

    import hfst
    fst = hfst.regex(pair_weight_str + "|" + forall_str)
    fst.repeat_star()
    fst.minimize()
    fstfile = hfst.HfstOutputStream(filename=args.metrics)
    fstfile.write(fst)
    fstfile.flush()
    fstfile.close()
    return

if __name__ == "__main__":
    main()
