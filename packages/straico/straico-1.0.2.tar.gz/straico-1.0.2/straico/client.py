import requests

# client implementation of
# https://documenter.getpostman.com/view/5900072/2s9YyzddrR

__version__ = "1.0.2"


class StraicoClient:
    base_url = "https://api.straico.com/"

    def __init__(self, api_key: str):
        """
        Takes in the Straico API key for authorization
        """
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    def get_user_data(self) -> dict:
        """
        This endpoint allows users to fetch details of a specific user from the Straico platform. By sending a GET request to the provided URL, including the necessary Authorization header with the user's unique API key, users can access information such as the user's first name, last name, the number of coins associated with the account, and the plan they are subscribed to.

        Returns:
            JSON object containing the user's data, including their first name, last name, available coins, and current plan under the "data" key.
        """
        version = "v0"
        endpoint = self.base_url + version + "/user"
        response = self._make_request("GET", endpoint)
        """
        {
  "data": {
    "first_name": "Jane",
    "last_name": "Doe",
    "coins": 562621.19,
    "plan": "Ultimate Pack"
  },
  "success": true
}
        """
        if response:
            return response["data"]

    def get_model_data(self) -> dict:
        """
        This endpoint allows users to fetch a list of available models along with their details from the Straico API. By sending a GET request to the provided URL and including the required Authorization header with the user's unique API key, users can access information about various models offered by Straico and their associated pricing.

        Returns:
            JSON object containing an array of model objects. Each model object includes details such as the model's name, unique model identifier, and pricing information. The pricing information consists of the cost in coins and the word limit for each model.
        """
        version = "v1"
        endpoint = self.base_url + version + "/models"
        response = self._make_request("GET", endpoint)

        if response:
            return response["data"]

    def make_model_request(
        self,
        models: list,
        message: str,
        file_urls: list = None,
        youtube_urls: list = None,
        display_transcripts: bool = False,
    ) -> dict:

        version = "v1"
        data = {
            "models": models,
            "message": message,
            "file_urls": file_urls,
            "youtube_urls": youtube_urls
        }
        if display_transcripts:
            data['display_transcripts'] = display_transcripts
          
        endpoint = self.base_url + version + "/prompt/completion"
        response = self._make_request("POST", endpoint, json=data)

        if response:
            return response["data"]

    def make_image_request(
        self, model: str, description: str, size: str = "square", variations: int = 1
    ) -> dict:

        version = "v0"
        data = {
            "model": model,
            "description": description,
            "size": size,
            "variations": variations,
        }
        endpoint = self.base_url + version + "/image/generation"
        response = self._make_request("POST", endpoint, json=data)

        if response:
            return response["data"]

    def upload_file(self, file_location: str) -> dict:

        version = "v0"
        
        try:
            with open(file_location, "rb") as f:
                endpoint = self.base_url + version + "/file/upload"
                response = self._make_request("POST", endpoint, files={'file' : f})

        except Exception as e:
            print(e)
            return None

        if response:
            return response["data"]

    def _make_request(self, method: str, url: str, **kwargs):
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            print(
                f"Response content: {e.response.content}"
            )  # Add this line to log the error response
            return None
