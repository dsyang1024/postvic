# VIC Soil Parameter Converter

This tool provides **two-way conversion** between CSV files and ASCII-format `soil.param` input files used by the [VIC hydrologic model (VIC-4.2)](https://vic.readthedocs.io/en/vic.4.2.2/).

## 🚀 Features

- ✅ Convert CSV → `soil.param` (ASCII format)
- ✅ Convert `soil.param` → CSV (for editing or QA)
- ✅ Supports arbitrary number of soil layers (via `--nlayer`)
- ✅ Command-line interface (CLI)
- ✅ Batch support for multiple files
- ✅ Auto header generation

---

## 📦 Installation

No dependencies outside standard Python:

```bash
python vic_soil_param_converter.py --help
```

---

## 📄 Usage

### ▶ Convert CSV to `soil.param`

```bash
python vic_soil_param_converter.py -n 6 \
    -i sample1.csv sample2.csv \
    -o output/
```

- `-n`: Number of soil layers (must match your VIC model)
- `-i`: One or more CSV files to convert
- `-o`: Output directory

### ◀ Convert `soil.param` to CSV

```bash
python vic_soil_param_converter.py -n 6 \
    -i soil1.asc soil2.asc \
    --reverse \
    -o output/
```

- Use `--reverse` to trigger ASCII → CSV conversion.

---

## 📋 CSV Format

The CSV must include headers. Each row represents a single VIC grid cell. Column names are auto-generated based on `nlayer` and follow the order expected by VIC (e.g., `depth_1`, ..., `Ksat_6`, `phi_s_6`, etc.).

Missing or malformed values will raise an error.

---

## 🔒 Example

Convert a VIC soil.param file back to CSV for editing:

```bash
python vic_soil_param_converter.py -n 6 -i input/soill.param.asc --reverse -o csv_editable/
```

Edit it in Excel or Python, then convert it back:

```bash
python vic_soil_param_converter.py -n 6 -i csv_editable/soill.param.csv -o input/
```

---

## 🧠 Notes

- The script assumes **NLAYER = 6** or as specified by the `-n` flag.
- Be sure to align your input CSV column structure with VIC's layer expectations.
- The script does not validate physical realism of values — only structure.

---

## 📜 License

MIT License