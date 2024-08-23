from urllib.parse import quote_from_bytes

import requests


class HttpAgent:

    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url

    def get_headers(self, extra=None):
        if extra is None:
            extra = {}
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Accept-Encoding": "identity",
            "Api-Key": self.api_key,
            **extra
        }

    def make_get_request(self, path, query_params=None, headers=None):
        headers = self.get_headers(headers)
        try:
            response = requests.get(self.make_absolute_url(path, query_params), headers=headers)
            return self.process_response(response, None)
        except Exception as error:
            return self.process_response(None, error)

    def make_post_request(self, path, data, headers=None):
        headers = self.get_headers(headers)
        try:
            response = requests.post(self.make_absolute_url(path), json=data, headers=headers)
            return self.process_response(response, None)
        except Exception as error:
            return self.process_response(None, error)

    def process_response(self, response, error):
        if error:
            return {"error": str(error)}
        try:
            return {"data": response.json()}
        except Exception:
            return {"data": response.text}

    def make_absolute_url(self, path, query_params=None):
        if path.startswith("http"):
            url = path
        else:
            url = "{}/{}".format(self.base_url.strip("/"), path)

        query = []

        if query_params:
            for key, value in query_params.items():
                if key is not None and value is not None:
                    query.append(
                        quote_from_bytes(str(key).encode('utf-8')) + "=" + quote_from_bytes(str(value).encode('utf-8')))

        if query:
            url += "?" + "&".join(query)

        return url
