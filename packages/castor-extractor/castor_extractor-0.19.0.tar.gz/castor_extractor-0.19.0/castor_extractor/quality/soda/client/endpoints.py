class SodaEndpointFactory:
    """Wrapper class around all endpoints we're using"""

    CLOUD_API = "https://cloud.soda.io/api/v1"
    REPORTING_API = "https://reporting.cloud.soda.io/v1"

    @classmethod
    def datasets(cls) -> str:
        return f"{cls.CLOUD_API}/datasets"

    @classmethod
    def check_results(cls) -> str:
        return f"{cls.REPORTING_API}/quality/check_results"
