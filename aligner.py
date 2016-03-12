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

    w2 = libhfst.fst(f2)
    w2.insert_freely(("Ø","Ø"))
    w2.minimize()

    w1.compose(align)
    w1.compose(w2)

    res = w1.n_best(1).minimize()
    
    paths = res.extract_paths(output='text')
    print(paths.strip())


