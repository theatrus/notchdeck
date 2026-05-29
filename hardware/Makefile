# NotchDeck hardware — Makefile
#
# Patterned on the other BenchBits hardware projects (tsumikoro / pulsarfab):
# kicad-cli drives doc generation (schematic + PCB SVGs, 3D renders), JLCPCB BOM
# export, and the JLCPCB fab+assembly package.
#
# Targets:
#   make docs               regenerate all docs (images + BOMs) for every PCB
#   make docs-<project>     regenerate docs for one PCB (project ∈ $(PROJECTS))
#   make images-<project>   just the images (schematic SVGs + PCB SVG + 3D PNG)
#   make bom-<project>      just the JLCPCB BOM
#   make jlc                build JLCPCB fab+assembly zips for every PCB
#   make jlc-<project>      JLCPCB zip for one PCB
#   make clean-docs         remove generated images and BOMs
#   make clean-jlc          remove generated JLCPCB packages
#   make help               list available targets
#
# Adding a new project <P>:
#   1. create hardware/<P>/{<P>.kicad_pro, <P>.kicad_sch, <P>.kicad_pcb}
#   2. append <P> to PROJECTS below
#
# Requires kicad-cli (KiCad 9+/10) on PATH.

KICAD_CLI ?= kicad-cli

# Add new PCB projects here.
PROJECTS    := notchdeck-one

BOM_FIELDS  := $${ITEM_NUMBER},Reference,Value,Footprint,$${QUANTITY},LCSC,MPN,Manufacturer
BOM_LABELS  := Item,Designator,Comment,Footprint,Qty,LCSC Part \#,MPN,Manufacturer

SCRIPTS_DIR := scripts
JLC_SCRIPT  := $(SCRIPTS_DIR)/jlcpcb-package.sh

.PHONY: all docs jlc clean-docs clean-jlc help
.PHONY: $(foreach p,$(PROJECTS),docs-$(p) images-$(p) bom-$(p) jlc-$(p))

all: docs

help:
	@echo "NotchDeck hardware makefile"
	@echo ""
	@echo "Projects: $(PROJECTS)"
	@echo ""
	@echo "Available targets:"
	@echo "  docs               Generate images + BOMs for every PCB project"
	@echo "  docs-<project>     Same but only for one PCB"
	@echo "  images-<project>   Schematic/PCB images only"
	@echo "  bom-<project>      JLCPCB BOM only"
	@echo "  jlc                Build JLCPCB fab+assembly zips for every PCB"
	@echo "  jlc-<project>      JLCPCB zip for one PCB"
	@echo "  clean-docs         Remove generated docs"
	@echo "  clean-jlc          Remove generated JLCPCB packages"

docs: $(foreach p,$(PROJECTS),docs-$(p))
jlc:  $(foreach p,$(PROJECTS),jlc-$(p))

clean-docs:
	$(foreach p,$(PROJECTS), rm -rf $(p)/docs/images && rm -f $(p)/jlcpcb_bom.csv ;)

clean-jlc:
	$(foreach p,$(PROJECTS), rm -rf $(p)/jlcpcb && rm -f $(p)/*-jlcpcb.zip ;)

# --- Per-project template -----------------------------------------------------
# Expands into docs-<p>, images-<p>, bom-<p>, jlc-<p> targets.

define PROJECT_TEMPLATE

$(1)_DIR  := $(1)
$(1)_SCH  := $(1)/$(1).kicad_sch
$(1)_PCB  := $(1)/$(1).kicad_pcb
$(1)_IMG  := $(1)/docs/images
$(1)_BOM  := $(1)/jlcpcb_bom.csv

docs-$(1): images-$(1) bom-$(1)

images-$(1): $$($(1)_SCH) $$($(1)_PCB)
	@mkdir -p $$($(1)_IMG)
	@echo "[$(1)] Schematic SVGs"
	$$(KICAD_CLI) sch export svg -o $$($(1)_IMG)/ $$($(1)_SCH)
	@echo "[$(1)] PCB top SVG"
	$$(KICAD_CLI) pcb export svg -o $$($(1)_IMG)/pcb-top.svg \
	    --layers "F.Cu,F.Silkscreen,F.Mask,Edge.Cuts" \
	    --page-size-mode 2 $$($(1)_PCB)
	@echo "[$(1)] PCB bottom SVG (mirrored)"
	$$(KICAD_CLI) pcb export svg -o $$($(1)_IMG)/pcb-bottom.svg \
	    --layers "B.Cu,B.Silkscreen,B.Mask,Edge.Cuts" \
	    --mirror --page-size-mode 2 $$($(1)_PCB)
	@echo "[$(1)] 3D renders"
	$$(KICAD_CLI) pcb render --side top    --width 1600 --height 1000 \
	    -o $$($(1)_IMG)/pcb-3d-top.png    $$($(1)_PCB)
	$$(KICAD_CLI) pcb render --side bottom --width 1600 --height 1000 \
	    -o $$($(1)_IMG)/pcb-3d-bottom.png $$($(1)_PCB)

bom-$(1): $$($(1)_SCH)
	@echo "[$(1)] JLCPCB BOM"
	$$(KICAD_CLI) sch export bom \
	    --output $$($(1)_BOM) \
	    --fields '$$(BOM_FIELDS)' \
	    --labels '$$(BOM_LABELS)' \
	    --group-by 'Value,Footprint' \
	    --exclude-dnp \
	    $$($(1)_SCH)

jlc-$(1): $$(JLC_SCRIPT) $$($(1)_PCB) $$($(1)_SCH)
	@echo "[jlcpcb] building package for $(1)"
	cd $$($(1)_DIR) && KICAD_CLI=$$(KICAD_CLI) ../$$(JLC_SCRIPT) \
	    $(1).kicad_pcb $(1).kicad_sch

endef

$(foreach p,$(PROJECTS),$(eval $(call PROJECT_TEMPLATE,$(p))))
