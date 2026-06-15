# config.py

SELLER_CONFIG = {
    "SELLER001": {
        "name": "Tech Store",
        "commission_rate": 0.05,
        "active": True
    },
    "SELLER002": {
        "name": "Fashion Store",
        "commission_rate": 0.10,
        "active": True
    },
    "SELLER003": {
        "name": "Book Store",
        "commission_rate": 0.03,
        "active": True
    }
}


def validate_seller(seller_id: str) -> bool:
    """
    Check if seller exists and is active
    """
    seller = SELLER_CONFIG.get(seller_id)
    if not seller:
        return False
    return seller.get("active", False)


def get_commission_rate(seller_id: str) -> float:
    """
    Return commission rate for seller
    Default commission is 5% if seller not found
    """
    seller = SELLER_CONFIG.get(seller_id)
    if not seller:
        return 0.05

    return seller.get("commission_rate", 0.05)
