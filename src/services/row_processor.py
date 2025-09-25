import time
import json
from src.config import settings
from src.services.api_client import insert_lead_to_db
from src.services.db_client import get_models_from_mysql, get_campaign_from_mongo
from src.services.cache_client import redis_client
from src.services.cache_client import cache_get, cache_set
from src.utils.helpers import hashed_key
from src.utils.validation import validate_field, normalize_text_field, normalize_phone, normalize_pincode

def process_row(row_data, sheet, row_idx, logger):
    """Process a single row from the sheet, validate, and insert into DB."""

    headers_row = sheet.row_values(1)
    if settings.STATUS_COLUMN not in headers_row:
        headers_row.append(settings.STATUS_COLUMN)
        sheet.update_cell(1, len(headers_row), settings.STATUS_COLUMN)

    status_col_index = headers_row.index(settings.STATUS_COLUMN) + 1
    current_status = normalize_text_field(row_data.get(settings.STATUS_COLUMN, ''))

    if current_status:
        logger.info(f"Row {row_idx}: Skipped (status='{current_status}')")
        return

    clean_data = {}
    for field in settings.FIELDS_TO_EXTRACT:
        value = normalize_text_field(row_data.get(field, ""))
        if not validate_field(field, value):
            sheet.update_cell(row_idx, status_col_index, "ERROR_UNFORMATTED")
            logger.warning(f"Row {row_idx}: Validation failed for '{field}' → {value}")
            return
        clean_data[field] = value

    logger.info(f"Row {row_idx}: Validation passed → {clean_data}")

    models = get_models_from_mysql(logger)
    campaign_name = clean_data["campaign_name"]

    key_string = f"campaign:{campaign_name.lower()}"
    campaign_cache_key = hashed_key(key_string)
    cached_model = cache_get(campaign_cache_key)
    if cached_model:
        matched_model = json.loads(cached_model)
        logger.info(f"Row {row_idx}: Using cached matched model → {matched_model}")
    else:
        matched_model = next(
            (m for m in models if m["full_model"].lower() in campaign_name.lower()), 
            None
    )
    if matched_model:
        # Store in Redis for future lookups
        cache_set(campaign_cache_key, json.dumps(matched_model), settings.CACHE_TTL )
        logger.info(f"Row {row_idx}: Cached matched model → {matched_model}")

    if not matched_model:
        sheet.update_cell(row_idx, status_col_index, "ERROR_MISMATCHED")
        logger.error(f"Row {row_idx}: No model match for campaign_name='{campaign_name}'")
        return

    logger.info(f"Row {row_idx}: Matched model for campaign '{campaign_name}' → {matched_model}")

    campaign = get_campaign_from_mongo(
        matched_model["brand_slug"],
        matched_model["model_slug"],
        logger
    )
    if not campaign:
        sheet.update_cell(row_idx, status_col_index, "ERROR_MISMATCHED")
        logger.error(f"Row {row_idx}: No active campaign for {matched_model}")
        return

    logger.info(f"Row {row_idx}: Fetched campaign → {campaign}")

    full_name = clean_data["full_name"]
    parts = full_name.split(" ", 1)
    fname = parts[0]
    lname = parts[1] if len(parts) > 1 else ""

    payload = {
        'fname': fname,
        "lname": lname,
        "mobile": normalize_phone(clean_data["phone_number"]),
        "status": "pending",
        "name": full_name,
        "vehicle": campaign["vehicleSlug"],
        "camp_name": campaign["camp_code"],
        "pincode": normalize_pincode(clean_data["zip_code"]),
        "location": clean_data["where_do_you_located_in?"],
        "state": clean_data["state"]
    }

    response = insert_lead_to_db(payload, logger)
    status = "SUCCESS" if response and response.status_code == 200 else "ERROR_INSERTION"
    sheet.update_cell(row_idx, status_col_index, status)
    logger.info(f"Row {row_idx}: Insert result → {status}")

    time.sleep(0.5)