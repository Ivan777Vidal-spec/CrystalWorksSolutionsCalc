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
    "dirty": 0.45,
}
PRESSURE_WASHING_MINIMUM = 130
PRESSURE_WASHING_STAIN_ADDONS = {
    "none": ("No stain add-on", 0),
    "oil_stain_light": ("Oil stain treatment (light)", 40),
    "oil_stain_heavy": ("Oil stain treatment (heavy)", 80),
    "rust_stain_light": ("Rust stain removal (light)", 50),
    "rust_stain_heavy": ("Rust stain removal (heavy)", 120),
    "heavy_buildup": ("Heavy buildup treatment", 60),
}

FLOOR_CARE_RATES = {
    "standard": 0.28,
    "heavy": 0.35,
}
FLOOR_CARE_MINIMUM = 120

RECURRING_DISCOUNTS = {
    "weekly": 0.20,
    "biweekly": 0.15,
    "monthly": 0.10,
}

RESIDENTIAL_MULTIPLIERS = {
    "basic": 1.00,
    "first_time": 1.18,
    "deep": 1.30,
    "vacant": 1.15,
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

BUNDLE_DEFINITIONS = {
    "home_refresh": {
        "name": "Home Refresh",
        "discount": 0.09,
        "service": "deep",
    },
    "move_out_reset": {
        "name": "Move-Out Reset",
        "discount": 0.10,
        "service": "vacant",
    },
    "full_property_reset": {
        "name": "Full Property Reset",
        "discount": 0.12,
        "service": "deep",
    },
}

RESIDENTIAL_SERVICE_DETAILS = {
    "basic": {
        "label": "Basic Cleaning",
        "purpose": "Maintenance cleaning for already-kept homes.",
        "includes": [
            "Kitchen wipe-down",
            "Bathroom cleaning",
            "Dusting",
            "Vacuum",
            "Mop",
            "Trash",
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
        "label": "Plus Cleaning",
        "purpose": "A more detailed clean and the best value option.",
        "includes": [
            "Everything in Basic",
            "Cabinet exteriors",
            "Baseboards spot cleaned",
            "Doors and switches wiped",
            "Deeper bathroom cleaning",
            "Deeper kitchen cleaning",
        ],
        "not_included": [
            "Inside oven unless added",
            "Inside refrigerator unless added",
            "Carpet cleaning unless added",
            "Pressure washing unless added",
        ],
    },
    "deep": {
        "label": "Full Reset / Deep Cleaning",
        "purpose": "Top-to-bottom interior detail cleaning.",
        "includes": [
            "Everything in Plus",
            "Full baseboards",
            "Doors and frames",
            "Blinds / detail areas",
            "Heavy buildup removal",
            "Deep kitchen and bathroom detail",
        ],
        "not_included": [
            "Inside oven unless added",
            "Inside refrigerator unless added",
            "Carpet cleaning unless added",
            "Pressure washing unless added",
        ],
    },
    "vacant": {
        "label": "Vacant / Move-Out Cleaning",
        "purpose": "Detailed cleaning for empty homes, rentals, and move-outs.",
        "includes": [
            "Full surface wipe-down",
            "Cabinets and drawers",
            "Kitchen reset",
            "Bathroom reset",
            "Move-out ready detail cleaning",
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
        "label": "Listing Prep Cleaning",
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
        "label": "Vacant / Move-Out Cleaning",
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

COMMERCIAL_SERVICE_DETAILS = {
    "janitorial": {
        "label": "Commercial Janitorial",
        "description": "General office and facility cleaning for one-time or recurring needs.",
    },
    "carpet": {
        "label": "Commercial Carpet Cleaning",
        "description": "Low-moisture commercial carpet refresh by square footage.",
    },
    "floor_care": {
        "label": "Floor Cleaning & Shine",
        "description": "Broad floor care for scrubbing and shine-focused maintenance.",
    },
}

# helpers + existing functions

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


def round_to_clean_price(value, increment=5):
    if value <= 0:
        return 0
    return int(round(float(value) / increment) * increment)


def calculate_floor_care_total(floor_care_sqft, floor_care_condition):
    if floor_care_sqft <= 0:
        return 0.0, []

    floor_rate = FLOOR_CARE_RATES.get(floor_care_condition, FLOOR_CARE_RATES["standard"])
    base_total = floor_care_sqft * floor_rate
    floor_total = max(base_total, FLOOR_CARE_MINIMUM)

    details = [(f"Floor Cleaning & Shine ({floor_care_condition.title()}) ({floor_care_sqft:g} sq ft × ${floor_rate:.2f})", money(base_total))]

    if base_total < FLOOR_CARE_MINIMUM:
        details.append(("Floor Care Minimum Applied", money(FLOOR_CARE_MINIMUM - base_total)))

    return money(floor_total), details


def select_best_bundle(base_total, selections):
    bundle_candidates = []
    if selections.get("deep_cleaning") and selections.get("carpet_cleaning"):
        bundle_candidates.append(("Home Refresh", 0.09))
    if selections.get("vacant_cleaning") and selections.get("carpet_cleaning"):
        bundle_candidates.append(("Move-Out Reset", 0.10))
    if all(selections.get(key) for key in ["deep_cleaning", "carpet_cleaning", "floor_care", "pressure_washing"]):
        bundle_candidates.append(("Full Property Reset", 0.12))
    if not bundle_candidates:
        return None
    best_bundle = None
    for bundle_name, discount_pct in bundle_candidates:
        discounted_total = round_to_clean_price(base_total * (1 - discount_pct))
        savings = round_to_clean_price(max(base_total - discounted_total, 0))
        bundle_data = {"name": bundle_name, "discount_pct": int(discount_pct * 100), "bundle_price": discounted_total, "savings": savings}
        if best_bundle is None or bundle_data["savings"] > best_bundle["savings"]:
            best_bundle = bundle_data
    return best_bundle


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
    return ((bedrooms * 0.75) + (bathrooms * 1.0) + (kitchens * 1.0) + (living_rooms * 0.5) + (dining_rooms * 0.5) + (hallways * 0.25))


def realtor_formula_units(bedrooms, bathrooms, kitchens, living_rooms, dining_rooms, hallways):
    return ((bedrooms * 0.6) + (bathrooms * 1.0) + (kitchens * 1.25) + (living_rooms * 0.5) + (dining_rooms * 0.5) + (hallways * 0.25))


def calculate_addons(window_count, oven, fridge, carpet_sqft, pressure_sqft, bins, floor_care_sqft=0, floor_care_condition="standard", service_context="residential", pressure_condition="standard", pressure_stain_addon="none"):
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
        addon_details.append((f"Pressure Washing ({pressure_condition.title()}) ({pressure_sqft:g} sq ft × ${pressure_rate:.2f})", money(base_total)))
        if base_total < PRESSURE_WASHING_MINIMUM:
            addon_details.append(("Pressure Washing Minimum Applied", money(PRESSURE_WASHING_MINIMUM - base_total)))
        stain_label, stain_amount = PRESSURE_WASHING_STAIN_ADDONS.get(pressure_stain_addon, PRESSURE_WASHING_STAIN_ADDONS["none"])
        if stain_amount > 0:
            addon_total += stain_amount
            addon_details.append((stain_label, stain_amount))
    floor_care_total, floor_care_details = calculate_floor_care_total(floor_care_sqft, floor_care_condition)
    if floor_care_total > 0:
        addon_total += floor_care_total
        addon_details.extend(floor_care_details)
    if bins > 0:
        has_other_service = (window_count > 0 or oven or fridge or carpet_sqft > 0 or pressure_sqft > 0 or floor_care_sqft > 0)
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
        rows.append({"key": key, "label": label, "normal": money(normal_price), "dirty": money(dirty_price), "very_dirty": money(very_dirty_price), "weekly": money(weekly_price), "biweekly": money(biweekly_price), "monthly": money(monthly_price), "purpose": RESIDENTIAL_SERVICE_DETAILS[key]["purpose"], "includes": RESIDENTIAL_SERVICE_DETAILS[key]["includes"], "not_included": RESIDENTIAL_SERVICE_DETAILS[key]["not_included"]})
    return rows


def calculate_residential(square_feet, bedrooms, bathrooms, kitchens, living_rooms, dining_rooms, hallways, window_count, oven, fridge, carpet_sqft, pressure_sqft, bins, floor_care_sqft, floor_care_condition="standard", pressure_condition="standard", pressure_stain_addon="none", chosen_service="", chosen_condition="normal", selected_bundle="", selected_frequency="one_time"):
    formula_units = residential_formula_units(bedrooms, bathrooms, kitchens, living_rooms, dining_rooms, hallways)
    base_price = formula_units * RESIDENTIAL_RATE_PER_HOUR
    sqft_adjustment = get_sqft_adjustment(square_feet)
    base_subtotal = base_price * (1 + sqft_adjustment)
    valid_service = chosen_service if chosen_service in RESIDENTIAL_MULTIPLIERS else ""
    if selected_bundle in BUNDLE_DEFINITIONS:
        valid_service = BUNDLE_DEFINITIONS[selected_bundle]["service"]

    addon_total, addon_details = calculate_addons(window_count, oven, fridge, carpet_sqft, pressure_sqft, bins, floor_care_sqft=floor_care_sqft, floor_care_condition=floor_care_condition, service_context="residential", pressure_condition=pressure_condition, pressure_stain_addon=pressure_stain_addon)
    rows = build_residential_rows(base_subtotal, addon_total)
    chosen_row = next((row for row in rows if row["key"] == valid_service), None)
    package_total = 0
    recurring_lookup = {"weekly": 0, "biweekly": 0, "monthly": 0}
    if chosen_row:
        package_total = chosen_row["normal"]
        if chosen_condition == "dirty":
            package_total = chosen_row["dirty"]
        elif chosen_condition == "very_dirty":
            package_total = chosen_row["very_dirty"]
        recurring_lookup = {"weekly": round_to_clean_price(chosen_row["weekly"]), "biweekly": round_to_clean_price(chosen_row["biweekly"]), "monthly": round_to_clean_price(chosen_row["monthly"])}
    addon_summary = ", ".join(item for item, _ in addon_details) if addon_details else "None"
    individual_total = round_to_clean_price(package_total if chosen_row else addon_total)
    bundle_selection = {"deep_cleaning": valid_service == "deep", "vacant_cleaning": valid_service == "vacant", "carpet_cleaning": carpet_sqft > 0, "floor_care": floor_care_sqft > 0, "pressure_washing": pressure_sqft > 0}
    best_bundle = select_best_bundle(individual_total, bundle_selection)
    chosen_bundle = None
    if selected_bundle and selected_bundle in BUNDLE_DEFINITIONS:
        definition = BUNDLE_DEFINITIONS[selected_bundle]
        meets_bundle_requirements = (
            (definition["service"] == "deep" and bundle_selection["deep_cleaning"]) or
            (definition["service"] == "vacant" and bundle_selection["vacant_cleaning"])
        ) and bundle_selection["carpet_cleaning"]
        if selected_bundle == "full_property_reset":
            meets_bundle_requirements = meets_bundle_requirements and bundle_selection["floor_care"] and bundle_selection["pressure_washing"]
        if meets_bundle_requirements:
            savings = round_to_clean_price(individual_total * definition["discount"])
            discounted_total = round_to_clean_price(max(individual_total - savings, 0))
            chosen_bundle = {"name": definition["name"], "discount_pct": int(definition["discount"] * 100), "original_price": individual_total, "bundle_price": discounted_total, "savings": savings}

    subtotal_before_bundle = individual_total
    bundle_discount_amount = chosen_bundle["savings"] if chosen_bundle else 0
    total_after_bundle = chosen_bundle["bundle_price"] if chosen_bundle else subtotal_before_bundle

    recurring_map = {"weekly": RECURRING_DISCOUNTS["weekly"], "biweekly": RECURRING_DISCOUNTS["biweekly"], "monthly": RECURRING_DISCOUNTS["monthly"], "one_time": 0}
    recurring_pct = recurring_map.get(selected_frequency, 0)
    recurring_discount_amount = round_to_clean_price(total_after_bundle * recurring_pct)
    final_quote = round_to_clean_price(total_after_bundle - recurring_discount_amount)

    return {
        "square_feet": square_feet,
        "formula_units": money(formula_units),
        "base_price": money(base_price),
        "sqft_adjustment_pct": int(sqft_adjustment * 100),
        "addon_total": addon_total,
        "addon_details": addon_details,
        "rows": rows,
        "chosen_service": valid_service,
        "chosen_service_label": RESIDENTIAL_SERVICE_DETAILS[valid_service]["label"] if valid_service else "No package selected",
        "chosen_condition": chosen_condition,
        "chosen_condition_label": {"normal": "Normal (+0%)", "dirty": "Dirty (+10%)", "very_dirty": "Very Dirty (+20%)"}[chosen_condition],
        "recurring_for_selected": recurring_lookup,
        "bundle_offer": chosen_bundle or best_bundle,
        "selected_bundle": chosen_bundle,
        "individual_service_total": individual_total,
        "addon_summary": addon_summary,
        "subtotal_before_bundle": subtotal_before_bundle,
        "bundle_discount_amount": bundle_discount_amount,
        "total_after_bundle": total_after_bundle,
        "selected_frequency": selected_frequency,
        "recurring_discount_pct": int(recurring_pct * 100),
        "recurring_discount_amount": recurring_discount_amount,
        "final_quote": final_quote,
    }


def calculate_realtor(square_feet, bedrooms, bathrooms, kitchens, living_rooms, dining_rooms, hallways, service_type, rush_type, condition, window_count, oven, fridge, carpet_sqft, pressure_sqft, bins, floor_care_sqft, floor_care_condition="standard", pressure_condition="standard", pressure_stain_addon="none"):
    formula_units = realtor_formula_units(bedrooms, bathrooms, kitchens, living_rooms, dining_rooms, hallways)
    base_price = formula_units * COMMERCIAL_JANITORIAL_RATE_PER_HOUR
    sqft_adjustment = get_sqft_adjustment(square_feet)
    subtotal = base_price * (1 + sqft_adjustment)
    subtotal *= (1 + CONDITION_ADJUSTMENTS.get(condition, 0.00))
    service_multiplier = REALTOR_MULTIPLIERS.get(service_type, 1.00)
    subtotal *= service_multiplier
    addon_total, addon_details = calculate_addons(window_count, oven, fridge, carpet_sqft, pressure_sqft, bins, floor_care_sqft=floor_care_sqft, floor_care_condition=floor_care_condition, service_context="commercial", pressure_condition=pressure_condition, pressure_stain_addon=pressure_stain_addon)
    subtotal += addon_total
    rush_pct = RUSH_FEES.get(rush_type, 0.00)
    total = subtotal * (1 + rush_pct)
    total = max(total, OPEN_HOUSE_MINIMUM if service_type == "open_house_touchup" else MINIMUM_SERVICE_PRICE)
    details = REALTOR_SERVICE_DETAILS[service_type]
    individual_total = round_to_clean_price(total)
    bundle_selection = {"deep_cleaning": service_type == "post_renovation", "vacant_cleaning": service_type == "vacant_move_out", "carpet_cleaning": carpet_sqft > 0, "floor_care": floor_care_sqft > 0, "pressure_washing": pressure_sqft > 0}
    best_bundle = select_best_bundle(individual_total, bundle_selection)
    return {"formula_units": money(formula_units), "base_price": money(base_price), "sqft_adjustment_pct": int(sqft_adjustment * 100), "condition_label": {"normal": "Normal", "dirty": "Dirty", "very_dirty": "Very Dirty"}[condition], "service_label": details["label"], "purpose": details["purpose"], "includes": details["includes"], "not_included": details["not_included"], "rush_label": {"none": "None", "next_day": "Next-Day", "same_day": "Same-Day"}[rush_type], "addon_total": addon_total, "addon_details": addon_details, "service_multiplier": service_multiplier, "rush_pct": int(rush_pct * 100), "total": individual_total, "bundle_offer": best_bundle, "individual_service_total": individual_total}


def calculate_commercial(square_feet, service_type, recurring, carpet_sqft, floor_care_sqft, floor_care_condition="standard"):
    details = COMMERCIAL_SERVICE_DETAILS.get(service_type, COMMERCIAL_SERVICE_DETAILS["janitorial"])
    base_price = 0.0
    line_item = ""
    if service_type == "carpet":
        base_price = max(carpet_sqft * CARPET_RATES["commercial"], MINIMUM_SERVICE_PRICE)
        line_item = f"Commercial Carpet Cleaning ({carpet_sqft:g} sq ft × ${CARPET_RATES['commercial']:.2f})"
    elif service_type == "floor_care":
        base_price, floor_details = calculate_floor_care_total(floor_care_sqft, floor_care_condition)
        line_item = floor_details[0][0] if floor_details else "Floor Cleaning & Shine"
    else:
        units = max((square_feet / 1000) * 1.25, 1.5)
        raw = units * COMMERCIAL_JANITORIAL_RATE_PER_HOUR
        base_price = max(raw, MINIMUM_SERVICE_PRICE)
        line_item = f"Commercial Janitorial ({units:.2f} labor units × ${COMMERCIAL_JANITORIAL_RATE_PER_HOUR}/hr)"
    recurring_total = base_price
    if recurring in RECURRING_DISCOUNTS:
        recurring_total = base_price * (1 - RECURRING_DISCOUNTS[recurring])
    return {
        "service_label": details["label"],
        "description": details["description"],
        "line_item": line_item,
        "base_total": round_to_clean_price(base_price),
        "recurring_label": {"none": "One-Time", "weekly": "Weekly", "biweekly": "Every 2 Weeks", "monthly": "Every 4 Weeks"}.get(recurring, "One-Time"),
        "recurring_pct": int(RECURRING_DISCOUNTS.get(recurring, 0) * 100),
        "final_total": round_to_clean_price(recurring_total),
    }


@app.route('/', methods=['GET', 'POST'])
def index():
    active_tab = 'residential'
    residential_result = None
    realtor_result = None
    commercial_result = None

    if request.method == 'POST':
        form_type = request.form.get('form_type', 'residential')
        active_tab = form_type
        if form_type == 'residential':
            carpet_selected = request.form.get('include_carpet') == 'on'
            pressure_selected = request.form.get('include_pressure') == 'on'
            floor_selected = request.form.get('include_floor_care') == 'on'
            bin_selected = request.form.get('include_bins') == 'on'
            selected_bundle = request.form.get('selected_bundle', '')

            if selected_bundle in {"home_refresh", "move_out_reset"}:
                carpet_selected = True
            elif selected_bundle == "full_property_reset":
                carpet_selected = True
                pressure_selected = True
                floor_selected = True

            residential_result = calculate_residential(
                square_feet=safe_int(request.form.get('square_feet')),
                bedrooms=safe_int(request.form.get('bedrooms')),
                bathrooms=safe_int(request.form.get('bathrooms')),
                kitchens=safe_int(request.form.get('kitchens'), 1),
                living_rooms=safe_int(request.form.get('living_rooms'), 1),
                dining_rooms=safe_int(request.form.get('dining_rooms'), 1),
                hallways=safe_int(request.form.get('hallways'), 1),
                window_count=safe_int(request.form.get('window_count')),
                oven=('oven' in request.form),
                fridge=('fridge' in request.form),
                carpet_sqft=safe_float(request.form.get('carpet_sqft')) if carpet_selected else 0,
                pressure_sqft=safe_float(request.form.get('pressure_sqft')) if pressure_selected else 0,
                bins=safe_int(request.form.get('bins')) if bin_selected else 0,
                floor_care_sqft=safe_float(request.form.get('floor_care_sqft')) if floor_selected else 0,
                floor_care_condition=request.form.get('floor_care_condition', 'standard'),
                pressure_condition=request.form.get('pressure_condition', 'standard'),
                pressure_stain_addon=request.form.get('pressure_stain_addon', 'none'),
                chosen_service=request.form.get('chosen_service', ''),
                chosen_condition=request.form.get('chosen_condition', 'normal'),
                selected_bundle=selected_bundle,
                selected_frequency=request.form.get('display_frequency', 'one_time'),
            )
        elif form_type == 'realtor':
            realtor_result = calculate_realtor(
                square_feet=safe_int(request.form.get('realtor_square_feet')),
                bedrooms=safe_int(request.form.get('realtor_bedrooms')),
                bathrooms=safe_int(request.form.get('realtor_bathrooms')),
                kitchens=safe_int(request.form.get('realtor_kitchens'), 1),
                living_rooms=safe_int(request.form.get('realtor_living_rooms'), 1),
                dining_rooms=safe_int(request.form.get('realtor_dining_rooms'), 1),
                hallways=safe_int(request.form.get('realtor_hallways'), 1),
                service_type=request.form.get('service_type', 'listing_prep'),
                rush_type=request.form.get('rush_type', 'none'),
                condition=request.form.get('realtor_condition', 'normal'),
                window_count=safe_int(request.form.get('realtor_window_count')),
                oven=('realtor_oven' in request.form),
                fridge=('realtor_fridge' in request.form),
                carpet_sqft=safe_float(request.form.get('realtor_carpet_sqft')),
                pressure_sqft=safe_float(request.form.get('realtor_pressure_sqft')),
                bins=safe_int(request.form.get('realtor_bins')),
                floor_care_sqft=safe_float(request.form.get('realtor_floor_care_sqft')),
                floor_care_condition=request.form.get('realtor_floor_care_condition', 'standard'),
                pressure_condition=request.form.get('realtor_pressure_condition', 'standard'),
                pressure_stain_addon=request.form.get('realtor_pressure_stain_addon', 'none'),
            )
        elif form_type == 'commercial':
            commercial_result = calculate_commercial(
                square_feet=safe_int(request.form.get('commercial_square_feet')),
                service_type=request.form.get('commercial_service_type', 'janitorial'),
                recurring=request.form.get('commercial_recurring', 'none'),
                carpet_sqft=safe_float(request.form.get('commercial_carpet_sqft')),
                floor_care_sqft=safe_float(request.form.get('commercial_floor_care_sqft')),
                floor_care_condition=request.form.get('commercial_floor_care_condition', 'standard'),
            )

    pricing_snapshot = {
        'rate_per_hour': RESIDENTIAL_RATE_PER_HOUR,
        'commercial_janitorial_rate_per_hour': COMMERCIAL_JANITORIAL_RATE_PER_HOUR,
        'minimum_service_price': MINIMUM_SERVICE_PRICE,
        'weekly_discount': int(RECURRING_DISCOUNTS['weekly'] * 100),
        'biweekly_discount': int(RECURRING_DISCOUNTS['biweekly'] * 100),
        'monthly_discount': int(RECURRING_DISCOUNTS['monthly'] * 100),
    }

    return render_template('index.html', active_tab=active_tab, residential_result=residential_result, realtor_result=realtor_result, commercial_result=commercial_result, pricing_snapshot=pricing_snapshot, residential_service_details=RESIDENTIAL_SERVICE_DETAILS, realtor_service_details=REALTOR_SERVICE_DETAILS, commercial_service_details=COMMERCIAL_SERVICE_DETAILS)


if __name__ == '__main__':
    app.run(debug=True)
