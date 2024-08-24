class MerriamWebsterClientException(Exception):
    def __init__(self, status_code: int, content: str, url: str) -> None:
        self.message = "Error happened on the Wordnik Client Side"
        super().__init__(self.message)

        self.status_code = status_code
        self.content = content
        self.url = url

    def __str__(self) -> str:
        return f"{self.message}: Status code: {self.status_code}; Content: {self.content}; URL: {self.url}"


class WordnikClientException(MerriamWebsterClientException):
    def __init__(self, status_code: int, content: str, url: str) -> None:
        super().__init__(status_code, content, url)
