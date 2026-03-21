#!/usr/bin/env python3
"""
Demonstrate machine actionability of a FAIR2Adapt RO-Crate.

Given only an RO-Crate PID, this script:
1. Loads the Research Object from ROHub
2. Discovers ViewAction annotations (schema:potentialAction)
3. Resolves the dataset URL from the linked resource
4. Constructs the dashboard URL from the urlTemplate
5. Opens the dashboard in the browser

No prior knowledge of the dashboard or dataset is needed — everything
is discovered from the RO-Crate annotations.

Usage:
    python demo_machine_actionable.py [RO_PID]

Default RO_PID: https://w3id.org/ro-id/24600867-23ca-4b97-be14-3aa63883c056
"""

import json
import sys
import webbrowser
from pathlib import Path

import rohub
from rohub import settings, utils

# --- Configuration ---
DEFAULT_RO_PID = "https://w3id.org/ro-id/24600867-23ca-4b97-be14-3aa63883c056"

# schema.org terms we look for
POTENTIAL_ACTION = "https://schema.org/potentialAction"
VIEW_ACTION = "https://schema.org/ViewAction"
RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
URL_TEMPLATE = "https://schema.org/urlTemplate"
OBJECT = "https://schema.org/object"
NAME = "https://schema.org/name"


def login():
    """Login to ROHub (required even for reading)."""
    cred_path = Path("~/rohub_credentials.json").expanduser()
    credentials = json.loads(cred_path.read_text())
    rohub.login(username=credentials["username"], password=credentials["password"])


def fetch_triples_for_annotation(annot_id):
    """Fetch triples directly via the ROHub API (bypasses buggy list_triples)."""
    url = settings.API_URL + f"annotations/{annot_id}/body/"
    try:
        r = utils.get_request(url=url, use_token=True)
        if r.status_code != 200:
            return []
        content = r.json()
        results = content.get("results", [])
        while content.get("next"):
            r = utils.get_request(url=content["next"])
            content = r.json()
            results.extend(content.get("results", []))
        return results
    except Exception:
        return []


def collect_all_triples(ro):
    """Collect all triples from all annotations in the RO."""
    triples = []
    for annot in ro.list_annotations():
        triples.extend(fetch_triples_for_annotation(annot["identifier"]))
    return triples


def find_triples(triples, subject=None, predicate=None, obj=None):
    """Filter triples by subject, predicate, and/or object."""
    results = []
    for t in triples:
        if subject and t.get("subject") != subject:
            continue
        if predicate and t.get("predicate") != predicate:
            continue
        if obj and t.get("object") != obj:
            continue
        results.append(t)
    return results


def get_object(triples, subject, predicate):
    """Get the object value of a triple matching subject + predicate."""
    matches = find_triples(triples, subject=subject, predicate=predicate)
    if matches:
        return matches[0]["object"]
    return None


def resolve_dataset_url(ro, resource_uri):
    """Resolve a dataset URL from the resource list.

    First tries to match by resource ID from the URI. If that fails
    (e.g. after a fork where resource IDs change), falls back to
    finding the first Dataset-typed resource in the RO.
    """
    resources = ro.list_resources()

    # Try exact match by resource ID
    resource_id = resource_uri.rstrip("/").split("/")[-1]
    match = resources[resources["identifier"] == resource_id]
    if not match.empty:
        return match.iloc[0]["url"]

    # Fallback: find the Dataset resource by type
    datasets = resources[resources["type"] == "Dataset"]
    if not datasets.empty:
        return datasets.iloc[0]["url"]

    return None


def main():
    ro_pid = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_RO_PID
    ro_id = ro_pid.rstrip("/").split("/")[-1]

    print(f"RO-Crate PID: {ro_pid}")
    print("=" * 60)

    # Step 1: Login and load the RO
    print("\n1. Loading Research Object from ROHub...")
    login()
    ro = rohub.ros_load(identifier=ro_id)
    print(f"   Loaded: {ro.title}")

    # Step 2: Collect all triples
    print("\n2. Collecting annotations...")
    triples = collect_all_triples(ro)
    print(f"   Found {len(triples)} triples across all annotations")

    # Step 3: Find ViewAction(s) via potentialAction
    print("\n3. Discovering ViewAction (schema:potentialAction)...")
    action_triples = find_triples(triples, predicate=POTENTIAL_ACTION)

    if not action_triples:
        print("   No potentialAction found. This RO-Crate has no machine-actionable views.")
        sys.exit(1)

    for action_triple in action_triples:
        action_id = action_triple["object"]
        dataset_res = action_triple["subject"]

        # Verify it's a ViewAction
        action_type = get_object(triples, subject=action_id, predicate=RDF_TYPE)
        if action_type != VIEW_ACTION:
            continue

        action_name = get_object(triples, subject=action_id, predicate=NAME)
        print(f"   Found: {action_name or action_id}")

        # Step 4: Get the URL template
        template = get_object(triples, subject=action_id, predicate=URL_TEMPLATE)
        print(f"   URL template: {template}")

        # Step 5: Resolve the dataset URL from the resource
        dataset_ref = get_object(triples, subject=action_id, predicate=OBJECT)
        print(f"   Dataset resource: {dataset_ref}")

        dataset_url = resolve_dataset_url(ro, dataset_ref)
        if not dataset_url:
            print("   ERROR: Could not resolve dataset URL from resource list.")
            continue

        print(f"   Dataset URL: {dataset_url}")

        # Step 6: Construct the final URL
        final_url = template.replace("{dataset_url}", dataset_url)

        # Step 7: Prompt for API key (for private datasets)
        token = input("\nAPI key (press Enter to skip for public datasets): ").strip()
        if token:
            final_url += f"::token={token}"

        print(f"\n{'=' * 60}")
        print(f"RESOLVED URL: {final_url}")
        print("=" * 60)

        # Step 8: Open in browser
        print("\nOpening dashboard in browser...")
        webbrowser.open(final_url)
        return

    print("   No valid ViewAction found.")
    sys.exit(1)


if __name__ == "__main__":
    main()
