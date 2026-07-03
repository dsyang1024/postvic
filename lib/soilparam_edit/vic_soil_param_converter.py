import pandas as pd
import argparse
import os

def generate_column_names(nlayer):
    # Fixed scalar fields
    fixed_cols = [
        "gridcell", "run_cell", "lat", "lon", "infilt", "Ds", "Dsmax", "Ws", "num_baseflow_layers"
    ]

    # Per-layer repeated fields
    layer_params = [
        "depth", "Wcr", "Wpwp", "expt", "Ksat", "phi_s", "init_moist",
        "bulk_density", "soil_density", "quartz", "resid_moist", "Eexp",
        "macKsat", "macdepth", "bubble", "quartz2", "resid_moist2"
    ]
    layered_cols = [f"{param}_{i+1}" for param in layer_params for i in range(nlayer)]

    # Final scalar values
    ending_cols = ["off_gmt", "avg_temp", "elevation", "veg_class", "cell_area"]

    return fixed_cols + layered_cols + ending_cols

def convert_csv_to_soil_param(csv_path, output_path, nlayer):
    col_names = generate_column_names(nlayer)
    df = pd.read_csv(csv_path, names=col_names, header=0)

    if df.isnull().values.any():
        raise ValueError(f"❌ Missing values in: {csv_path}")

    with open(output_path, 'w') as f:
        for _, row in df.iterrows():
            values = row.tolist()
            values = [f"{val:.6f}" if isinstance(val, float) else str(val) for val in values]
            f.write(" ".join(values) + "\n")

    print(f"✅ CSV → soil.param: {csv_path} → {output_path}")

def convert_soil_param_to_csv(asc_path, output_csv, nlayer):
    col_names = generate_column_names(nlayer)
    data = []

    with open(asc_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != len(col_names):
                raise ValueError(f"❌ Line length mismatch at {asc_path}. Expected {len(col_names)} values, got {len(parts)}")
            data.append(parts)

    df = pd.DataFrame(data, columns=col_names)
    df.to_csv(output_csv, index=False)
    print(f"✅ soil.param → CSV: {asc_path} → {output_csv}")

def main():
    parser = argparse.ArgumentParser(description="Convert between VIC CSV and soil.param formats")
    parser.add_argument("-n", "--nlayer", type=int, required=True, help="Number of soil layers")
    parser.add_argument("-i", "--inputs", nargs="+", required=True, help="Input file(s)")
    parser.add_argument("-o", "--outdir", default=".", help="Output directory")
    parser.add_argument("--reverse", action="store_true", help="Convert .asc to .csv instead")

    args = parser.parse_args()

    for file_path in args.inputs:
        if not os.path.isfile(file_path):
            print(f"⚠️ Skipping missing file: {file_path}")
            continue

        base = os.path.splitext(os.path.basename(file_path))[0]
        if args.reverse:
            output_file = os.path.join(args.outdir, base + ".csv")
            convert_soil_param_to_csv(file_path, output_file, args.nlayer)
        else:
            output_file = os.path.join(args.outdir, base + ".soilparam.asc")
            convert_csv_to_soil_param(file_path, output_file, args.nlayer)

if __name__ == "__main__":
    main()
