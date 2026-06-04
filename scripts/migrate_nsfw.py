"""
Migration : separe les categories NSFW dans videos-nsfw.json + dossier videos/nsfw/
Architecture modulaire pour pouvoir retirer le NSFW en supprimant juste 2 elements.
"""
import os
import json
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEOS_DIR = os.path.join(ROOT, "videos")
NSFW_DIR = os.path.join(VIDEOS_DIR, "nsfw")
JSON_SFW = os.path.join(ROOT, "data", "videos.json")
JSON_NSFW = os.path.join(ROOT, "data", "videos-nsfw.json")


def main():
    os.makedirs(NSFW_DIR, exist_ok=True)

    with open(JSON_SFW, "r", encoding="utf-8") as f:
        data = json.load(f)

    nsfw_cats = []
    sfw_cats = []
    files_moved = 0

    for cat in data["categories"]:
        if cat.get("nsfw"):
            # Migre les URLs : videos/nsfw-xxx_1.mp4 -> videos/nsfw/xxx_1.mp4
            for v in cat["videos"]:
                old_url = v["url"]  # ex: "videos/nsfw-pole-dance_1.mp4"
                old_path = os.path.join(ROOT, old_url)
                # Nouveau nom : on retire le prefixe "nsfw-" qui devient redondant
                base = os.path.basename(old_url)
                if base.startswith("nsfw-"):
                    new_base = base[len("nsfw-"):]
                else:
                    new_base = base
                new_url = f"videos/nsfw/{new_base}"
                new_path = os.path.join(ROOT, new_url)

                if os.path.exists(old_path):
                    shutil.move(old_path, new_path)
                    files_moved += 1
                    print(f"  MOVED {base} -> nsfw/{new_base}")

                v["url"] = new_url
            nsfw_cats.append(cat)
        else:
            sfw_cats.append(cat)

    # Sauve les 2 fichiers
    data["categories"] = sfw_cats
    with open(JSON_SFW, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    nsfw_data = {"categories": nsfw_cats}
    with open(JSON_NSFW, "w", encoding="utf-8") as f:
        json.dump(nsfw_data, f, ensure_ascii=False, indent=2)

    print()
    print(f"[OK] {len(sfw_cats)} categories SFW dans videos.json")
    print(f"[OK] {len(nsfw_cats)} categories NSFW dans videos-nsfw.json")
    print(f"[OK] {files_moved} fichiers MP4 deplaces vers videos/nsfw/")


if __name__ == "__main__":
    main()
