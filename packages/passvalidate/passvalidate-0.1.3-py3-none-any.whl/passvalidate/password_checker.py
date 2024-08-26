import re
from typing import List, Tuple


class PasswordPolicy:
    def __init__(
        self,
        min_length: int = 8,
        min_uppercase: int = 1,
        min_lowercase: int = 2,
        min_digits: int = 1,
        min_special: int = 1,
        special_chars: str = r"[ !#$%&'()*+,-./[\\\]^_`{|}~"+r'"]',
        allow_spaces: bool = False
    ):
        self.min_length = min_length
        self.min_uppercase = min_uppercase
        self.min_lowercase = min_lowercase
        self.min_digits = min_digits
        self.min_special = min_special
        self.special_chars = special_chars
        self.allow_spaces = allow_spaces

    def check_password(self, password: str) -> Tuple[bool, List[str]]:
        """
        Checks a password against the defined policy.

        Args:
            password (str): The password to check.

        Returns:
            Tuple[bool, List[str]]: A tuple containing:
                - bool: True if the password meets the policy, False otherwise.
                - List[str]: A list of issues with the password. Empty if password is valid.
        """
        issues = self._get_password_issues(password)
        return (len(issues) == 0, issues)

    def _get_password_issues(self, password: str) -> List[str]:
        """
        Checks a password against the defined policy and returns a list of issues.

        Args:
            password (str): The password to check.

        Returns:
            List[str]: A list of strings describing the issues with the password.
                       An empty list means the password is valid.
        """
        issues = []

        if not password:
            issues.append('Password cannot be empty.')
            return issues
        
        if len(password) < self.min_length:
            issues.append(f'Password needs to be at least {self.min_length} characters long.')
        if not self.allow_spaces and ' ' in password:
            issues.append('Spaces are not allowed in the password.')

        uppercase_count = len(re.findall(r'[A-Z]', password))
        if uppercase_count < self.min_uppercase:
            issues.append(f'Password needs at least {self.min_uppercase} uppercase characters.')

        lowercase_count = len(re.findall(r'[a-z]', password))
        if lowercase_count < self.min_lowercase:
            issues.append(f'Password needs at least {self.min_lowercase} lowercase characters.')

        digit_count = len(re.findall(r'\d', password))
        if digit_count < self.min_digits:
            issues.append(f'Password needs at least {self.min_digits} numeric digits.')

        special_count = len(re.findall(f'[{re.escape(self.special_chars)}]', password))
        if special_count < self.min_special:
            issues.append(f'Password needs at least {self.min_special} special characters.')

        return issues

    def get_policy_description(self) -> List[str]:
        """
        Returns a list of strings describing the current password policy.
        """
        return [
            f"Minimum length: {self.min_length}",
            f"Minimum uppercase characters: {self.min_uppercase}",
            f"Minimum lowercase characters: {self.min_lowercase}",
            f"Minimum digits: {self.min_digits}",
            f"Minimum special characters: {self.min_special}",
            f"Special characters: {self.special_chars}",
            f"Spaces allowed: {self.allow_spaces}"
        ]
