TEXFILE = bellDatabase
LATEX = xelatex
BIBTEX = bibtex

all: $(TEXFILE).pdf

$(TEXFILE).pdf: $(TEXFILE).tex references.bib
	$(LATEX) $(TEXFILE).tex
	$(BIBTEX) $(TEXFILE)
	$(LATEX) $(TEXFILE).tex
	$(LATEX) $(TEXFILE).tex

clean:
	rm -f *.aux *.log *.out *.pdf *.toc *.bbl *.blg *.bcf *.run.xml

.PHONY: all clean