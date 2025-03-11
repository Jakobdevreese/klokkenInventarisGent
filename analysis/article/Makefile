TEXFILE = bellDatabase
LATEX = xelatex

all: $(TEXFILE).pdf

$(TEXFILE).pdf: $(TEXFILE).tex
		$(LATEX) $(TEXFILE).tex
		$(LATEX) $(TEXFILE).tex

clean:
		rm -f *.aux *.log *.out *.pdf *.toc

.PHONY: all clean