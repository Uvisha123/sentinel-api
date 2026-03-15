from app.services.security_engine import detect_suspicious_activity
from app.models.blocked_ip import BlockedIP

def test_auto_block_ip(test_db):
    ip_address = "192.168.1.100"
    api_key = "dummy_key"

    detect_suspicious_activity(test_db, api_key, ip_address)

    blocked = test_db.query(BlockedIP).filter(BlockedIP.ip_address == ip_address).first()
    assert blocked is not None
    assert blocked.reason == "Request flood detected"