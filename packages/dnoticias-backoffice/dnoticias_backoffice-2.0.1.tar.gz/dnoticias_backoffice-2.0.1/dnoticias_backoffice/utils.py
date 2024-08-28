from django.contrib.auth import get_user_model

User = get_user_model()


def get_acronym(user: User) -> str:
    email = user.email
    name = user.get_full_name()
    to_use = name if len(name) > 2 else email
    to_use = "".join([char for char in to_use if char.isalpha()])
    print("Acronym", user.get_full_name(), user.email, user.first_name, user.last_name)
    return to_use[:2].upper()
