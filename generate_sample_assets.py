"""
Run this once to generate PLACEHOLDER images and a sample work_orders.xlsx
so the app runs end-to-end out of the box. Replace static/images/*.png with
your real aircraft diagrams (same filenames, or update config/panels.json)
and replace data/work_orders.xlsx with your real data whenever you're ready.
"""
import json
import os
import random

from PIL import Image, ImageDraw, ImageFont
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "config", "panels.json")) as f:
    panels_config = json.load(f)

# ---- Placeholder images ----
os.makedirs(os.path.join(BASE_DIR, "static", "images"), exist_ok=True)
for area_slug, cfg in panels_config.items():
    w, h = cfg["image_width"], cfg["image_height"]
    img = Image.new("RGB", (w, h), color=(214, 224, 232))
    draw = ImageDraw.Draw(img)
    # simple border + label so it's obvious this is a placeholder
    draw.rectangle([4, 4, w - 4, h - 4], outline=(120, 140, 160), width=4)
    label = area_slug.replace("_", " ").title() + " (placeholder image)"
    draw.text((20, 20), label, fill=(60, 80, 100))
    for p in cfg["panels"]:
        draw.rectangle(
            [p["x"], p["y"], p["x"] + p["width"], p["y"] + p["height"]],
            outline=(160, 170, 180),
            width=2,
        )
    img.save(os.path.join(BASE_DIR, "static", "images", cfg["image"]))

# ---- Sample work order data ----
descriptions = [
    "Inspect skin for corrosion",
    "Replace fastener",
    "Torque check",
    "Sealant repair",
    "Access panel inspection",
    "Wiring bundle check",
    "Hydraulic line inspection",
    "Structural repair follow-up",
    "NDT inspection",
    "Paint touch-up",
]

rows = []
wo_counter = 1000
random.seed(7)
for area_slug, cfg in panels_config.items():
    for p in cfg["panels"]:
        num_orders = random.randint(0, 4)
        for _ in range(num_orders):
            wo_counter += 1
            rows.append(
                {
                    "WO_Number": f"WO-{wo_counter}",
                    "Description": random.choice(descriptions),
                    "Area": area_slug,
                    "Panel": p["id"],
                    "POS": p["id"],
                    "Status": random.choice(["Open", "Open", "Closed"]),
                }
            )

df = pd.DataFrame(rows, columns=["WO_Number", "Description", "Area", "Panel", "POS", "Status"])
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
df.to_excel(os.path.join(BASE_DIR, "data", "work_orders.xlsx"), index=False)

print(f"Generated {len(panels_config)} placeholder images and {len(df)} sample work orders.")
