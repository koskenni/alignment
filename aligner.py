import sys, hfst
algfile = hfst.HfstInputStream("chardist.fst")
align = algfile.read()

for line in sys.stdin:
    lst =  line.strip().split(sep=":")
    if len(lst) == 2:
        f1,f2 = lst
    else: f1,f2 = lst[0],lst[0]

    w1 = hfst.fst(f1)
    w1.insert_freely(("Ø","Ø"))
    w1.minimize()
#    print(w1)

    w2 = hfst.fst(f2)
    w2.insert_freely(("Ø","Ø"))
    w2.minimize()
#    print(w2)

    w3 = hfst.HfstTransducer(w1)
    w3.compose(align)
    w3.compose(w2)
#    print(w1)

    w3.n_best(1)
    w3.minimize()
    
    paths = w3.extract_paths(output='text')
    print(paths.strip())


