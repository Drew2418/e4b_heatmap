# Aircraft Work Order Tracker

A local Flask web app: pick an aircraft area on the home page, see that
area's image with a color-coded heat-map overlay per panel, click a panel
to see its open/closed work orders pulled from an Excel file.

## 1. Install & run

```bash
cd airplane_wo_tracker
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Only needed once, to create placeholder images + sample data so you can
# see it working immediately. Skip this once you've added your own assets.
python3 generate_sample_assets.py

python3 app.py
```

Open **http://localhost:5000** in your browser.

## 2. Swap in your real images

Drop your real aircraft diagrams into `static/images/`, using the filenames
referenced in `config/panels.json` (e.g. `upper_deck.png`), or update the
`"image"` field in that config to match your actual filenames.

**Important:** update `image_width` and `image_height` in `config/panels.json`
for each area to match the real pixel dimensions of your image. The panel
overlays are positioned as a percentage of these dimensions, so if they're
wrong, the colored boxes won't line up with the picture.

## 3. Set your real panel coordinates

Each area in `config/panels.json` has a `panels` list. Each panel needs:

```json
{ "id": "UD-1", "label": "Panel UD-1", "x": 100, "y": 150, "width": 250, "height": 150 }
```

- `id` — must exactly match the value used in the `Panel` column of your Excel file
- `label` — friendly name shown in the modal title and tooltip
- `x`, `y` — pixel coordinates of the panel's top-left corner on your image
- `width`, `height` — pixel size of the panel's clickable box on your image

If your coordinates come from a tool that gives you corner points instead of
a box, just convert to `x, y, width, height` (top-left corner + size).

## 4. Point it at your real Excel file

Replace `data/work_orders.xlsx` with your real file (same filename), with
these exact column headers:

| WO_Number | Description | Area | Panel | POS | Status |
|---|---|---|---|---|---|
| WO-1001 | Replace fastener | upper_deck | UD-2 | UD-2 | Open |

- `Area` must match an area **slug** (see the list in `app.py` → `AREAS`, e.g. `upper_deck`, `left_wing`, `vertical`)
- `Panel` must match a panel `id` from `config/panels.json`
- `Status` should be `Open` or `Closed` (any capitalization is fine)
- `POS` is shown as its own column in the work order list — use it for whatever position/zone code you track

The app re-reads the Excel file on every request, so you can just save the
file and refresh the browser — no restart needed.

## How the heat map coloring works

Each panel's overlay color is computed from its work orders:
- **Gray** — no work orders logged for that panel
- **Green** — work orders exist, all closed
- **Yellow → Red** — scales with the number of *open* work orders (5+ open = full red)

You can tune this in `panel_color()` in `app.py`.

## Project structure

```
airplane_wo_tracker/
├── app.py                     # Flask app & routes
├── generate_sample_assets.py  # one-time helper for placeholder images + sample data
├── requirements.txt
├── config/
│   └── panels.json            # image filenames, dimensions, panel coordinates
├── data/
│   └── work_orders.xlsx       # your work order data (replace this)
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── images/                # your area diagrams go here
└── templates/
    ├── base.html
    ├── home.html
    └── area.html
```

## Ideas for later

- Add a search/filter box in the modal (by status, keyword)
- Add a "last updated" timestamp read from the Excel file's modified time
- Support polygon-shaped panels (not just rectangles) for irregular zones
- Add authentication if this will be exposed beyond your local machine
