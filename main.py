import user_panel

from users import Users


def main():
    users = Users()
    users.load_users()

    print("Welcome to Accessible-Look!")

    while True:
        print("\nMain Menu:")
        print("1. Sign-Up")
        print("2. Login")
        print("3. Enter as a guest")

        action = input("Choose your option: ")

        if action == '1':
            print("\nSign-up to the system:")
            username = input("Username: ")
            password = input("Password: ")
            user = users.add_new_user(username, password)
            if user:
                break

        elif action == '2':
            print("\nPlease log-in:")
            username = input("Username: ")
            password = input("Password: ")
            user = users.login(username, password)
            if user:
                break

        elif action == 3:
            # View all businesses as a guest
            pass

        else:
            print("Invalid action, try again. \n")

    user.action_center()


if __name__ == "__main__":
    main()
