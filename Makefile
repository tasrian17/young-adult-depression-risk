# One command to run everything: `make all`.
# Targets are added as checkpoints add pipeline steps.

PYTHON ?= python3
MANIFEST := data/nhanes_manifest.csv
FETCH_FLAGS := $(if $(ACCEPT_REVISIONS),--accept-revisions,)

.PHONY: all data manifest fetch verify test install

all: data test

install:
	$(PYTHON) -m pip install -r requirements.txt

# The manifest is committed. It is only rebuilt from the CDC pages if missing,
# or on purpose with `make manifest`.
$(MANIFEST):
	$(PYTHON) -m src.download manifest

manifest:
	$(PYTHON) -m src.download manifest

# Idempotent: files already present with the recorded checksum are skipped.
# Use `make data ACCEPT_REVISIONS=1` to accept files CDC may have revised.
data: $(MANIFEST)
	$(PYTHON) -m src.download fetch $(FETCH_FLAGS)
	$(PYTHON) -m src.download verify

test:
	$(PYTHON) -m pytest -q tests
