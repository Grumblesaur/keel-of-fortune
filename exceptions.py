class RandomizerError(Exception):
    pass


class RegistrationError(RandomizerError):
    pass


class UploadError(RegistrationError):
    pass


class UnrecognizedFileType(UploadError):
    pass


class UnrecognizedShips(RegistrationError):
    pass


class UnrecognizedUsers(RegistrationError):
    pass


class SpamError(RegistrationError):
    pass


class DivisionError(RandomizerError):
    pass


class ImproperSize(DivisionError):
    pass


class ImproperTier(RandomizerError):
    pass


class ImproperType(RandomizerError):
    pass


class ImproperNation(RandomizerError):
    pass


class UnrecognizedNation(RandomizerError):
    pass


class NoShips(RandomizerError):
    pass