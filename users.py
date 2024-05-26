import pickle

from user_panel import User

USERS_DB = 'db/users.pkl'


class Users:
    def __init__(self):
        self.users_dict = {}

    def add_new_user(self, username, password):
        if not self.validate_new_user(username, password):
            return
        user = User(username, password)
        self.users_dict[username] = user
        print(f"User {username} has been created successfully!")
        self.save_users()

    def login(self, username, password):
        user = self.users_dict.get(username)
        if user and user.validate_password(password):
            print("Credentials were validated. Proceeding...")
            return user
        print("Credentials are wrong.")
        return False

    def load_users(self):
        try:
            with open(USERS_DB, 'rb') as file:
                users = pickle.load(file)
                self.users_dict = users
        except Exception as e:
            print(f"An error occurred while loading the users pickle file: {e}")

    def save_users(self):
        try:
            with open(USERS_DB, 'wb') as file:
                pickle.dump(self.users_dict, file)
        except Exception as e:
            print(f"An error occurred while saving the users pickle file: {e}")

    @staticmethod
    def validate_new_user(username, password):
        return True
