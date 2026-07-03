"""
Aircraft Work Order Tracker
----------------------------
A small Flask app that shows a home page of aircraft "areas" (Overview,
Upper Deck, Main Deck, etc). Selecting an area shows that area's image
with a color-coded heat-map overlay for each panel. Clicking a panel
opens a modal listing the work orders for that panel, pulled from an
Excel file.

Run with:  python app.py
Then open: http://localhost:5000
"""

from flask import Flask, render_template, jsonify, abort
import pandas as pd
import json
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(BASE_DIR, "data", "work_orders.xlsx")
PANELS_CONFIG_PATH = os.path.join(BASE_DIR, "config", "panels.json")

# The list of areas shown on the home page. "slug" must match:
#   - the key used in config/panels.json
#   - the value used in the "Area" column of the Excel file
AREAS = [
    {"slug": "overview", "label": "Overview"},
    {"slug": "upper_deck", "label": "Upper Deck"},
    {"slug": "main_deck", "label": "Main Deck"},
    {"slug": "lower_lobe", "label": "Lower Lobe"},
    {"slug": "left_wing", "label": "Left Wing"},
    {"slug": "right_wing", "label": "Right Wing"},
    {"slug": "left_horizontal", "label": "Left Horizontal"},
    {"slug": "right_horizontal", "label": "Right Horizontal"},
    {"slug": "vertical", "label": "Vertical"},
]
AREA_BY_SLUG = {a["slug"]: a for a in AREAS}


def load_panels_config():
    with open(PANELS_CONFIG_PATH, "r") as f:
        return json.load(f)


def load_work_orders():
    """Read the work orders Excel file into a DataFrame.

    Expected columns: WO_Number, Description, Area, Panel, POS, Status
    Status should be 'open' or 'closed' (any case).
    """
    if not os.path.exists(EXCEL_PATH):
        return pd.DataFrame(
            columns=["WO_Number", "Description", "Area", "Panel", "POS", "Status"]
        )
    df = pd.read_excel(EXCEL_PATH)
    df.columns = [str(c).strip() for c in df.columns]
    required = {"WO_Number", "Description", "Area", "Panel", "POS", "Status"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"work_orders.xlsx is missing required column(s): {', '.join(sorted(missing))}"
        )
    df["Area"] = df["Area"].astype(str).str.strip()
    df["Panel"] = df["Panel"].astype(str).str.strip()
    df["Status"] = df["Status"].astype(str).str.strip().str.lower()
    return df


def panel_summary(df, area_slug, panel_id):
    subset = df[(df["Area"] == area_slug) & (df["Panel"] == panel_id)]
    open_count = int((subset["Status"] == "open").sum())
    closed_count = int((subset["Status"] == "closed").sum())
    return open_count, closed_count


def panel_color(open_count, closed_count):
    """Heat-map color for a panel overlay.
    Gray  = no work orders logged
    Green = work orders exist, all closed
    Yellow -> Red = scales with number of OPEN work orders (more open = redder)
    """
    if open_count == 0 and closed_count == 0:
        return "#B0B0B0"
    if open_count == 0:
        return "#4CAF50"
    intensity = min(open_count / 5.0, 1.0)  # cap "full red" at 5+ open WOs
    g = int(215 - 215 * intensity)
    return f"rgb(255,{g},0)"


@app.route("/")
def home():
    return render_template("home.html", areas=AREAS)


@app.route("/area/<area_slug>")
def area_view(area_slug):
    if area_slug not in AREA_BY_SLUG:
        abort(404)

    panels_config = load_panels_config()
    area_config = panels_config.get(area_slug)
    if not area_config:
        abort(
            404,
            description=(
                f"No panel configuration found for '{area_slug}'. "
                f"Add an entry to config/panels.json"
            ),
        )

    df = load_work_orders()
    img_w = area_config.get("image_width", 1000)
    img_h = area_config.get("image_height", 1000)

    panels = []
    for p in area_config.get("panels", []):
        open_c, closed_c = panel_summary(df, area_slug, p["id"])
        panels.append(
            {
                **p,
                "left_pct": p["x"] / img_w * 100,
                "top_pct": p["y"] / img_h * 100,
                "width_pct": p["width"] / img_w * 100,
                "height_pct": p["height"] / img_h * 100,
                "open_count": open_c,
                "closed_count": closed_c,
                "color": panel_color(open_c, closed_c),
            }
        )

    return render_template(
        "area.html",
        area=AREA_BY_SLUG[area_slug],
        image=area_config.get("image"),
        panels=panels,
    )


@app.route("/api/panel/<area_slug>/<panel_id>")
def panel_work_orders(area_slug, panel_id):
    df = load_work_orders()
    subset = df[(df["Area"] == area_slug) & (df["Panel"] == panel_id)]
    orders = [
        {
            "wo_number": r.get("WO_Number", ""),
            "description": r.get("Description", ""),
            "pos": r.get("POS", ""),
            "status": r.get("Status", ""),
        }
        for r in subset.to_dict(orient="records")
    ]
    return jsonify(orders)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
