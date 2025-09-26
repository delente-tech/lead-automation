import pymysql
import certifi
from pymongo import MongoClient
from src.services.cache_client import cache_get, cache_set
from src.config import settings
from src.utils.helpers import hashed_key, make_json_serializable

MYSQL_QUERY = """
SELECT CONCAT(b.name, ' ', m.name) AS full_model,
       b.slug AS brand_slug,
       m.slug AS model_slug
FROM CAR_MODELS_EN m
INNER JOIN CAR_BRANDS_EN b 
  ON m.brandSlug = b.slug
WHERE m.status IN ('onsale', 'current')
ORDER BY model_slug;
"""

def get_models_from_mysql(logger):
    key_string = "campaign:model"
    cache_key = hashed_key(key_string)
    cached = cache_get(cache_key)
    if cached:
        logger.info("Loaded models from Redis cache")
        return cached

    connection = pymysql.connect(
        host=settings.MYSQL_HOST,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        database=settings.MYSQL_DB
    )
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute(MYSQL_QUERY)
        results = cursor.fetchall()
        logger.info(results, "")
        cache_set(cache_key, results, settings.CACHE_TTL)
        logger.info("Models loaded from MySQL and cached")
        return results

def get_campaign_from_mongo(brand_slug, model_slug, logger):
    key_string = f"campaign:{brand_slug}:{model_slug}"
    cache_key = hashed_key(key_string)
    cached = cache_get(cache_key)
    if cached:
        logger.info(f"Loaded campaign from Redis for {brand_slug}/{model_slug}")
        return cached

    # client = MongoClient(settings.MONGO_URI,tls=True,
    # tlsCAFile=certifi.where())
    client = MongoClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB]
    campaigns = db[settings.MONGO_CAMPAIGN_COLLECTION]

    campaign = campaigns.find_one({
        "brandSlug": brand_slug,
        "modelSlug": model_slug,
        "status": "active"
    })

    if campaign:
        campaign_serializable = make_json_serializable(campaign)
        cache_set(cache_key, campaign_serializable, settings.REDIS_TTL_SECONDS)
        logger.info(f"Campaign cached in Redis for {brand_slug}/{model_slug}")
    return campaign
