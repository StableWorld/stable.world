

class StableWorldError(Exception):
    pass


class UserError(StableWorldError):
    pass


class DuplicateKeyError(UserError):
    pass


class PZError(UserError):
    def log(self):
        print(self.args[0])


class PasswordError(UserError):
    def log(self):
        print('User with the email %s ' % self.args[0])


class ValidationError(UserError):
    def log(self):
        print(self.args[0])
