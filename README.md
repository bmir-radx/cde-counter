# CDE Counter

This script counts variables used by each study as listed in the RADx Data Hub variable report. It separates the variables by tiers (Tier 1 CDEs, Tier 2 CDEs, and other data elements), and then saves the result to CSV. Example usage:

```bash
python count_cdes.py -i variable-report.xlsx -o counts.csv
```

Variable reports of the expected format can be downloaded from the [variables catalog](https://radxdatahub.nih.gov/variablesCatalog) at the RADx Data Hub.
