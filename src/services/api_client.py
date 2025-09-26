import requests
from src.config import settings

def insert_lead_to_db(payload, logger):
    """
    Insert the validated and enriched lead into the DB 
    using the configured REST endpoint.
    """

    try:
        response = requests.post(
            settings.LEAD_INSERTION_URL,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )

        # if response.status_code == 201:
        #     logger.info(f"Lead inserted successfully → {payload}")
        # else:
        #     logger.error(f"Lead insertion failed [{response.status_code}] → {response.text}")

        if response.status_code in (200, 201):
            logger.info(f"Lead inserted successfully → {payload}")
        else:
            logger.error(f"Lead insertion failed [{response.status_code}] → {response.text}")

        return response
    except Exception as e:
        logger.exception(f"Lead insertion exception → {str(e)}")
        return None
