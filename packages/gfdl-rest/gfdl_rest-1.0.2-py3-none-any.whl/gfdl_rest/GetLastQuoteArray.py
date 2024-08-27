from .base_api import BaseAPI

class GetLastQuoteArray(BaseAPI):
    def GetLastQuoteArray(self, exchange, instrument_identifiers):
        endpoint = "GetLastQuoteArray/"
        params = {
            'exchange': exchange,
            'instrumentIdentifiers': instrument_identifiers
        }
        return self._get(endpoint, params)
