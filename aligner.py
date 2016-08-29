import sys, io, fileinput
import libhfst
tok = libhfst.HfstTokenizer()
algfile = libhfst.HfstInputStream("chardist.fst")
align = algfile.read()

for line in sys.stdin:
    (f1,f2) = line.strip().split(sep=":")

    w1 = libhfst.fst(f1)
    w1.insert_freely(("Ø","Ø"))
    w1.minimize()
#    print(w1)

    w2 = libhfst.fst(f2)
    w2.insert_freely(("Ø","Ø"))
    w2.minimize()
#    print(w2)

    w3 = libhfst.HfstTransducer(w1)
    w3.compose(align)
    w3.compose(w2)
#    print(w1)

    w3.n_best(1)
    w3.minimize()
    
    paths = w3.extract_paths(output='text')
    print(paths.strip())


