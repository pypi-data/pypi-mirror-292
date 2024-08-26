class MiError(Exception):
    pass

class HTTPError(Exception):
    pass

class MisskeyAPIError(MiError):
    pass

class ClientException(MiError):
    pass

class ParseError(Exception):
    pass

class NotExtensionError(Exception):
    pass

class RegistedError(Exception):
    pass

class AlreadyRegisted(RegistedError):
    pass

class NotFound(HTTPError):
    pass

class MiAuthFailed(NotFound):
    pass

class AuthFailed(MisskeyAPIError):
    pass