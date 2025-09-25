import json
from flask import Blueprint, request
from src.config import settings
from src.services.google_sheets import get_sheet_client
from src.services.row_processor import process_row

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    from app import logger

    logger.info("=== WEBHOOK RECEIVED ===")
    webhook_secret = request.headers.get("X-Webhook-Secret")

    if webhook_secret != settings.WEBHOOK_SECRET:
        logger.warning("Unauthorized webhook attempt!")
        return "Unauthorized", 401

    try:
        payload = request.get_json()
        logger.info(f"Payload received: {json.dumps(payload, indent=2)}")
    except Exception as e:
        logger.error(f"Failed to parse JSON: {str(e)}")
        return "Invalid JSON", 400

    if not payload or "rows" not in payload:
        logger.error("Invalid payload structure")
        return "Invalid payload", 400

    try:
        sheet = get_sheet_client()
        headers_row = sheet.row_values(1)
        data = sheet.get_all_values()
        logger.info(f"Sheet has {len(data)} rows")

        for row_data in payload["rows"]:
            row_idx = row_data.get("rowIndex")
            if not row_idx:
                logger.warning("No rowIndex found, skipping row")
                continue

            row_values = sheet.row_values(row_idx)
            row_dict = dict(zip(headers_row, row_values))
            process_row(row_dict, sheet, row_idx, logger)

        logger.info("=== WEBHOOK PROCESSING COMPLETE ===")
        return "OK", 200
    except Exception as e:
        logger.exception(f"Webhook processing failed: {str(e)}")
        return "Internal Server Error", 500
