class SwayamError(Exception):
    """Base exception for all SWAYAM integration errors."""
    pass

class SwayamAuthenticationError(SwayamError):
    pass

class SwayamAuthorizationError(SwayamError):
    pass

class SwayamValidationError(SwayamError):
    pass

class SwayamNotFoundError(SwayamError):
    pass

class SwayamNotProvisionedError(SwayamError):
    pass

class SwayamInvalidTransitionError(SwayamError):
    pass

class SwayamConfigurationError(SwayamError):
    pass
