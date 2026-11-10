"""Domain error base (docs/conventions.md, Error handling).

Domain code raises only subclasses of DomainError; app.shared.problem turns them into
RFC 9457 problem+json responses. `detail` is user-facing Turkish text.
"""


class DomainError(Exception):
    status: int = 422
    title: str = "İş kuralı ihlali"

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail
