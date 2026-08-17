class RandomizerError(Exception):
    pass


class RegistrationError(RandomizerError):
    pass


class UnrecognizedShips(RegistrationError):
    pass


class SpamError(RegistrationError):
    pass


class DivisionError(RandomizerError):
    pass

class ImproperSize(DivisionError):
    pass