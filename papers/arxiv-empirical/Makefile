.PHONY: all figures clean

ROOT_DIR := ../..
FIG_DIR := ../shared/figures
FIG_SENTINEL := $(FIG_DIR)/fig_sandbox_builds.pdf

all: main.pdf

$(FIG_SENTINEL):
	cd $(ROOT_DIR) && uv run python -m src.generate_figures

figures:
	cd $(ROOT_DIR) && uv run python -m src.generate_figures

main.pdf: main.tex ../shared/references.bib $(FIG_SENTINEL)
	latexmk -pdf -interaction=nonstopmode main.tex

clean:
	latexmk -C
