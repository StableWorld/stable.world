

class StableWorldError(Exception):
    def __init__(self, message, payload=None):
        Exception.__init__(self, message)
        self.payload = payload
        self.message = message


class UserError(StableWorldError):
    pass


class NotFound(UserError):
    pass


class HTTPException(UserError):

    @property
    def path(self):
        return self.payload.get('path') if self.payload else None

    @property
    def method(self):
        return self.payload.get('method', 'GET') if self.payload else 'GET'

    @property
    def quick_path(self):
        return '[%s] %s' % (self.method, self.path)

    def __str__(self):
        if self.path:
            return '%s (%s)' % (self.message, self.quick_path)
        else:
            return '%s' % self.message


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
