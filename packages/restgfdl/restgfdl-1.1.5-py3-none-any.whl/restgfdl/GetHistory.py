from .base_api import BaseAPI

class GetHistory(BaseAPI):
    def Get_History(self, exchange, instrument_identifier, periodicity, period, max_results=None, from_timestamp=None, to_timestamp=None):
        endpoint = "GetHistory/"
        params = {
            'exchange': exchange,
            'instrumentIdentifier': instrument_identifier,
            'periodicity': periodicity,
            'period': period
        }
        if max_results:
            params['max'] = max_results
        if from_timestamp:
            params['from'] = from_timestamp
        if to_timestamp:
            params['to'] = to_timestamp
        return self._get(endpoint, params)
