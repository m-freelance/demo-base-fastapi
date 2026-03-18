from passlib.context import CryptContext


class PasswordHasher:
    def __init__(self):
        self._pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

    def encrypt_password(self, password: str) -> str:
        """
        Encrypt the given password using the configured hashing algorithm.

        :param password: The plain text password to encrypt

        :return: The hashed password as a string
        """
        return self._pwd_context.encrypt(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify that the provided plain password matches the hashed password. Returns True if the password is correct, False otherwise.

        :param plain_password: The plain text password to verify
        :param hashed_password: The hashed password to compare against

        :return: True if the password is correct, False otherwise
        """
        return self._pwd_context.verify(plain_password, hashed_password)
