import base64
import json
import shutil
from pathlib import Path

# Directories
BLOCKBENCH_DIR = Path("blockbench/blockbench_projects")
OUTPUT_BASE = Path("src/main/resources/assets/bloodskellyvillage/entity")


def extract_textures_from_bbmodel(entity_dir: Path) -> int:
    extracted = 0
    for bbmodel_path in entity_dir.glob("*.bbmodel"):
        try:
            with bbmodel_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as exc:
            print(f"Failed to read {bbmodel_path}: {exc}")
            continue

        textures = data.get("textures") or []
        if isinstance(textures, dict):
            textures = [textures]

        for texture in textures:
            if not isinstance(texture, dict):
                continue

            name = texture.get("name") or texture.get("id") or "texture"
            source = texture.get("source")
            if not isinstance(source, str):
                continue

            if source.startswith("data:image/png;base64,"):
                png_data = base64.b64decode(source.split(",", 1)[1])
                filename = f"{Path(name).stem}.png"
                dest = entity_dir / filename
                with dest.open("wb") as out_file:
                    out_file.write(png_data)
                print(f"Extracted embedded texture {name} from {bbmodel_path} -> {dest}")
                extracted += 1
            elif source.lower().endswith(".png"):
                ref_path = (entity_dir / source).resolve()
                if ref_path.exists() and ref_path.suffix.lower() == ".png":
                    target = entity_dir / ref_path.name
                    if ref_path != target:
                        shutil.copy2(ref_path, target)
                        print(f"Copied referenced texture {ref_path} -> {target}")
                    extracted += 1
    return extracted


def copy_textures():
    if not BLOCKBENCH_DIR.exists():
        print(f"Blockbench projects folder not found: {BLOCKBENCH_DIR}")
        return

    total_copied = 0
    total_extracted = 0

    for entity_dir in BLOCKBENCH_DIR.iterdir():
        if not entity_dir.is_dir():
            continue

        entity_name = entity_dir.name
        out_dir = OUTPUT_BASE / entity_name
        out_dir.mkdir(parents=True, exist_ok=True)

        extracted = extract_textures_from_bbmodel(entity_dir)
        total_extracted += extracted

        for tex in entity_dir.rglob("*.png"):
            dest = out_dir / tex.name
            shutil.copy2(tex, dest)
            print(f"Copied {tex} -> {dest}")
            total_copied += 1

    print(f"\nTotal embedded textures extracted: {total_extracted}")
    print(f"Total textures copied: {total_copied}")


if __name__ == '__main__':
    copy_textures()
