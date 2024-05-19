class Users:
    def __init__(self):
        self.users_dict = {}

    def add_new_user(self, username, password):
        self.validate_new_user(username, password)
        user = User(username, password)
        self.users_dict[username] = user
        print(f"User {username} has been created successfully!")

    def login(self, username, password):
        user = self.users_dict.get(username)
        if user and user.validate_password(password):
            print("Credentials were validated. Proceeding...")
            return user
        print("Credentials are wrong.")
        return False

    @staticmethod
    def validate_new_user(username, password):
        pass


class User:
    def __init__(self, username, password):
        self.username = username
        self.__password = password
        self.places = {}
        self.final_result = ''

    def add_place(self, place, photos, response):
        self.places[place] = {}
        self.places[place]['images'] = photos
        self.places[place]['response'] = response

    def validate_password(self, password):
        return self.__password == password

    def produce_final_result(self):
        pass

    def print_results(self):
        pass


# TODO - Add new user

# TODO - Use external DB
# TODO - Add web
