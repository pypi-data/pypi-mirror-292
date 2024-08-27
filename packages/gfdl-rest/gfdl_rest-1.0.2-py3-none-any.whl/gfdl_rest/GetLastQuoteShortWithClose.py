from .base_api import BaseAPI

class GetLastQuoteShortWithClose(BaseAPI):
    def Get_LastQuoteShortWithClose(self, exchange, instrument_identifier):
        endpoint = "GetLastQuoteShortWithClose/"
        params = {
            'exchange': exchange,
            'instrumentIdentifier': instrument_identifier
        }
        return self._get(endpoint, params) 
