import json
import re
from pathlib import Path

#AI generated

def clean_mod_name(filename):
    """Strips version numbers, file extensions, and common prefixes to normalize mod names.

    e.g., 'jei-1.20.1-15.2.0.27.jar' -> 'jei'
    """
    name = Path(filename).stem  # removes extension (.jar)
    # Remove version strings (e.g., -1.20.1-1.0.0, +v1.2, _v2)
    name = re.sub(
        r"[-_+]?(v?\d+\.\d+.*|\d+.*)", "", name, flags=re.IGNORECASE
    )
    # Clean trailing dashes or underscores
    return name.strip("-_ ").lower()


def get_mod_list(dir_path):
    """Extracts mod names from actual .jar files, modlist.html, or manifest.json."""
    folder = Path(dir_path)

    if not folder.is_dir():
        print(f"Error: Path '{dir_path}' is not a valid directory.")
        return None

    mods = set()

    # Case 1: Check for actual .jar files in /mods or root
    jar_files = list(folder.rglob("*.jar"))
    if jar_files:
        for jar in jar_files:
            mods.add(clean_mod_name(jar.name))
        return mods

    # Case 2: Check for CurseForge modlist.html (found in exported modpacks)
    modlist_file = folder / "modlist.html"
    if modlist_file.exists():
        content = modlist_file.read_text(encoding="utf-8")
        # Extract mod names from <li><a href="...">Mod Name</a></li>
        found_mods = re.findall(
            r'href="http[^"]*">(.*?)</a>', content, re.IGNORECASE
        )
        for mod in found_mods:
            mods.add(mod.strip().lower())
        return mods

    # Case 3: Check for manifest.json (CurseForge Project IDs)
    manifest_file = folder / "manifest.json"
    if manifest_file.exists():
        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for file_info in data.get("files", []):
                    # Using Project ID as the identifier
                    mods.add(f"Project ID: {file_info.get('projectID')}")
            return mods
        except Exception as e:
            print(f"Error reading manifest.json: {e}")

    print(
        f"Warning: No .jar files, modlist.html, or manifest.json found in '{dir_path}'"
    )
    return mods


def compare_modpacks(pack1_path, pack2_path):
    mods1 = get_mod_list(pack1_path)
    mods2 = get_mod_list(pack2_path)

    if mods1 is None or mods2 is None:
        return

    pack1_name = Path(pack1_path).name
    pack2_name = Path(pack2_path).name

    # Set operations to find unique mods
    only_in_pack1 = sorted(list(mods1 - mods2))
    only_in_pack2 = sorted(list(mods2 - mods1))
    in_both = sorted(list(mods1 & mods2))

    print(f"=== Modpack Comparison Summary ===")
    print(f"Total mods in 1: {len(mods1)}")
    print(f"Total mods in 2: {len(mods2)}")
    print(f"Shared mods in both: {len(in_both)}\n")

    print(f"--- Mods ONLY in 1 ({len(only_in_pack1)}) ---")
    for mod in only_in_pack1:
        print(f"  - {mod}")

    print(f"\n--- Mods ONLY in 2 ({len(only_in_pack2)}) ---")
    for mod in only_in_pack2:
        print(f"  - {mod}")

    return only_in_pack1, only_in_pack2


if __name__ == "__main__":
    # Point these to the root directories of both modpacks (or their /mods subfolders)
    modpack_a = input('Input path a ')
    modpack_b = input('Input path b ')

    while True:
        compare_modpacks(modpack_a, modpack_b)
        a = input('Again?')