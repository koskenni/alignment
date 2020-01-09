BASE=demo
DELIM=,
.SUFFIXES:

.PHONY : renamed raw zerofilled words features listraw clean

renamed : $(BASE)-renamed.pstr

raw : $(BASE)-raw.csv

zerofilled : $(BASE)-zerofilled.csv

words : $(BASE)-words.csv

features : $(BASE)-features.text

listraw : $(BASE)-listraw.text

clean :
	rm -f $(BASE)-renamed.pstr $(BASE)-raw.csv $(BASE)-zerofilled.csv $(BASE)-words.csv
	rm -f $(BASE)-features.text $(BASE)-listraw.text

$(BASE)-renamed.pstr : $(BASE)-raw.csv $(BASE)-newnames.csv
	twol-raw2named $< $@ $(BASE)-newnames.csv

$(BASE)-raw.csv : $(BASE)-zerofilled.csv $(BASE)-affixes.csv
	twol-zerofilled2raw -d '$(DELIM)' $< $@ $(BASE)-affixes.csv

$(BASE)-zerofilled.csv : $(BASE)-words.csv
	twol-words2zerofilled -d '$(DELIM)' $< $@

$(BASE)-words.csv : $(BASE)-table.csv
	twol-table2words -d '$(DELIM)' -s "."  $< $@

$(BASE)-features.text : $(BASE)-raw.csv
	cat $< | cut -d ',' -f 1 | cut -d ' ' -s -f 2,3 | tr ' ' '\n' | sort | uniq > $@

$(BASE)-listraw.text : $(BASE)-raw.csv
	cat $< | cut -d ',' -f 4 | tr ' ' '\n' | sort | egrep '^\{.+\}' | uniq > $@

$(BASE)-examples.fst : $(BASE)-renamed.pstr
	twol-twexamp $< $@
