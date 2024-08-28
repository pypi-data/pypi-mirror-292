import random
import string


class DataGenerator:

    def generate_register_data(self):
        username = self._generate_random_string(8)
        password = self._generate_random_string(12)
        email = f"{username}@gmail.com"
        return {
            'username': username,
            'password': password,
            'email': email
        }

    def generate_other_data(self):
        return {
            'a': self._generate_random_string(5),
            'b': self._generate_random_string(5),
            'c': self._generate_random_string(5),
            'd': self._generate_random_string(5)
        }

    @staticmethod
    def _generate_random_string(length):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
