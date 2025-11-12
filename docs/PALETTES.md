# Facies Palettes & Legend Specification

Goal: Keep facies→color mapping stable across environments and reports.

Legend Principles:
- Fixed order per environment, consistent between preview and PDFs.
- Colors chosen for grayscale contrast and colorblind safety when possible.
- Legend bar includes name and swatch; same order as masks composition.

Schema (per environment):
```text
env:
  - facies: <name>
    color: <hex or rgb>
  - facies: <name>
    color: <hex or rgb>
```

Recommended Facies Lists:
- Meandering: channel, pointbar, levee, floodplain, oxbow
- Braided: thread, bar, chute, floodplain
- Anastomosing: channel, levee, marsh, floodplain, fan
- Aeolian: crest, slipface, stoss, interdune
- Estuarine: channel, bar, mudflat, shoreline

Implementation Notes:
- Keep the palette definition centralized (e.g., `utils.py` or a JSON file) and import where needed.
- The reporting pipeline should render the legend directly from the palette schema to avoid drift.
