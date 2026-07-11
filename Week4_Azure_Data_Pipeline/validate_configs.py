"""
validate_configs.py

This script validates the integrity and syntax of the Azure Data Factory
resource configurations (JSON files) created in the 'adf_config' directory.
"""

import json
import os
import sys

def load_json(filepath):
    if not os.path.exists(filepath):
        print(f"[FAIL] File not found: {filepath}")
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"[PASS] Successfully parsed JSON: {filepath}")
            return data
    except json.JSONDecodeError as e:
        print(f"[FAIL] Invalid JSON syntax in {filepath}: {e}")
        return None

def validate_all():
    print("=" * 60)
    print("           ADF CONFIGURATION VALIDATOR")
    print("=" * 60)

    config_dir = "adf_config"
    ls_path = os.path.join(config_dir, "linkedService", "AzureBlobStorageLS.json")
    src_ds_path = os.path.join(config_dir, "dataset", "SourceBlobDataset.json")
    dest_ds_path = os.path.join(config_dir, "dataset", "DestinationBlobDataset.json")
    pl_path = os.path.join(config_dir, "pipeline", "SuperstoreIngestionPipeline.json")

    # Load and validate Linked Service
    ls = load_json(ls_path)
    if not ls: return False
    assert ls.get("name") == "AzureBlobStorageLS", "Linked Service name must be AzureBlobStorageLS"
    assert ls.get("properties", {}).get("type") == "AzureBlobStorage", "Linked Service type must be AzureBlobStorage"
    assert "serviceEndpoint" in ls.get("properties", {}).get("typeProperties", {}), "Linked Service must contain serviceEndpoint for Managed Identity authentication"

    # Load and validate Datasets
    src_ds = load_json(src_ds_path)
    if not src_ds: return False
    assert src_ds.get("name") == "SourceBlobDataset", "Source Dataset name must be SourceBlobDataset"
    assert src_ds.get("properties", {}).get("type") == "DelimitedText", "Source Dataset type must be DelimitedText"
    assert src_ds.get("properties", {}).get("linkedServiceName", {}).get("referenceName") == "AzureBlobStorageLS", "Source Dataset must reference AzureBlobStorageLS linked service"
    assert src_ds.get("properties", {}).get("typeProperties", {}).get("location", {}).get("fileName") == "Sample - Superstore.csv", "Source Dataset fileName must match Sample - Superstore.csv"

    dest_ds = load_json(dest_ds_path)
    if not dest_ds: return False
    assert dest_ds.get("name") == "DestinationBlobDataset", "Destination Dataset name must be DestinationBlobDataset"
    assert dest_ds.get("properties", {}).get("type") == "DelimitedText", "Destination Dataset type must be DelimitedText"
    assert dest_ds.get("properties", {}).get("linkedServiceName", {}).get("referenceName") == "AzureBlobStorageLS", "Destination Dataset must reference AzureBlobStorageLS linked service"

    # Load and validate Pipeline
    pl = load_json(pl_path)
    if not pl: return False
    assert pl.get("name") == "SuperstoreIngestionPipeline", "Pipeline name must be SuperstoreIngestionPipeline"
    
    activities = pl.get("properties", {}).get("activities", [])
    assert len(activities) == 3, f"Pipeline must contain exactly 3 activities, found {len(activities)}"
    
    # Check individual activities
    activity_names = [act.get("name") for act in activities]
    assert "Validate_Source_File" in activity_names, "Missing Validation activity: Validate_Source_File"
    assert "Get_Source_Metadata" in activity_names, "Missing Get Metadata activity: Get_Source_Metadata"
    assert "Copy_Superstore_To_Destination" in activity_names, "Missing Copy activity: Copy_Superstore_To_Destination"

    # Validate sequence dependencies
    val_act = next(act for act in activities if act.get("name") == "Validate_Source_File")
    get_metadata_act = next(act for act in activities if act.get("name") == "Get_Source_Metadata")
    copy_act = next(act for act in activities if act.get("name") == "Copy_Superstore_To_Destination")

    assert len(val_act.get("dependsOn", [])) == 0, "Validation activity should not have any dependencies"
    
    get_metadata_deps = get_metadata_act.get("dependsOn", [])
    assert len(get_metadata_deps) == 1, "Get Metadata activity must have exactly 1 dependency"
    assert get_metadata_deps[0].get("activity") == "Validate_Source_File", "Get Metadata activity must depend on Validate_Source_File"
    assert "Succeeded" in get_metadata_deps[0].get("dependencyConditions", []), "Get Metadata activity dependency condition must be Succeeded"

    copy_deps = copy_act.get("dependsOn", [])
    assert len(copy_deps) == 1, "Copy activity must have exactly 1 dependency"
    assert copy_deps[0].get("activity") == "Get_Source_Metadata", "Copy activity must depend on Get_Source_Metadata"
    assert "Succeeded" in copy_deps[0].get("dependencyConditions", []), "Copy activity dependency condition must be Succeeded"

    # Check copy inputs and outputs
    assert copy_act.get("inputs", [{}])[0].get("referenceName") == "SourceBlobDataset", "Copy activity input must be SourceBlobDataset"
    assert copy_act.get("outputs", [{}])[0].get("referenceName") == "DestinationBlobDataset", "Copy activity output must be DestinationBlobDataset"

    print("=" * 60)
    print("   SUCCESS: ALL CONFIGURATIONS VALID AND DYNAMICALLY LINKED!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = validate_all()
        if not success:
            sys.exit(1)
    except AssertionError as e:
        print(f"[FAIL] Configuration Integrity Error: {e}")
        sys.exit(1)
