# Test files for programs

This folder contains test data for the programs in the ``twolalign`` package.  Most tests can be performed through a ``make`` command which uses the ``Makefile`` present in this directory.

## DEMO

This is a very small example of transforming a table of Finnish words into a morphophonemic representation for which one can then author two-level rules.  The files are in the Comma Separated Values (CSV) format which one can create and view using a spreadsheet program and store from there in this format.

1. ``demo-table.csv`` is the table of a few words in selected inflectional forms.  Each line in the table represents one lexeme and each column an inflectional form. The first column is the label used when identifying the lexeme. The endings in the inflected forms are separated from the stem by a period.  Note that there may be several endings or no edings at all in the word forms, but in each column the number must be the same.  The top labels represent the names of the underlying morphemes for the stem (``STM``) or the endings (e.g. ``INE``).

2. ``demo-affixes.csv`` is a small file which determines two things:

    a. Firstly, it tells which columns (or forms) are actually taken for the process.  Often the table contains more forms than we actually need.  The initial four lines in the CSV table identify each one column in ``demo-table.csv``.  Such lines contain a ``+`` sign in the second column.
    b. Secondly, the table gives the morphophonemic forms of the inflectional morphemes present in the selected columns.  E.g. the plural might occur in several columns.  The morphophonemes are enclosed in braces (e.g. ``{aä}``).  The program could align the endings but that is done manually this way because of practical reasons.

This small table is needed for the producing the raw morphophonemic representations for the word forms in the original table.



## KSK-NOUNS and KSK-VERBS

These two are full-scale inflectional paradigms of Finnish nouns and verbs.  The describe the stem internal and stem final phonemic alternations in a comprehensive manner.  The tables of inflectional forms can be transformed into a set of example words in a format required by the Python implementation of the two-level rule compiler.