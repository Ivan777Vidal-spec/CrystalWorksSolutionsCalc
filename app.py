from flask import Flask, render_template, request

app = Flask(__name__)

# ----------------------------
# SETTINGS
# ----------------------------

RATE_PER_HOUR = 70
MINIMUM_SERVICE_PRICE = 150
OPEN_HOUSE_MINIMUM = 150

RECURRING_DISCOUNTS = {
    "one_time": 0.00,
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

CONDITION_MULTIPLIERS = {
    "normal": 1.00,
    "dirty": 1.10,
    "very_dirty": 1.20,
}

CONDITION_RANGE = {
    "normal": (0.97, 1.05),
    "dirty": (0.98, 1.08),
    "very_dirty": (1.00, 1.12),
}


# ----------------------------
# SERVICE DETAILS
# ----------------------------

RESIDENTIAL_SERVICE_DETAILS = {
    "basic": {
        "label": "Basic Cleaning",
        "purpose": "Routine cleaning for homes that are already maintained. Best for recurring clients.",
        "includes": [
            "Kitchen: wipe countertops, clean sink and faucet, clean stovetop, wipe cabinet fronts, exterior appliance wipe-down",
            "Bathrooms: clean toilet, clean sink and faucet, clean mirrors, light scrub of tub/shower",
            "Bedrooms & living areas: dust accessible surfaces, vacuum carpets, sweep floors, mop floors",
            "General: trash removal, light straightening",
        ],
        "not_included": [
            "Baseboards",
            "Inside appliances",
            "Inside cabinets or drawers",
            "Window cleaning",
            "Heavy scrubbing",
            "Wall cleaning",
        ],
    },
    "first_time": {
        "label": "First-Time Cleaning",
        "purpose": "Used when cleaning a home for the first time. Homes usually need extra work on the first visit.",
        "includes": [
            "Everything in Basic Cleaning",
            "Extra dust removal",
            "Detailed bathroom cleaning",
            "Extra kitchen detailing",
            "Additional buildup removal",
        ],
        "not_included": [
            "Inside oven",
            "Inside refrigerator",
            "Interior windows",
            "Carpet shampooing",
            "Exterior pressure washing",
        ],
    },
    "deep": {
        "label": "Deep Cleaning",
        "purpose": "A more detailed cleaning service for homes needing a thorough reset.",
        "includes": [
            "Everything in Basic Cleaning",
            "Kitchen: clean backsplash, detail around appliances, clean inside microwave",
            "Bathrooms: scrub tile and grout areas, remove soap scum buildup, detail around fixtures",
            "Whole house: baseboards cleaned, door frames wiped, light switch plates cleaned, vent covers dusted",
        ],
        "not_included": [
            "Inside oven",
            "Inside refrigerator",
            "Interior windows",
            "Carpet shampooing",
            "Exterior pressure washing",
        ],
    },
}

REALTOR_SERVICE_DETAILS = {
    "listing_prep": {
        "label": "Listing Preparation",
        "purpose": "Prepare a home for listing photos, showings, and marketing.",
        "includes": [
            "Kitchen: wipe countertops, clean sink and faucet, clean exterior appliances, wipe cabinet fronts, clean stovetop",
            "Bathrooms: clean toilet, clean sink and faucet, clean mirrors, light scrub of shower/tub",
            "Bedrooms & living areas: dust accessible surfaces, vacuum carpets, sweep and mop floors",
            "General: trash removal, quick detail cleaning",
        ],
        "not_included": [
            "Inside cabinets",
            "Inside appliances",
            "Window cleaning",
            "Carpet shampooing",
            "Pressure washing",
        ],
    },
    "vacant_move_out": {
        "label": "Vacant / Move-Out",
        "purpose": "Clean empty homes after tenants move out or before listing.",
        "includes": [
            "Kitchen: wipe cabinets, clean countertops, clean sink and faucet, clean exterior appliances",
            "Bathrooms: deep clean toilets, scrub tubs and showers, clean mirrors and sinks",
            "Whole house: baseboards wiped, closets dusted, floors vacuumed, sweep and mop floors, trash removal",
        ],
        "not_included": [
            "Carpet shampooing",
            "Window cleaning",
            "Exterior pressure washing",
            "Heavy stain removal",
        ],
    },
    "open_house_touchup": {
        "label": "Open House Touch-Up",
        "purpose": "Quick refresh before an open house or showing.",
        "includes": [
            "Wipe countertops",
            "Bathroom quick clean",
            "Mirror cleaning",
            "Vacuum or sweep floors",
            "Trash removal",
            "Quick dusting",
        ],
        "not_included": [
            "Deep cleaning",
            "Appliances",
            "Cabinets",
            "Baseboards",
        ],
    },
    "post_renovation": {
        "label": "Post-Renovation Cleaning",
        "purpose": "Cleaning after remodeling or repairs.",
        "includes": [
            "Removal of dust from surfaces",
            "Cleaning countertops and fixtures",
            "Vacuuming floors",
            "Sweeping and mopping floors",
            "Bathroom wipe-down",
            "Trash removal",
        ],
        "not_included": [
            "Paint removal",
            "Adhesive removal",
            "Window scraping",
            "Heavy debris removal",
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


def build_range(total_price: float, condition_key: str):
    low_mult, high_mult = CONDITION_RANGE.get(condition_key, (0.97, 1.05))
    low = max(MINIMUM_SERVICE_PRICE, total_price * low_mult)
    high = max(MINIMUM_SERVICE_PRICE, total_price * high_mult)
    return money(low), money(high)


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


def calculate_addons(window_count, oven, fridge, carpet_sqft, pressure_sqft, bins):
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
        total = carpet_sqft * 0.35
        addon_total += total
        addon_details.append(("Carpet Cleaning", money(total)))

    if pressure_sqft > 0:
        total = pressure_sqft * 0.37
        addon_total += total
        addon_details.append(("Pressure Washing", money(total)))

    if bins > 0:
        has_other_service = (
            window_count > 0 or oven or fridge or carpet_sqft > 0 or pressure_sqft > 0
        )
        bin_rate = 17 if has_other_service else 20
        total = bins * bin_rate
        addon_total += total
        addon_details.append(("Trash Bin Cleaning", money(total)))

    return money(addon_total), addon_details


def calculate_residential(
    square_feet,
    bedrooms,
    bathrooms,
    kitchens,
    living_rooms,
    dining_rooms,
    hallways,
    condition,
    window_count,
    oven,
    fridge,
    carpet_sqft,
    pressure_sqft,
    bins,
):
    formula_units = residential_formula_units(
        bedrooms, bathrooms, kitchens, living_rooms, dining_rooms, hallways
    )

    base_price = formula_units * RATE_PER_HOUR
    sqft_adjustment = get_sqft_adjustment(square_feet)
    after_sqft = base_price * (1 + sqft_adjustment)

    condition_mult = CONDITION_MULTIPLIERS.get(condition, 1.00)
    conditioned_subtotal = after_sqft * condition_mult

    addon_total, addon_details = calculate_addons(
        window_count, oven, fridge, carpet_sqft, pressure_sqft, bins
    )

    rows = []
    for service_key, multiplier in RESIDENTIAL_MULTIPLIERS.items():
        one_time_total = (conditioned_subtotal * multiplier) + addon_total
        one_time_total = max(one_time_total, MINIMUM_SERVICE_PRICE)

        weekly_total = max(one_time_total * (1 - RECURRING_DISCOUNTS["weekly"]), MINIMUM_SERVICE_PRICE)
        biweekly_total = max(one_time_total * (1 - RECURRING_DISCOUNTS["biweekly"]), MINIMUM_SERVICE_PRICE)
        monthly_total = max(one_time_total * (1 - RECURRING_DISCOUNTS["monthly"]), MINIMUM_SERVICE_PRICE)

        range_low, range_high = build_range(one_time_total, condition)

        rows.append({
            "key": service_key,
            "label": RESIDENTIAL_SERVICE_DETAILS[service_key]["label"],
            "one_time": money(one_time_total),
            "weekly": money(weekly_total),
            "biweekly": money(biweekly_total),
            "monthly": money(monthly_total),
            "range_low": range_low,
            "range_high": range_high,
            "purpose": RESIDENTIAL_SERVICE_DETAILS[service_key]["purpose"],
            "includes": RESIDENTIAL_SERVICE_DETAILS[service_key]["includes"],
            "not_included": RESIDENTIAL_SERVICE_DETAILS[service_key]["not_included"],
        })

    return {
        "square_feet": square_feet,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "kitchens": kitchens,
        "living_rooms": living_rooms,
        "dining_rooms": dining_rooms,
        "hallways": hallways,
        "condition": condition,
        "formula_units": money(formula_units),
        "base_price": money(base_price),
        "sqft_adjustment_pct": int(sqft_adjustment * 100),
        "condition_pct": int((condition_mult - 1) * 100),
        "addon_total": money(addon_total),
        "addon_details": addon_details,
        "rows": rows,
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
):
    formula_units = realtor_formula_units(
        bedrooms, bathrooms, kitchens, living_rooms, dining_rooms, hallways
    )

    base_price = formula_units * RATE_PER_HOUR
    sqft_adjustment = get_sqft_adjustment(square_feet)
    after_sqft = base_price * (1 + sqft_adjustment)

    condition_mult = CONDITION_MULTIPLIERS.get(condition, 1.00)
    after_condition = after_sqft * condition_mult

    service_mult = REALTOR_MULTIPLIERS.get(service_type, 1.00)
    subtotal = after_condition * service_mult

    addon_total, addon_details = calculate_addons(
        window_count, oven, fridge, carpet_sqft, pressure_sqft, bins
    )

    subtotal_with_addons = subtotal + addon_total

    rush_pct = RUSH_FEES.get(rush_type, 0.00)
    total = subtotal_with_addons * (1 + rush_pct)

    if service_type == "open_house_touchup":
        total = max(total, OPEN_HOUSE_MINIMUM)
    else:
        total = max(total, MINIMUM_SERVICE_PRICE)

    range_low, range_high = build_range(total, condition)
    details = REALTOR_SERVICE_DETAILS[service_type]

    return {
        "square_feet": square_feet,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "kitchens": kitchens,
        "living_rooms": living_rooms,
        "dining_rooms": dining_rooms,
        "hallways": hallways,
        "service_type": service_type,
        "service_label": details["label"],
        "purpose": details["purpose"],
        "includes": details["includes"],
        "not_included": details["not_included"],
        "rush_type": rush_type,
        "rush_label": {
            "none": "None",
            "next_day": "Next-Day",
            "same_day": "Same-Day",
        }[rush_type],
        "condition": condition,
        "formula_units": money(formula_units),
        "base_price": money(base_price),
        "sqft_adjustment_pct": int(sqft_adjustment * 100),
        "condition_pct": int((condition_mult - 1) * 100),
        "service_multiplier": service_mult,
        "rush_pct": int(rush_pct * 100),
        "addon_total": money(addon_total),
        "addon_details": addon_details,
        "total": money(total),
        "range_low": range_low,
        "range_high": range_high,
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
                condition=request.form.get("condition", "normal"),
                window_count=safe_int(request.form.get("window_count")),
                oven=("oven" in request.form),
                fridge=("fridge" in request.form),
                carpet_sqft=safe_float(request.form.get("carpet_sqft")),
                pressure_sqft=safe_float(request.form.get("pressure_sqft")),
                bins=safe_int(request.form.get("bins")),
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
            )

    return render_template(
        "index.html",
        active_tab=active_tab,
        residential_result=residential_result,
        realtor_result=realtor_result,
    )


if __name__ == "__main__":
    app.run(debug=True)
