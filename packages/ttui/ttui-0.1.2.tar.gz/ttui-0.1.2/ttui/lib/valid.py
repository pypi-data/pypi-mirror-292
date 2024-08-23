from textual.validation import Function, Number, ValidationResult, Validator
import os


# A custom validator
class FileValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        """Check a string is equal to its reverse."""
        if len(value) == 0:
            self.failure("no input")

        if self.is_file(value):
            return self.success()
        else:
            return self.failure("That's not a palindrome :/")

    @staticmethod
    def is_file(value: str) -> bool:
        return os.path.exists(value)

