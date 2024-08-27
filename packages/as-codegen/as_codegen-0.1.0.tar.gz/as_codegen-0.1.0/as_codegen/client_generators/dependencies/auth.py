import time

import httpx

API_KEY_HEADER = "X-Api-Key"

in_memory_cache: dict = {}


class AuthenticationError(Exception):
    def __init__(self, message, details=None, response_status=None):
        super().__init__(message)
        self.details = details
        self.response_status = response_status


def cache_key_builder(config: dict) -> str:
    """Builds a cache key for the given username and client_id."""
    return f"{config.username}:{config.client_id}"


async def request_access_token(config: dict):
    """Requests an access token using the given configuration."""
    headers = {
        API_KEY_HEADER: config.api_key,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "grant_type": "password",
        "username": config.username,
        "password": config.password,
        "client_id": config.client_id,
        "client_secret": config.client_secret,
    }

    url = f"{config.url}{config.auth_endpoint}"

    response = httpx.post(url, headers=headers, data=data)

    # logger.trace(f"response status: {response.status_code}")

    if response.status_code != 200:
        try:
            error_data = response.json()  # Try to parse as JSON first
        except ValueError:
            error_data = response.text  # Fall back to plain text if JSON parsing fails

        raise AuthenticationError(
            "Authentication failed",
            {
                "response_status": response.status_code,
                "response": error_data,
            },
        )

    parsed_response = response.json()

    in_memory_cache[cache_key_builder(config)] = {
        **parsed_response,
        "timestamp": time.time(),
    }

    return parsed_response


def get_cached_auth_response(config):
    return in_memory_cache.get(cache_key_builder(config))


def is_token_usable(response):
    lead_time = 60  # 1 minute in seconds
    expiration_time = response["timestamp"] + response["expires_in"]
    current_time = time.time()
    return expiration_time > current_time - lead_time


async def get_access_token(config: dict = None):
    """Returns an access token using the given configuration."""
    cached_auth_response = get_cached_auth_response(config)

    if cached_auth_response and is_token_usable(cached_auth_response):
        # logger.info("Cached access token is used")
        return cached_auth_response["access_token"]

    # logger.info("Requesting new access token")
    try:
        auth_response = await request_access_token(config)

        return auth_response["access_token"]
    except (
        Exception
    ) as error:  # Catching a general Exception for broader error handling
        # logger.error(error, "Authentication error")
        print("Error: ", error)
        return None  # Explicitly return None to indicate failure
