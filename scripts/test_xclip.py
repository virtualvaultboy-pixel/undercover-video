"""Test X-CLIP zero-shot sur 1 video connue.
Verifie que le modele identifie correctement le contenu vs des labels candidats.
"""
import os
import sys
import av
import numpy as np
import torch
from transformers import XCLIPProcessor, XCLIPModel

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def read_video_frames(path, num_frames=8):
    """Lit num_frames etalees uniformement dans la video."""
    container = av.open(path)
    stream = container.streams.video[0]
    total = stream.frames or 0
    if total < 1:
        # fallback : decoder tout pour compter
        frames = [f for f in container.decode(video=0)]
        total = len(frames)
        indices = np.linspace(0, total - 1, num_frames).astype(int)
        return [frames[i].to_ndarray(format="rgb24") for i in indices]
    indices = np.linspace(0, total - 1, num_frames).astype(int)
    frames = []
    container.seek(0)
    idx = 0
    target = set(int(i) for i in indices)
    for f in container.decode(video=0):
        if idx in target:
            frames.append(f.to_ndarray(format="rgb24"))
            if len(frames) >= num_frames:
                break
        idx += 1
    container.close()
    return frames


def main():
    print("[INFO] Loading X-CLIP model (1er run = download ~400 MB)...")
    proc = XCLIPProcessor.from_pretrained("microsoft/xclip-base-patch32")
    model = XCLIPModel.from_pretrained("microsoft/xclip-base-patch32")
    print("[OK] Model loaded")

    test_cases = [
        ("videos/animal-compagnie_1.mp4", "cat"),
        ("videos/animal-compagnie_2.mp4", "dog"),
        ("videos/voiture_1.mp4", "car"),
        ("videos/sport-combat_1.mp4", "boxing"),
        ("videos/boisson-chaude_1.mp4", "coffee"),
    ]

    candidate_labels = [
        "a cat", "a dog", "a car", "a motorcycle", "boxing match",
        "karate", "coffee being poured", "tea being poured",
        "a meme with text", "a cartoon character",
        "a person dancing", "a beach", "food on plate",
    ]

    for vid_rel, expected in test_cases:
        path = os.path.join(ROOT, vid_rel)
        if not os.path.exists(path):
            print(f"[SKIP] {vid_rel} introuvable")
            continue
        try:
            frames = read_video_frames(path, num_frames=8)
        except Exception as e:
            print(f"[ERR] {vid_rel}: {e}")
            continue
        if len(frames) < 8:
            print(f"[WARN] {vid_rel}: only {len(frames)} frames")
            continue

        inputs = proc(text=candidate_labels, videos=list(frames), return_tensors="pt", padding=True)
        with torch.no_grad():
            out = model(**inputs)
        logits = out.logits_per_video[0]
        probs = logits.softmax(dim=-1).numpy()
        top3 = sorted(enumerate(probs), key=lambda x: -x[1])[:3]
        print(f"\n{vid_rel} (expected: {expected!r})")
        for idx, p in top3:
            mark = " <-" if expected.lower() in candidate_labels[idx].lower() else ""
            print(f"  {p*100:5.1f}%  {candidate_labels[idx]!r}{mark}")


if __name__ == "__main__":
    main()
