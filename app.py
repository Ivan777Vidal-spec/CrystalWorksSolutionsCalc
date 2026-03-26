from flask import Flask, render_template, request

app = Flask(__name__)

# ----------------------------
# SETTINGS
# ----------------------------

RESIDENTIAL_RATE_PER_HOUR = 70
COMMERCIAL_JANITORIAL_RATE_PER_HOUR = 63
MINIMUM_SERVICE_PRICE = 150
OPEN_HOUSE_MINIMUM = 150

CARPET_RATES = {
    "residential": 0.37,
    "commercial": 0.30,
}

PRESSURE_WASHING_RATES = {
    "standard": 0.40,
    "dirty": 0.50,
}
PRESSURE_WASHING_MINIMUM = 130
PRESSURE_WASHING_STAIN_ADDONS = {
    "none": ("No stain add-on", 0),
    "small_oil_rust": ("Small oil/rust stain add-on", 50),
    "medium_oil_rust": ("Medium oil/rust stain add-on", 90),
    "heavy_oil_rust": ("Heavy oil/rust stain add-on", 120),
    "heavy_organic": ("Heavy organic stain add-on", 40),
}

RECURRING_DISCOUNTS = {
    "weekly": 0.20,
    "biweekly": 0.15,
    "monthly": 0.10,
}

RESIDENTIAL_MULTIPLIERS = {
    "basic": 1.00,
    "first_time": 1.18,
    "deep": 1.30,
}

REALTOR_MULTIPLIERS = {
    "listing_prep": 1.00,
    "vacant_move_out": 1.15,
    "post_renovation": 1.30,
    "open_house_touchup": 1.00,
}

RUSH_FEES = {
    "none": 0.00,
    "next_day": 0.15,
    "same_day": 0.25,
}

CONDITION_ADJUSTMENTS = {
    "normal": 0.00,
    "dirty": 0.10,
    "very_dirty": 0.20,
}

RESIDENTIAL_SERVICE_DETAILS = {
    "basic": {
        "label": "Basic Cleaning",
        "purpose": "Routine cleaning for homes that are already maintained.",
        "includes": [
            "Kitchen counters wiped",
            "Sink and faucet cleaned",
            "Bathrooms cleaned",
            "Floors vacuumed and mopped",
            "Dusting accessible surfaces",
            "Trash removal",
        ],
        "not_included": [
            "Inside oven",
            "Inside refrigerator",
            "Interior windows",
            "Heavy buildup removal",
            "Baseboards",
        ],
    },
    "first_time": {
        "label": "First-Time Cleaning",
        "purpose": "For first visits when the home usually needs more work than a maintenance clean.",
        "includes": [
            "Everything in Basic Cleaning",
            "Extra dust removal",
            "More detailed bathroom cleaning",
            "Extra kitchen attention",
            "More buildup removal than basic",
        ],
        "not_included": [
            "Inside oven unless added",
            "Inside refrigerator unless added",
            "Carpet cleaning unless added",
            "Pressure washing unless added",
        ],
    },
    "deep": {
        "label": "Deep Cleaning",
        "purpose": "More detailed reset cleaning for homes that need heavier work.",
        "includes": [
            "Everything in Basic Cleaning",
            "Baseboards wiped",
            "Door frames wiped",
            "Light switch plates wiped",
            "More detailed bathroom scrubbing",
            "More detailed kitchen cleaning",
        ],
        "not_included": [
            "Inside oven unless added",
            "Inside refrigerator unless added",
            "Carpet cleaning unless added",
            "Pressure washing unless added",
        ],
    },
}

REALTOR_SERVICE_DETAILS = {
    "listing_prep": {
        "label": "Listing Preparation",
        "purpose": "Prepare a home for listing photos and showings.",
        "includes": [
            "Counters wiped",
            "Bathrooms cleaned",
            "Dusting",
            "Floors vacuumed and mopped",
            "General detail cleaning",
        ],
        "not_included": [
            "Inside appliances unless added",
            "Carpet cleaning unless added",
            "Pressure washing unless added",
        ],
    },
    "vacant_move_out": {
        "label": "Vacant / Move-Out",
        "purpose": "Cleaning for empty homes before listing or after move-out.",
        "includes": [
            "Kitchen cleaning",
            "Bathroom detail cleaning",
            "Closets dusted",
            "Floors vacuumed and mopped",
            "Trash removal",
        ],
        "not_included": [
            "Heavy stain removal",
            "Carpet cleaning unless added",
            "Pressure washing unless added",
        ],
    },
    "post_renovation": {
        "label": "Post-Renovation Cleaning",
        "purpose": "Cleaning after remodeling or repair work.",
        "includes": [
            "Dust removal from surfaces",
            "Counters and fixtures cleaned",
            "Floors vacuumed",
            "Floors swept and mopped",
            "Bathroom wipe-down",
        ],
        "not_included": [
            "Paint removal",
            "Adhesive removal",
            "Heavy debris hauling",
        ],
    },
    "open_house_touchup": {
        "label": "Open House Touch-Up",
        "purpose": "Quick refresh before an open house or showing.",
        "includes": [
            "Quick countertop wipe-down",
            "Bathroom touch-up",
            "Mirror cleaning",
            "Quick vacuum or sweep",
            "Quick dusting",
        ],
        "not_included": [
            "Deep cleaning",
            "Appliance interior cleaning",
            "Detailed buildup removal",
        ],
    },
}


# ----------------------------
# HELPERS
# ----------------------------

def safe_int(value, default=0):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def money(value):
    return round(float(value), 2)


def get_sqft_adjustment(square_feet: int) -> float:
    if square_feet > 5000:
        return 0.30
    elif square_feet > 4000:
        return 0.20
    elif square_feet > 3000:
        return 0.15
    elif square_feet > 2000:
        return 0.10
    return 0.00


def residential_formula_units(bedrooms, bathrooms, kitchens, living_rooms, dining_rooms, hallways):
    return (
        (bedrooms * 0.75) +
        (bathrooms * 1.0) +
        (kitchens * 1.0) +
        (living_rooms * 0.5) +
        (dining_rooms * 0.5) +
        (hallways * 0.25)
    )


def realtor_formula_units(bedrooms, bathrooms, kitchens, living_rooms, dining_rooms, hallways):
    return (
        (bedrooms * 0.6) +
        (bathrooms * 1.0) +
        (kitchens * 1.25) +
        (living_rooms * 0.5) +
        (dining_rooms * 0.5) +
        (hallways * 0.25)
    )


def calculate_addons(
    window_count,
    oven,
    fridge,
    carpet_sqft,
    pressure_sqft,
    bins,
    service_context="residential",
    pressure_condition="standard",
    pressure_stain_addon="none",
):
    addon_details = []
    addon_total = 0.0

    if window_count > 0:
        total = window_count * 5
        addon_total += total
        addon_details.append(("Window Cleaning", money(total)))

    if oven:
        addon_total += 25
        addon_details.append(("Inside Oven Cleaning", 25))

    if fridge:
        addon_total += 20
        addon_details.append(("Inside Refrigerator Cleaning", 20))

    if carpet_sqft > 0:
        carpet_rate = CARPET_RATES["residential"] if service_context == "residential" else CARPET_RATES["commercial"]
        total = carpet_sqft * carpet_rate
        addon_total += total
        addon_details.append((f"Carpet Cleaning ({carpet_sqft:g} sq ft × ${carpet_rate:.2f})", money(total)))

    if pressure_sqft > 0:
        pressure_rate = PRESSURE_WASHING_RATES.get(pressure_condition, PRESSURE_WASHING_RATES["standard"])
        base_total = pressure_sqft * pressure_rate
        pressure_base_after_minimum = max(base_total, PRESSURE_WASHING_MINIMUM)
        addon_total += pressure_base_after_minimum
        addon_details.append(
            (
                f"Pressure Washing ({pressure_condition.title()}) ({pressure_sqft:g} sq ft × ${pressure_rate:.2f})",
                money(base_total),
            )
        )
        if base_total < PRESSURE_WASHING_MINIMUM:
            addon_details.append(
                (
                    "Pressure Washing Minimum Applied",
                    money(PRESSURE_WASHING_MINIMUM - base_total),
                )
            )

        stain_label, stain_amount = PRESSURE_WASHING_STAIN_ADDONS.get(
            pressure_stain_addon, PRESSURE_WASHING_STAIN_ADDONS["none"]
        )
        if stain_amount > 0:
            addon_total += stain_amount
            addon_details.append((stain_label, stain_amount))

    if bins > 0:
        has_other_service = (
            window_count > 0 or oven or fridge or carpet_sqft > 0 or pressure_sqft > 0
        )
        bin_rate = 17 if has_other_service else 20
        total = bins * bin_rate
        addon_total += total
        addon_details.append(("Trash Bin Cleaning", money(total)))

    return money(addon_total), addon_details


def build_residential_rows(base_subtotal, addon_total):
    rows = []

    for key, multiplier in RESIDENTIAL_MULTIPLIERS.items():
        label = RESIDENTIAL_SERVICE_DETAILS[key]["label"]

        normal_price = max((base_subtotal * multiplier) + addon_total, MINIMUM_SERVICE_PRICE)
        dirty_price = max((base_subtotal * multiplier * 1.10) + addon_total, MINIMUM_SERVICE_PRICE)
        very_dirty_price = max((base_subtotal * multiplier * 1.20) + addon_total, MINIMUM_SERVICE_PRICE)

        weekly_price = max(normal_price * (1 - RECURRING_DISCOUNTS["weekly"]), MINIMUM_SERVICE_PRICE)
        biweekly_price = max(normal_price * (1 - RECURRING_DISCOUNTS["biweekly"]), MINIMUM_SERVICE_PRICE)
        monthly_price = max(normal_price * (1 - RECURRING_DISCOUNTS["monthly"]), MINIMUM_SERVICE_PRICE)

        rows.append({
            "key": key,
            "label": label,
            "normal": money(normal_price),
            "dirty": money(dirty_price),
            "very_dirty": money(very_dirty_price),
            "weekly": money(weekly_price),
            "biweekly": money(biweekly_price),
            "monthly": money(monthly_price),
            "purpose": RESIDENTIAL_SERVICE_DETAILS[key]["purpose"],
            "includes": RESIDENTIAL_SERVICE_DETAILS[key]["includes"],
            "not_included": RESIDENTIAL_SERVICE_DETAILS[key]["not_included"],
        })

    return rows


def calculate_residential(
    square_feet,
    bedrooms,
    bathrooms,
    kitchens,
    living_rooms,
    dining_rooms,
    hallways,
    window_count,
    oven,
    fridge,
    carpet_sqft,
    pressure_sqft,
    bins,
    pressure_condition="standard",
    pressure_stain_addon="none",
    chosen_service="first_time",
    chosen_condition="normal",
):
    formula_units = residential_formula_units(
        bedrooms, bathrooms, kitchens, living_rooms, dining_rooms, hallways
    )

    base_price = formula_units * RESIDENTIAL_RATE_PER_HOUR
    sqft_adjustment = get_sqft_adjustment(square_feet)
    base_subtotal = base_price * (1 + sqft_adjustment)

    addon_total, addon_details = calculate_addons(
        window_count,
        oven,
        fridge,
        carpet_sqft,
        pressure_sqft,
        bins,
        service_context="residential",
        pressure_condition=pressure_condition,
        pressure_stain_addon=pressure_stain_addon,
    )

    rows = build_residential_rows(base_subtotal, addon_total)

    chosen_row = next((row for row in rows if row["key"] == chosen_service), rows[1])

    if chosen_condition == "dirty":
        final_quote = chosen_row["dirty"]
    elif chosen_condition == "very_dirty":
        final_quote = chosen_row["very_dirty"]
    else:
        final_quote = chosen_row["normal"]

    recurring_lookup = {
        "weekly": chosen_row["weekly"],
        "biweekly": chosen_row["biweekly"],
        "monthly": chosen_row["monthly"],
    }

    service_price_lookup = {
        row["key"]: {
            "normal": row["normal"],
            "dirty": row["dirty"],
            "very_dirty": row["very_dirty"],
        }
        for row in rows
    }

    addon_summary = ", ".join(item for item, _ in addon_details) if addon_details else "None"

    return {
        "square_feet": square_feet,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "kitchens": kitchens,
        "living_rooms": living_rooms,
        "dining_rooms": dining_rooms,
        "hallways": hallways,
        "formula_units": money(formula_units),
        "base_price": money(base_price),
        "sqft_adjustment_pct": int(sqft_adjustment * 100),
        "addon_total": addon_total,
        "addon_details": addon_details,
        "rows": rows,
        "chosen_service": chosen_service,
        "chosen_service_label": RESIDENTIAL_SERVICE_DETAILS[chosen_service]["label"],
        "chosen_condition": chosen_condition,
        "chosen_condition_label": {
            "normal": "Normal (+0%)",
            "dirty": "Dirty (+10%)",
            "very_dirty": "Very Dirty (+20%)",
        }[chosen_condition],
        "final_quote": money(final_quote),
        "recurring_for_selected": recurring_lookup,
        "service_price_lookup": service_price_lookup,
        "addon_summary": addon_summary,
    }


def calculate_realtor(
    square_feet,
    bedrooms,
    bathrooms,
    kitchens,
    living_rooms,
    dining_rooms,
    hallways,
    service_type,
    rush_type,
    condition,
    window_count,
    oven,
    fridge,
    carpet_sqft,
    pressure_sqft,
    bins,
    pressure_condition="standard",
    pressure_stain_addon="none",
):
    formula_units = realtor_formula_units(
        bedrooms, bathrooms, kitchens, living_rooms, dining_rooms, hallways
    )

    base_price = formula_units * COMMERCIAL_JANITORIAL_RATE_PER_HOUR
    sqft_adjustment = get_sqft_adjustment(square_feet)
    subtotal = base_price * (1 + sqft_adjustment)

    condition_rate = CONDITION_ADJUSTMENTS.get(condition, 0.00)
    subtotal *= (1 + condition_rate)

    service_multiplier = REALTOR_MULTIPLIERS.get(service_type, 1.00)
    subtotal *= service_multiplier

    addon_total, addon_details = calculate_addons(
        window_count,
        oven,
        fridge,
        carpet_sqft,
        pressure_sqft,
        bins,
        service_context="commercial",
        pressure_condition=pressure_condition,
        pressure_stain_addon=pressure_stain_addon,
    )

    subtotal += addon_total

    rush_pct = RUSH_FEES.get(rush_type, 0.00)
    total = subtotal * (1 + rush_pct)

    if service_type == "open_house_touchup":
        total = max(total, OPEN_HOUSE_MINIMUM)
    else:
        total = max(total, MINIMUM_SERVICE_PRICE)

    details = REALTOR_SERVICE_DETAILS[service_type]

    return {
        "square_feet": square_feet,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "kitchens": kitchens,
        "living_rooms": living_rooms,
        "dining_rooms": dining_rooms,
        "hallways": hallways,
        "formula_units": money(formula_units),
        "base_price": money(base_price),
        "sqft_adjustment_pct": int(sqft_adjustment * 100),
        "condition_label": {
            "normal": "Normal",
            "dirty": "Dirty",
            "very_dirty": "Very Dirty",
        }[condition],
        "service_label": details["label"],
        "purpose": details["purpose"],
        "includes": details["includes"],
        "not_included": details["not_included"],
        "rush_label": {
            "none": "None",
            "next_day": "Next-Day",
            "same_day": "Same-Day",
        }[rush_type],
        "addon_total": addon_total,
        "addon_details": addon_details,
        "service_multiplier": service_multiplier,
        "rush_pct": int(rush_pct * 100),
        "total": money(total),
    }


# ----------------------------
# ROUTE
# ----------------------------

@app.route("/", methods=["GET", "POST"])
def index():
    active_tab = "residential"
    residential_result = None
    realtor_result = None

    if request.method == "POST":
        form_type = request.form.get("form_type", "residential")
        active_tab = form_type

        if form_type == "residential":
            residential_result = calculate_residential(
                square_feet=safe_int(request.form.get("square_feet")),
                bedrooms=safe_int(request.form.get("bedrooms")),
                bathrooms=safe_int(request.form.get("bathrooms")),
                kitchens=safe_int(request.form.get("kitchens"), 1),
                living_rooms=safe_int(request.form.get("living_rooms"), 1),
                dining_rooms=safe_int(request.form.get("dining_rooms"), 1),
                hallways=safe_int(request.form.get("hallways"), 1),
                window_count=safe_int(request.form.get("window_count")),
                oven=("oven" in request.form),
                fridge=("fridge" in request.form),
                carpet_sqft=safe_float(request.form.get("carpet_sqft")),
                pressure_sqft=safe_float(request.form.get("pressure_sqft")),
                bins=safe_int(request.form.get("bins")),
                pressure_condition=request.form.get("pressure_condition", "standard"),
                pressure_stain_addon=request.form.get("pressure_stain_addon", "none"),
                chosen_service=request.form.get("chosen_service", "first_time"),
                chosen_condition=request.form.get("chosen_condition", "normal"),
            )

        elif form_type == "realtor":
            realtor_result = calculate_realtor(
                square_feet=safe_int(request.form.get("realtor_square_feet")),
                bedrooms=safe_int(request.form.get("realtor_bedrooms")),
                bathrooms=safe_int(request.form.get("realtor_bathrooms")),
                kitchens=safe_int(request.form.get("realtor_kitchens"), 1),
                living_rooms=safe_int(request.form.get("realtor_living_rooms"), 1),
                dining_rooms=safe_int(request.form.get("realtor_dining_rooms"), 1),
                hallways=safe_int(request.form.get("realtor_hallways"), 1),
                service_type=request.form.get("service_type", "listing_prep"),
                rush_type=request.form.get("rush_type", "none"),
                condition=request.form.get("realtor_condition", "normal"),
                window_count=safe_int(request.form.get("realtor_window_count")),
                oven=("realtor_oven" in request.form),
                fridge=("realtor_fridge" in request.form),
                carpet_sqft=safe_float(request.form.get("realtor_carpet_sqft")),
                pressure_sqft=safe_float(request.form.get("realtor_pressure_sqft")),
                bins=safe_int(request.form.get("realtor_bins")),
                pressure_condition=request.form.get("realtor_pressure_condition", "standard"),
                pressure_stain_addon=request.form.get("realtor_pressure_stain_addon", "none"),
            )

    pricing_snapshot = {
        "rate_per_hour": RESIDENTIAL_RATE_PER_HOUR,
        "commercial_janitorial_rate_per_hour": COMMERCIAL_JANITORIAL_RATE_PER_HOUR,
        "minimum_service_price": MINIMUM_SERVICE_PRICE,
        "weekly_discount": int(RECURRING_DISCOUNTS["weekly"] * 100),
        "biweekly_discount": int(RECURRING_DISCOUNTS["biweekly"] * 100),
        "monthly_discount": int(RECURRING_DISCOUNTS["monthly"] * 100),
    }

    return render_template(
        "index.html",
        active_tab=active_tab,
        residential_result=residential_result,
        realtor_result=realtor_result,
        pricing_snapshot=pricing_snapshot,
        residential_service_details=RESIDENTIAL_SERVICE_DETAILS,
        realtor_service_details=REALTOR_SERVICE_DETAILS,
    )


if __name__ == "__main__":
    app.run(debug=True)
