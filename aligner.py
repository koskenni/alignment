# aligner.py

def main():
    import argparse
    arpar = argparse.ArgumentParser(
        description="Run-time aligner of words")
    arpar.add_argument(
        "metrics",
        help="FST which contains weights for preferring alternative alignments")
    arpar.add_argument(
        "-d", "--delimiter",
        help="Delimiter between the two words to be aligned",
        default=":")
    arpar.add_argument(
        "-l", "--layout",
        choices=["vertical","list","horizontal"],
        help="output layout",
        default="vertical")
    arpar.add_argument(
        "-n", "--number",
        help="number of results to be printed",
        type=int, default=1)
    arpar.add_argument(
        "-w", "--weights",
        help="print also the weight of each alignment",
        action="store_true")

    args = arpar.parse_args()

    import hfst
    algfile = hfst.HfstInputStream(args.metrics)
    align = algfile.read()

    separator = args.delimiter
    import sys
    for line in sys.stdin:
        lst =  line.strip().split(sep=separator)
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

        w3.n_best(args.number)
        w3.minimize()

    #    print(w3)

        paths_str = w3.extract_paths(output='text')
        paths_lst = paths_str.split(sep="\n")
        # print(paths_lst) ###
        for path in paths_lst:
            if not path:
                continue
            pair, tab, weight = path.partition("\t")
            inword, colon, outword = pair.partition(":")
            if not colon:
                outword = inword
            if args.weights:
                weight = "\t" + weight
            else:
                weight = ""
            if args.layout == "list":
                print(inword + "\t" + outword + weight)
            elif args.layout == "vertical":
                print(inword )
                print(outword)
                print(weight)
            else:                       # horizontal
                lst = []
                for inch, outch in zip(inword, outword):
                    if inch == outch:
                        pair = inch
                    else:
                        pair = inch + outch
                    lst.append(pair)
                print(" ".join(lst) + weight)

    return

if __name__ == "__main__":
    main()
