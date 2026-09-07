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
    print(f"Total mods in {pack1_name}: {len(mods1)}")
    print(f"Total mods in {pack2_name}: {len(mods2)}")
    print(f"Shared mods in {pack1_name} and {pack2_name}: {len(in_both)}\n")

    print(f"--- Mods ONLY in {pack1_name} ({len(only_in_pack1)}) ---")
    for mod in only_in_pack1:
        print(f"  - {mod}")

    print(f"\n--- Mods ONLY in {pack2_name} ({len(only_in_pack2)}) ---")
    for mod in only_in_pack2:
        print(f"  - {mod}")

    return only_in_pack1, only_in_pack2


def get_modpack_directories():
    """Return CurseForge Minecraft instance directories in name order."""
    instances_dir = (
        Path.home() / "curseforge" / "minecraft" / "Instances"
    )

    if not instances_dir.is_dir():
        print(f"Error: CurseForge instances directory not found: {instances_dir}")
        return []

    return sorted(
        (directory for directory in instances_dir.iterdir() if directory.is_dir()),
        key=lambda directory: directory.name.lower(),
    )


def select_modpacks():
    """Prompt the user to select two installed modpacks to compare."""
    modpacks = get_modpack_directories()

    if len(modpacks) < 2:
        print("Error: At least two modpack directories are required to compare.")
        return None

    print("Available modpacks:")
    for index, modpack in enumerate(modpacks, start=1):
        print(f"  {index}. {modpack.name}")

    while True:
        selection = input("Select two modpacks by number, separated by a comma: ")
        try:
            selected_indexes = [int(value.strip()) for value in selection.split(",")]
        except ValueError:
            print("Please enter two valid numbers separated by a comma.")
            continue

        if (
            len(selected_indexes) == 2
            and selected_indexes[0] != selected_indexes[1]
            and all(1 <= index <= len(modpacks) for index in selected_indexes)
        ):
            return tuple(modpacks[index - 1] for index in selected_indexes)

        print("Please select two different modpacks from the list.")


if __name__ == "__main__":
    selected_modpacks = select_modpacks()

    if selected_modpacks is None:
        raise SystemExit(1)

    modpack_a, modpack_b = selected_modpacks

    while True:
        compare_modpacks(modpack_a, modpack_b)
        input("Press Enter to compare again, or close the window to exit.")