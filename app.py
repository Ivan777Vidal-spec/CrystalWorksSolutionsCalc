from flask import Flask, request, render_template_string

app = Flask(__name__)

RATE = 70.0

# Residential occupied-home weights
W_RES = {
    "bed": 0.75,
    "bath": 1.0,
    "kitchen": 1.0,
    "living": 0.5,
    "dining": 0.5,
    "hall": 0.25,
}

# Realtor / vacant-home weights
W_RE = {
    "bed": 0.60,
    "bath": 1.0,
    "kitchen": 1.25,
    "living": 0.5,
    "dining": 0.5,
    "hall": 0.25,
}


def size_multiplier(sqft: float) -> float:
    if sqft > 5000:
        return 1.30
    if sqft > 4000:
        return 1.20
    if sqft > 3000:
        return 1.15
    if sqft > 2000:
        return 1.10
    return 1.00


def calc_hours(weights: dict, bed: int, bath: int, kitchen: int, living: int, dining: int, hall: int) -> float:
    return (
        bed * weights["bed"]
        + bath * weights["bath"]
        + kitchen * weights["kitchen"]
        + living * weights["living"]
        + dining * weights["dining"]
        + hall * weights["hall"]
    )


def residential_service_multiplier(service_type: str) -> float:
    if service_type == "first_time":
        return 1.18
    if service_type == "deep":
        return 1.30
    return 1.00  # basic


def realtor_service_multiplier(service_type: str) -> float:
    if service_type == "vacant":
        return 1.15
    if service_type == "post_reno":
        return 1.30
    return 1.00  # listing_prep


def rush_multiplier(rush_type: str) -> float:
    if rush_type == "next_day":
        return 1.15
    if rush_type == "same_day":
        return 1.25
    return 1.00


def safe_int(form, key, default=0):
    try:
        return int(form.get(key, default) or 0)
    except ValueError:
        return default


BASE_HTML = """
<!doctype html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{{ title }}</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, Arial, sans-serif;
      margin: 18px;
      max-width: 700px;
    }
    h1 {
      font-size: 24px;
      margin-bottom: 6px;
    }
    .muted {
      color: #666;
      font-size: 13px;
      margin-bottom: 14px;
    }
    .nav {
      margin-bottom: 16px;
    }
    .nav a {
      margin-right: 14px;
      text-decoration: none;
      font-weight: 600;
      color: #222;
    }
    .card {
      border: 1px solid #ddd;
      border-radius: 16px;
      padding: 16px;
      margin-bottom: 16px;
    }
    .grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }
    label {
      font-size: 12px;
      color: #444;
      display: block;
      margin-bottom: 4px;
    }
    input, select {
      width: 100%;
      padding: 10px;
      font-size: 16px;
      border-radius: 10px;
      border: 1px solid #ccc;
      box-sizing: border-box;
    }
    button {
      width: 100%;
      padding: 12px;
      font-size: 16px;
      border: none;
      border-radius: 12px;
      cursor: pointer;
      margin-top: 10px;
    }
    .big {
      font-size: 28px;
      font-weight: 800;
      margin-bottom: 10px;
    }
    .row {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      padding: 4px 0;
      font-size: 14px;
    }
    .quote {
      margin-top: 14px;
      padding: 12px;
      border: 1px dashed #bbb;
      border-radius: 10px;
      white-space: pre-wrap;
      font-size: 14px;
    }
    .section-title {
      font-size: 18px;
      font-weight: 700;
      margin: 4px 0 10px 0;
    }
    .full {
      grid-column: span 2;
    }
    @media (max-width: 640px) {
      .grid {
        grid-template-columns: 1fr;
      }
      .full {
        grid-column: span 1;
      }
    }
  </style>
  <script>
    function copyQuote() {
      const el = document.getElementById("quote");
      if (!el) return;
      navigator.clipboard.writeText(el.innerText);
      alert("Quote copied.");
    }
  </script>
</head>
<body>
  <div class="nav">
    <a href="/">Residential</a>
    <a href="/realtor">Realtor</a>
  </div>

  <h1>{{ header }}</h1>
  <div class="muted">{{ subheader }}</div>

  <div class="card">
    <form method="post">
      <div class="grid">
        {{ form_fields|safe }}
      </div>
      <button type="submit">Calculate</button>
    </form>
  </div>

  {% if result %}
  <div class="card">
    <div class="section-title">Estimate</div>
    <div class="big">${{ "{:,.0f}".format(result["total"]) }}</div>

    {% for label, value in result["details"] %}
      <div class="row">
        <span>{{ label }}</span>
        <span>{{ value }}</span>
      </div>
    {% endfor %}

    <div class="quote" id="quote">{{ result["quote"] }}</div>
    <button type="button" onclick="copyQuote()">Copy Quote Text</button>
  </div>
  {% endif %}
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def residential():
    data = {
        "bed": 3,
        "bath": 2,
        "kitchen": 1,
        "living": 1,
        "dining": 1,
        "hall": 1,
        "sqft": 2000,
        "service_type": "basic",
    }
    result = None

    if request.method == "POST":
        for key in ["bed", "bath", "kitchen", "living", "dining", "hall", "sqft"]:
            data[key] = safe_int(request.form, key, data[key])
        data["service_type"] = request.form.get("service_type", "basic")

        hours = calc_hours(
            W_RES,
            data["bed"],
            data["bath"],
            data["kitchen"],
            data["living"],
            data["dining"],
            data["hall"],
        )
        base_price = hours * RATE
        service_mult = residential_service_multiplier(data["service_type"])
        sqft_mult = size_multiplier(float(data["sqft"]))
        total = base_price * service_mult * sqft_mult

        service_names = {
            "basic": "Basic Cleaning",
            "first_time": "First-Time Cleaning",
            "deep": "Deep Cleaning",
        }
        service_name = service_names[data["service_type"]]

        result = {
            "total": total,
            "details": [
                ("Service", service_name),
                ("Estimated Hours", f"{hours:.2f}"),
                ("Base Price", f"${base_price:,.0f}"),
                ("Service Multiplier", f"×{service_mult:.2f}"),
                ("Sq Ft Multiplier", f"×{sqft_mult:.2f}"),
            ],
            "quote": f"{service_name} – Residential Home\nTotal: ${total:,.0f}",
        }

    form_fields = f"""
      <div>
        <label>Bedrooms</label>
        <input name="bed" type="number" min="0" step="1" value="{data['bed']}">
      </div>
      <div>
        <label>Bathrooms</label>
        <input name="bath" type="number" min="0" step="1" value="{data['bath']}">
      </div>
      <div>
        <label>Kitchens</label>
        <input name="kitchen" type="number" min="0" step="1" value="{data['kitchen']}">
      </div>
      <div>
        <label>Living Rooms</label>
        <input name="living" type="number" min="0" step="1" value="{data['living']}">
      </div>
      <div>
        <label>Dining Rooms</label>
        <input name="dining" type="number" min="0" step="1" value="{data['dining']}">
      </div>
      <div>
        <label>Hallways</label>
        <input name="hall" type="number" min="0" step="1" value="{data['hall']}">
      </div>
      <div class="full">
        <label>Square Footage</label>
        <input name="sqft" type="number" min="0" step="1" value="{data['sqft']}">
      </div>
      <div class="full">
        <label>Service Type</label>
        <select name="service_type">
          <option value="basic" {"selected" if data["service_type"] == "basic" else ""}>Basic Cleaning</option>
          <option value="first_time" {"selected" if data["service_type"] == "first_time" else ""}>First-Time Cleaning</option>
          <option value="deep" {"selected" if data["service_type"] == "deep" else ""}>Deep Cleaning</option>
        </select>
      </div>
    """

    return render_template_string(
        BASE_HTML,
        title="CWS Residential Estimator",
        header="Crystal Works Solutions — Residential Estimator",
        subheader="Internal pricing tool for residential homes.",
        form_fields=form_fields,
        result=result,
    )


@app.route("/realtor", methods=["GET", "POST"])
def realtor():
    data = {
        "bed": 3,
        "bath": 2,
        "kitchen": 1,
        "living": 1,
        "dining": 1,
        "hall": 1,
        "sqft": 2000,
        "service_type": "listing_prep",
        "rush_type": "standard",
    }
    result = None

    if request.method == "POST":
        for key in ["bed", "bath", "kitchen", "living", "dining", "hall", "sqft"]:
            data[key] = safe_int(request.form, key, data[key])
        data["service_type"] = request.form.get("service_type", "listing_prep")
        data["rush_type"] = request.form.get("rush_type", "standard")

        service_names = {
            "listing_prep": "Listing Prep Cleaning",
            "vacant": "Vacant Property / Move-Out Cleaning",
            "touch_up": "Open House Touch-Up",
            "post_reno": "Post-Renovation Cleaning",
        }

        rush_names = {
            "standard": "Standard Scheduling",
            "next_day": "Next-Day Priority",
            "same_day": "Same-Day Emergency",
        }

        service_name = service_names[data["service_type"]]
        rush_name = rush_names[data["rush_type"]]

        if data["service_type"] == "touch_up":
            base_price = 150.0
            service_mult = 1.00
            sqft_mult = 1.00
            rush_mult = rush_multiplier(data["rush_type"])
            total = base_price * rush_mult

            result = {
                "total": total,
                "details": [
                    ("Service", service_name),
                    ("Base Price", f"${base_price:,.0f}"),
                    ("Rush Multiplier", f"×{rush_mult:.2f}"),
                    ("Schedule", rush_name),
                ],
                "quote": f"{service_name}\nTotal: ${total:,.0f}",
            }
        else:
            hours = calc_hours(
                W_RE,
                data["bed"],
                data["bath"],
                data["kitchen"],
                data["living"],
                data["dining"],
                data["hall"],
            )
            formula_base = hours * RATE
            service_mult = realtor_service_multiplier(data["service_type"])
            sqft_mult = size_multiplier(float(data["sqft"]))
            rush_mult = rush_multiplier(data["rush_type"])
            total = formula_base * service_mult * sqft_mult * rush_mult

            result = {
                "total": total,
                "details": [
                    ("Service", service_name),
                    ("Estimated Hours", f"{hours:.2f}"),
                    ("Base Price", f"${formula_base:,.0f}"),
                    ("Service Multiplier", f"×{service_mult:.2f}"),
                    ("Sq Ft Multiplier", f"×{sqft_mult:.2f}"),
                    ("Rush Multiplier", f"×{rush_mult:.2f}"),
                    ("Schedule", rush_name),
                ],
                "quote": f"{service_name}\nTotal: ${total:,.0f}",
            }

    form_fields = f"""
      <div>
        <label>Bedrooms</label>
        <input name="bed" type="number" min="0" step="1" value="{data['bed']}">
      </div>
      <div>
        <label>Bathrooms</label>
        <input name="bath" type="number" min="0" step="1" value="{data['bath']}">
      </div>
      <div>
        <label>Kitchens</label>
        <input name="kitchen" type="number" min="0" step="1" value="{data['kitchen']}">
      </div>
      <div>
        <label>Living Rooms</label>
        <input name="living" type="number" min="0" step="1" value="{data['living']}">
      </div>
      <div>
        <label>Dining Rooms</label>
        <input name="dining" type="number" min="0" step="1" value="{data['dining']}">
      </div>
      <div>
        <label>Hallways</label>
        <input name="hall" type="number" min="0" step="1" value="{data['hall']}">
      </div>
      <div class="full">
        <label>Square Footage</label>
        <input name="sqft" type="number" min="0" step="1" value="{data['sqft']}">
      </div>
      <div class="full">
        <label>Service Type</label>
        <select name="service_type">
          <option value="listing_prep" {"selected" if data["service_type"] == "listing_prep" else ""}>Listing Prep Cleaning</option>
          <option value="vacant" {"selected" if data["service_type"] == "vacant" else ""}>Vacant Property / Move-Out Cleaning</option>
          <option value="touch_up" {"selected" if data["service_type"] == "touch_up" else ""}>Open House Touch-Up</option>
          <option value="post_reno" {"selected" if data["service_type"] == "post_reno" else ""}>Post-Renovation Cleaning</option>
        </select>
      </div>
      <div class="full">
        <label>Rush Scheduling</label>
        <select name="rush_type">
          <option value="standard" {"selected" if data["rush_type"] == "standard" else ""}>Standard Scheduling</option>
          <option value="next_day" {"selected" if data["rush_type"] == "next_day" else ""}>Next-Day Priority (+15%)</option>
          <option value="same_day" {"selected" if data["rush_type"] == "same_day" else ""}>Same-Day Emergency (+25%)</option>
        </select>
      </div>
    """

    return render_template_string(
        BASE_HTML,
        title="CWS Realtor Estimator",
        header="Crystal Works Solutions — Realtor Estimator",
        subheader="Internal pricing tool for listing prep, vacant, touch-up, and post-renovation jobs.",
        form_fields=form_fields,
        result=result,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
