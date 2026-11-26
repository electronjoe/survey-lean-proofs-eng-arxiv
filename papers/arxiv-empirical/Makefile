.PHONY: all figures clean

ROOT_DIR := ../..
FIG_DIR := ../shared/figures
FIG_SENTINEL := $(FIG_DIR)/fig_eligibility_adjusted_adoption.pdf
FIG_DEPS := $(ROOT_DIR)/artifacts/unified_15cat_panel.json $(ROOT_DIR)/artifacts/lean_eligibility_t2.json $(ROOT_DIR)/src/generate_figures.py

all: main.pdf

$(FIG_SENTINEL): $(FIG_DEPS)
	cd $(ROOT_DIR) && uv run python -m src.generate_figures

figures:
	cd $(ROOT_DIR) && uv run python -m src.generate_figures

main.pdf: main.tex ../shared/references.bib $(FIG_SENTINEL)
	latexmk -pdf -interaction=nonstopmode main.tex

clean:
	latexmk -C
