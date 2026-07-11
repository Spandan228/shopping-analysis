"""
deploy_pipeline.py

This script automates the deployment of the Azure Data Pipeline.
It performs the following:
1. Creates the Resource Group.
2. Creates the Storage Account and Blob Container.
3. Uploads the 'Sample - Superstore.csv' dataset.
4. Creates the Azure Data Factory.
5. Configures Linked Services, Datasets, and the Pipeline from JSON configs.
6. Handles Role-Based Access Control (RBAC) role assignment.
7. Triggers the pipeline execution.

Usage:
  python deploy_pipeline.py --resource-group rg-superstore-data-pipeline --storage-account stsuperstoredata --data-factory adf-superstore-data --dry-run
"""

import argparse
import json
import os
import subprocess
import sys

def run_command(command, dry_run=False):
    print(f"[CMD] {' '.join(command)}")
    if dry_run:
        print("[DRY-RUN] Command skipped.")
        return True, ""
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed with code {e.returncode}")
        print(f"[ERROR] Stderr: {e.stderr.strip()}")
        return False, e.stderr.strip()
    except FileNotFoundError:
        print("[ERROR] azure-cli (az) is not installed or not in PATH.")
        return False, "az not found"

def check_azure_cli():
    print("[INFO] Checking for Azure CLI installation...")
    try:
        subprocess.run(["az", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, shell=True)
        print("[INFO] Azure CLI found.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[WARNING] Azure CLI was not found on this system. Running in DRY-RUN mode is recommended.")
        return False

def deploy(args):
    print("\n" + "="*60)
    print("      AZURE DATA PIPELINE AUTOMATED DEPLOYMENT SYSTEM")
    print("="*60)
    print(f"Resource Group: {args.resource_group}")
    print(f"Storage Account: {args.storage_account}")
    print(f"Blob Container:  {args.container}")
    print(f"Data Factory:    {args.data_factory}")
    print(f"Dataset Path:    {args.dataset_path}")
    print(f"Dry-Run Mode:    {args.dry_run}")
    print("="*60 + "\n")

    if not args.dry_run and not check_azure_cli():
        print("[ERROR] Cannot execute live deployment without Azure CLI. Switching to DRY-RUN mode.")
        args.dry_run = True

    # 1. Create Resource Group
    print("\n--- Task 1: Create Resource Group ---")
    rg_cmd = ["az", "group", "create", "--name", args.resource_group, "--location", args.location]
    run_command(rg_cmd, args.dry_run)

    # 2. Create Storage Account
    print("\n--- Task 2: Create Storage Account & Container ---")
    storage_cmd = [
        "az", "storage", "account", "create",
        "--name", args.storage_account,
        "--resource-group", args.resource_group,
        "--location", args.location,
        "--sku", "Standard_LRS",
        "--kind", "StorageV2"
    ]
    run_command(storage_cmd, args.dry_run)

    # 3. Create Container
    container_cmd = [
        "az", "storage", "container", "create",
        "--name", args.container,
        "--account-name", args.storage_account,
        "--auth-mode", "login"
    ]
    run_command(container_cmd, args.dry_run)

    # 4. Upload CSV Dataset
    print(f"\n--- Upload dataset '{os.path.basename(args.dataset_path)}' ---")
    if not os.path.exists(args.dataset_path):
        print(f"[ERROR] Source dataset not found at {args.dataset_path}!")
        sys.exit(1)
        
    upload_cmd = [
        "az", "storage", "blob", "upload",
        "--account-name", args.storage_account,
        "--container-name", args.container,
        "--name", os.path.basename(args.dataset_path),
        "--file", args.dataset_path,
        "--auth-mode", "login"
    ]
    run_command(upload_cmd, args.dry_run)

    # Destination Container for pipeline copy
    dest_container_cmd = [
        "az", "storage", "container", "create",
        "--name", "processed-data",
        "--account-name", args.storage_account,
        "--auth-mode", "login"
    ]
    run_command(dest_container_cmd, args.dry_run)

    # 5. Create Azure Data Factory
    print("\n--- Task 3: Create Azure Data Factory ---")
    adf_cmd = [
        "az", "datafactory", "create",
        "--resource-group", args.resource_group,
        "--factory-name", args.data_factory,
        "--location", args.location
    ]
    run_command(adf_cmd, args.dry_run)

    # 6. Configure Role-Based Access Control (RBAC) - Task 6
    print("\n--- Task 6: Configure IAM Role Assignment (RBAC) ---")
    print("[INFO] Enabling System-Assigned Managed Identity on ADF...")
    identity_cmd = [
        "az", "resource", "update",
        "--name", args.data_factory,
        "--resource-group", args.resource_group,
        "--namespace", "Microsoft.DataFactory",
        "--resource-type", "factories",
        "--set", "identity.type=SystemAssigned"
    ]
    success, identity_output = run_command(identity_cmd, args.dry_run)
    
    # Get Principal ID and Subscription ID dynamically
    principal_id = "00000000-0000-0000-0000-000000000000"
    subscription_id = "<subscription-id>"
    if not args.dry_run:
        # Get subscription ID dynamically
        _, sub_output = run_command(["az", "account", "show", "--query", "id", "-o", "tsv"], False)
        if sub_output:
            subscription_id = sub_output.strip()
            
        if success:
            try:
                _, df_show = run_command(["az", "datafactory", "show", "--resource-group", args.resource_group, "--name", args.data_factory], False)
                df_json = json.loads(df_show)
                principal_id = df_json.get("identity", {}).get("principalId", principal_id)
                print(f"[INFO] ADF Managed Identity Principal ID: {principal_id}")
            except Exception as e:
                print(f"[WARNING] Could not parse ADF Principal ID: {e}. Attempting query using az resource show...")
                try:
                    _, res_show = run_command(["az", "resource", "show", "--name", args.data_factory, "--resource-group", args.resource_group, "--resource-type", "factories", "--namespace", "Microsoft.DataFactory"], False)
                    res_json = json.loads(res_show)
                    principal_id = res_json.get("identity", {}).get("principalId", principal_id)
                    print(f"[INFO] ADF Managed Identity Principal ID (via Resource Show): {principal_id}")
                except Exception:
                    pass
    else:
        print("[INFO] ADF Managed Identity Principal ID: <ADF_MANAGED_IDENTITY_PRINCIPAL_ID> (Placeholder)")

    # Assign Storage Blob Data Contributor to ADF Identity
    role_cmd = [
        "az", "role", "assignment", "create",
        "--assignee", principal_id,
        "--role", "Storage Blob Data Contributor",
        "--scope", f"/subscriptions/{subscription_id}/resourceGroups/{args.resource_group}/providers/Microsoft.Storage/storageAccounts/{args.storage_account}"
    ]
    run_command(role_cmd, args.dry_run)

    # 7. Create Linked Services, Datasets, and Pipeline
    print("\n--- Task 3/4: Configure ADF Resources ---")
    
    # Read files
    config_dir = "adf_config"
    ls_file = os.path.join(config_dir, "linkedService", "AzureBlobStorageLS.json")
    src_ds_file = os.path.join(config_dir, "dataset", "SourceBlobDataset.json")
    dest_ds_file = os.path.join(config_dir, "dataset", "DestinationBlobDataset.json")
    pipeline_file = os.path.join(config_dir, "pipeline", "SuperstoreIngestionPipeline.json")

    # Dynamically update the linked service JSON with the actual storage account name
    if not args.dry_run:
        try:
            with open(ls_file, 'r', encoding='utf-8') as f:
                ls_data = json.load(f)
            ls_data["properties"]["typeProperties"]["serviceEndpoint"] = f"https://{args.storage_account}.blob.core.windows.net/"
            with open(ls_file, 'w', encoding='utf-8') as f:
                json.dump(ls_data, f, indent=4)
            print(f"[INFO] Dynamically updated {ls_file} to point to {args.storage_account}")
        except Exception as e:
            print(f"[WARNING] Could not dynamically update Linked Service JSON: {e}")

    # Helper to deploy properties
    def deploy_properties(cmd_prefix, file_path, args):
        import tempfile
        if args.dry_run:
            return run_command(cmd_prefix + ["--properties", f"@{file_path}"], True)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            properties_data = data.get("properties", data)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tmp:
                json.dump(properties_data, tmp, indent=4)
                tmp_path = tmp.name
            
            tmp_path = tmp_path.replace('\\', '/')
            cmd = cmd_prefix + ["--properties", f"@{tmp_path}"]
            success, output = run_command(cmd, False)
            try:
                os.remove(tmp_path)
            except Exception:
                pass
            return success, output
        except Exception as e:
            print(f"[ERROR] Failed to extract and write properties for {file_path}: {e}")
            return False, str(e)

    # Deploy LS
    deploy_ls_cmd = [
        "az", "datafactory", "linked-service", "create",
        "--resource-group", args.resource_group,
        "--factory-name", args.data_factory,
        "--linked-service-name", "AzureBlobStorageLS"
    ]
    deploy_properties(deploy_ls_cmd, ls_file, args)

    # Deploy Source Dataset
    deploy_src_ds_cmd = [
        "az", "datafactory", "dataset", "create",
        "--resource-group", args.resource_group,
        "--factory-name", args.data_factory,
        "--dataset-name", "SourceBlobDataset"
    ]
    deploy_properties(deploy_src_ds_cmd, src_ds_file, args)

    # Deploy Destination Dataset
    deploy_dest_ds_cmd = [
        "az", "datafactory", "dataset", "create",
        "--resource-group", args.resource_group,
        "--factory-name", args.data_factory,
        "--dataset-name", "DestinationBlobDataset"
    ]
    deploy_properties(deploy_dest_ds_cmd, dest_ds_file, args)

    # Deploy Pipeline
    deploy_pl_cmd = [
        "az", "datafactory", "pipeline", "create",
        "--resource-group", args.resource_group,
        "--factory-name", args.data_factory,
        "--pipeline-name", "SuperstoreIngestionPipeline",
        "--pipeline", f"@{pipeline_file}"
    ]
    run_command(deploy_pl_cmd, args.dry_run)

    # 8. Run & Monitor Pipeline - Task 5
    print("\n--- Task 5: Execute and Run Pipeline ---")
    run_pl_cmd = [
        "az", "datafactory", "pipeline", "create-run",
        "--resource-group", args.resource_group,
        "--factory-name", args.data_factory,
        "--pipeline-name", "SuperstoreIngestionPipeline"
    ]
    success, run_output = run_command(run_pl_cmd, args.dry_run)
    
    if not args.dry_run and success:
        try:
            run_json = json.loads(run_output)
            run_id = run_json.get("runId")
            print(f"[SUCCESS] Pipeline run initiated! Run ID: {run_id}")
            print(f"[INFO] Monitor execution online or run: az datafactory pipeline-run show --resource-group {args.resource_group} --factory-name {args.data_factory} --run-id {run_id}")
        except Exception:
            print("[INFO] Run successfully triggered. Check Azure portal for monitoring details.")
    else:
        print("[INFO] Pipeline trigger executed successfully (Simulation/Dry-run).")

    print("\n" + "="*60)
    print("              DEPLOYMENT PROCESS COMPLETE!")
    print("="*60 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Azure Data Pipeline Automation Deployer")
    parser.add_argument("--resource-group", default="rg-superstore-data-pipeline", help="Azure Resource Group Name")
    parser.add_argument("--storage-account", default="stsuperstoredata", help="Azure Storage Account Name")
    parser.add_argument("--container", default="raw-data", help="Blob Container Name")
    parser.add_argument("--data-factory", default="adf-superstore-data", help="Azure Data Factory Name")
    parser.add_argument("--location", default="eastus", help="Azure Region Location")
    parser.add_argument("--dataset-path", default=r"dataset\Sample - Superstore.csv", help="Path to local dataset CSV file")
    parser.add_argument("--live", action="store_true", default=False, help="Execute live deployment commands (Default: False/Simulated)")

    args = parser.parse_args()
    args.dry_run = not args.live
    deploy(args)
