from backend.api.exceptions import BaseNotFoundException


class UserNotFoundException(BaseNotFoundException):
    def __init__(self, user_email: int):
        detail = f"User with email {user_email} not found."
        super().__init__(detail=detail)
