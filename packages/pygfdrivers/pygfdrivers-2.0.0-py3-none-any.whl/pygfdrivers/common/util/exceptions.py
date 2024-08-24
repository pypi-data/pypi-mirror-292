class CommandNotSupportedError(Exception):
    """
    Exception raised when a command is not supported. Note that exception classes can be empty.
    """
    pass


class GeneralExceptions:
    class NotSupportedError(Exception):
        pass


class DeviceExceptions:
    class DeviceNotSupportedError(Exception):
        pass


class CommandClassExceptions:
    class CommandNotSupportedError(Exception):
        pass

    class CommandError(Exception):
        pass

    class CommandArgsError(Exception):
        pass

    class CommandDefaultError(Exception):
        pass


class SettingExceptions:
    class SettingOptionError(Exception):
        def __init__(self, setting, valid_options) -> None:
            message = f"Setting '{setting}' is not in valid options: {valid_options}."
            super().__init__(message)

    class SettingRangeError(Exception):
        def __init__(self, setting, max_value, min_value) -> None:
            message = f"Setting '{setting}' is out of the valid range [{min_value}, {max_value}]."
            super().__init__(message)
