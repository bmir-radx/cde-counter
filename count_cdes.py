import argparse
import json
import os
import pandas as pd

def main(
    in_file: str,
    out_file: str,
    sheet_name: str,
    tier1_json: str,
    tier2_json: str,
):
    # read input data
    var_df = pd.read_excel(in_file, sheet_name=sheet_name)

    # store all variables in sets indexed by phs id
    variables_by_study = {}
    for i, row in var_df.iterrows():
        study_id = row["dbGaP ID"]
        variable_text = row["Variables"]
        variables = set([x.strip() for x in variable_text.split(",")])
        if study_id not in variables_by_study:
            variables_by_study[study_id] = set()
        variables_by_study[study_id] = variables_by_study[study_id].union(variables)

    # load all T1 variables. put domain and codomain in a hash set.
    with open(tier1_json, "r") as f:
        mappings = json.load(f)

    t1 = []
    for maps in mappings.values():
        t1.extend(maps.keys())
        t1.extend(maps.values())
    t1 = set(t1)

    # load all T2 variables.
    with open(tier2_json, "r") as f:
        t2_elements = json.load(f)

    t2 = []
    for variables in t2_elements.values():
        t2.extend(variables)
    t2 = set(t2)

    # deduplicate variables
    t1_variables_by_study = {}
    t2_variables_by_study = {}
    t3_variables_by_study = {}
    for study_id, variables in variables_by_study.items():
        t1_variables_by_study[study_id] = {v for v in variables if v in t1 and v.startswith("nih_")}
        t2_variables_by_study[study_id] = {v for v in variables if v in t2}
        t3_variables_by_study[study_id] = {v for v in variables if (v not in t1 and v not in t2)}

    # log variable counts by study
    data = {
        "Study ID": [],
        "Tier 1 Count": [],
        "Tier 1 CDEs": [],
        "Tier 2 Count": [],
        "Tier 2 CDEs": [],
        "Other Count": [],
        "Other DEs": [],
    }
    for study_id in t1_variables_by_study:
        data["Study ID"].append(study_id)
        data["Tier 1 Count"].append(len(t1_variables_by_study[study_id]))
        data["Tier 1 CDEs"].append(", ".join(t1_variables_by_study[study_id]))
        data["Tier 2 Count"].append(len(t2_variables_by_study[study_id]))
        data["Tier 2 CDEs"].append(", ".join(t2_variables_by_study[study_id]))
        data["Other Count"].append(len(t3_variables_by_study[study_id]))
        data["Other DEs"].append(", ".join(t3_variables_by_study[study_id]))

    # dump counts
    out_df = pd.DataFrame(data)
    out_df.to_csv(out_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A CDE counter that writes counts to CSV.")
    parser.add_argument(
        "-i", "--input",
        required=True,
        type=str,
        help="Name of input xlsx file",
    )
    parser.add_argument(
        "-o", "--output",
        required=False,
        type=str,
        default="counts.csv",
        help="Name of output file (default: counts.csv)",
    )
    parser.add_argument(
        "-s", "--sheet-name",
        required=False,
        type=str,
        default="Variable by Study and File",
        help="Name of xlsx sheet to parse (default: Variable by Study and File)"
    )
    parser.add_argument(
        "-t1", "--tier1-json",
        required=False,
        type=str,
        default=None,
        help="Name of reference for Tier 1 CDE mappings (optional)",
    )
    parser.add_argument(
        "-t2", "--tier2-json",
        required=False,
        type=str,
        default=None,
        help="Name of reference for Tier 2 CDE list (optional)",
    )

    args = parser.parse_args()
    if args.tier1_json is None:
        t1_json = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/global_codebook_rules.json")
    else:
        t1_json = args.tier1_json
    if args.tier2_json is None:
        t2_json = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/tier2_elements.json")
    else:
        t2_json = args.tier2_json

    main(
        args.input,
        args.output,
        args.sheet_name,
        t1_json,
        t2_json,
    )
