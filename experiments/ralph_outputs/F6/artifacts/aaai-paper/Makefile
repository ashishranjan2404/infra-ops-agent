# AAAI-2026 paper build. Requires a TeX distribution (TeX Live / MacTeX).
MAIN = main

.PHONY: all clean parse-check

all: $(MAIN).pdf

$(MAIN).pdf: $(MAIN).tex sections/*.tex references.bib
	pdflatex -interaction=nonstopmode $(MAIN)
	-bibtex $(MAIN)
	pdflatex -interaction=nonstopmode $(MAIN)
	pdflatex -interaction=nonstopmode $(MAIN)

# Structural validation without a TeX toolchain.
parse-check:
	python3 check_balance.py

clean:
	rm -f $(MAIN).pdf $(MAIN).aux $(MAIN).log $(MAIN).bbl $(MAIN).blg $(MAIN).out
