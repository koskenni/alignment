import re, sys, hfst

vowel_features = {
    'i':('Close','Front','Unrounded'),
    'j':('Semivowel','Front','Unrounded'),
    'y':('Close','Front','Rounded'),
    'ü':('Close','Front','Rounded'), ##
    'u':('Close','Back','Rounded'),
    'e':('Mid','Front','Unrounded'),
    'ö':('Mid','Front','Rounded'),
    'o':('Mid','Back','Rounded'),
    'õ':('Mid','Back','Unrounded'),
    'ä':('Open','Front','Unrounded'),
    'a':('Open','Back','Unrounded'),
    'Ø':('Zero', 'Zero', 'Zero')
    }

cmo = {'Semivowel':0.0, 'Close':1.0, 'Mid':2.0, 'Open':3.0}
fb = {'Front':1, 'Back':2}
ur = {'Unrounded':1, 'Rounded':2}
vowels = set(vowel_features.keys())

semivowels = set('j')
semivowel_vowels = {'j': frozenset(['i', 'j', 'Ø'])}

def vowel_set_weight(subset):
    w = len(subset)
    svs = subset.intersection(semivowels)
    if svs:
        for sv in svs:
            if not subset <= semivowel_vowels[sv]:
                w += 10
    if ('Ø' in subset): w -= 0.6
    return float(w)

consonant_features = {
    'm':('Bilab','Voiced','Nasal'),
    'p':('Bilab','Unvoiced','Stop'),
    'b':('Bilab','Voiced','Stop'),
    'v':('Labdent','Voiced','Fricative'),
    'f':('Labdent','Unvoiced','Fricative'),
    'w':('Labdent','Voiced','Fricative'),
    'n':('Alveolar','Voiced','Nasal'),
    't':('Alveolar','Unvoiced','Stop'),
    'z':('Alveolar','Unvoiced','Stop'), ##
    'd':('Alveolar','Voiced','Stop'),
    's':('Alveolar','Unvoiced','Sibilant'),
    'š':('Alveolar','Unvoiced','Sibilant'),
    'ž':('Alveolar','Voiced','Sibilant'),
    'l':('Alveolar','Voiced','Lateral'),
    'r':('Alveolar','Voiced','Tremulant'),
    'j':('Palatal','Voiced','Approximant'),
    'k':('Velar','Unvoiced','Stop'),
    'c':('Velar','Unvoiced','Stop'), ##
    'x':('Velar','Unvoiced','Stop'), ##
    'g':('Velar','Voiced','Stop'),
    'h':('Glottal','Unvoiced','Fricative'),
    'Ø':('Zero', 'Zero', 'Zero')
}

pos = {'Bilab':0.0, 'Labdent':1.0, 'Alveolar':2.0, 'Palatal':3.0, 'Velar':3.0, 'Glottal':4.0}
voic = {'Unvoiced':1, 'Voiced':2}
consonants = set(consonant_features.keys())

def cons_set_weight(subset):
    w = 0.0
    pmin, pmax = 100.0, 0.0
    vmin, vmax = 100.0, 0.0
    mm= set()
    for x in subset:
        if x == 'Ø':
            w += 2.6
        else:
            p, v, m = consonant_features[x]
            pval = pos[p]
            pmin = min(pval, pmin)
            pmax = max(pval, pmax)
            vval = voic[v]
            vmin = min(vval, vmin)
            vmax = max(vval, vmax)
            mm.add(m)
    w += (len(mm) - 1.0)
    w += (pmax - pmin)*0.5
    w += vmax - vmin
    # print(subset, w, pmin, pmax, vmin, vmax, mm) ###
    return w

mphon_separator = ''
weight_cache = {}

def mphon_weight(mphon):
    global  vowels, consonants, mphon_separator, weight_cache
    if mphon in weight_cache:
        return weight_cache[mphon]
    if mphon_separator == '':
        phon_list = list(mphon)
    else: phon_list = mphon.split(mphon_separator)
    phon_set = set(phon_list)
    if len(phon_set) == 1 and 'Ø' in phon_set:
        weight = 1000.0
    elif phon_set <= consonants:
        # return float(len(phon_set))
        weight = cons_set_weight(phon_set)
    elif phon_set <= vowels:
        # return float(len(phon_set))
        weight = vowel_set_weight(phon_set)
    else:
        weight = float('Infinity')
    weight_cache[mphon] = weight
    return weight

def fst_to_fsa(FST):
    global mphon_separator
    FB = hfst.HfstBasicTransducer(FST)
    sym_pairs = FB.get_transition_pairs()
    dict = {}
    for sym_pair in sym_pairs:
        in_sym, out_sym = sym_pair
        joint_sym = in_sym + mphon_separator + out_sym
        dict[sym_pair] = (joint_sym, joint_sym)
    FB.substitute(dict)
    RES = hfst.HfstTransducer(FB)
    return RES

def remove_bad_transitions(FST, weighting, max_weight_allowed):
    BF = hfst.HfstBasicTransducer(FST)
    for state in BF.states():
        for arc in BF.transitions(state):
            in_syms = arc.get_input_symbol()
            w = weighting(in_syms)
            if w > max_weight_allowed:
                BF.remove_transition(state, arc)
    RES = hfst.HfstTransducer(BF)
    return RES

def shuffle_with_zeros(string, target_length):
    S = hfst.fst(string)
    l = len(string)
    if l < target_length:
        n = target_length - l
        Z = hfst.regex(' '.join(n * 'Ø'))
        S.shuffle(Z)
    S.minimize()
    S.set_name(string)
    return S

def set_weights(FST, weighting):
    B = hfst.HfstBasicTransducer(FST)
    for state in B.states():
        for arc in B.transitions(state):
            tostate = arc.get_target_state()
            insym = arc.get_input_symbol()
            outsym = arc.get_output_symbol()
            w = weighting(insym)
            B.remove_transition(state, arc)
            B.add_transition(state, tostate, insym, outsym, w)
    RES = hfst.HfstTransducer(B)
    # print("set_weights:\n", RES) ##
    return RES

def multialign(strings, target_length, weighting):
    s1 = strings[0]
    R = shuffle_with_zeros(s1, target_length)
    for string in strings[1:]:
        S = shuffle_with_zeros(string, target_length)
        R.cross_product(S)
        T = fst_to_fsa(R)
        R = remove_bad_transitions(T, weighting, 1000000.0)
        R.minimize()
    RES = set_weights(R, weighting)
    # print("multialign:\n", RES) ##
    return RES

def print_alignment(lst):
    l = len(lst[0])
    for i in range(l):
        syms = [itm[i:i+1] for itm in lst]
        print(''.join(syms))
    print()
    return

if __name__ == "__main__":
    for line in sys.stdin:
        words = line.strip().split(sep=' ')
        ml = max([len(x) for x in words])
        RES = hfst.empty_fst()
        notyetfound = True
        for m in range(ml,ml+5):
            R = multialign(words, m, mphon_weight)
            if R.compare(hfst.empty_fst()):
                continue
            RES.disjunct(R)
            RES.n_best(10)
            RES.minimize()
            if notyetfound:
                notyetfound = False
            else:
                break

        RES.n_best(10)
        RES.minimize()
        paths = RES.extract_paths(output='raw')
        for w, path in paths:
            lst = [isym for isym,outsym in path]
            # print([(x, mphon_weight(x)) for x in lst], w) ##
        if len(paths) < 1:
            print("***", line, "***", paths)
            continue
        best_w = paths[0][0]
        zb = -1
        for w, path in paths:
            if w > best_w: break
            lst = [isym for isym,outsym in path]
            z = 0
            i = 0
            for isym in lst:
                z = z + i * isym.count('Ø')
                i = i + 1
            # print('  '.join(lst), w, z) ##
            if z > zb:
                zb = z
                best = lst
        best2 = [re.sub(r'^([a-zšžüõåäö])\1\1*$', r'\1', cc) for cc in best]
        # best2 = [re.sub(r'^([a-zšžüõåäöØ])([a-zšžüõåäöØ])$', r'\1:\2', cc) for cc in best]
        # print(' '.join(best2), best_w, zb)
        # print(' '.join(best2))
        print_alignment(best)
        # print('  '.join(best2), zb)
    
