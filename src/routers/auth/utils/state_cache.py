# Basic in memory storage for state validation
#
# It is not the best solution :
# - it can still be vulnerable to replay attacks
# - it can leak memory
#
# A better solution would be to use signed states that can be verified (cheksum)

import time

_state_cache = {}


def store_state(state: str) -> None:
    """Store state with timestamp for validation"""
    _state_cache[state] = {
        "timestamp": time.time(),
    }


def validate_and_remove_state(state: str, max_age: int = 600) -> bool:
    """Validate state and remove it from cache"""
    if state not in _state_cache:
        return False

    stored_data = _state_cache.pop(state)
    return (time.time() - stored_data["timestamp"]) <= max_age
