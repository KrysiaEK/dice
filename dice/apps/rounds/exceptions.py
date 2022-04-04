from rest_framework import exceptions, status


class RoundExistsError(exceptions.APIException):
    """Ensure http 409 is returned, when incomplete round exists."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = "Incomplete round exists, can't create new one"


class FiguresTakenError(exceptions.APIException):
    """Ensure http 409 is returned, when all figures are taken. """

    status_code = status.HTTP_409_CONFLICT
    default_detail = "All figures are taken, can't create new round"


class NotYourRoundError(exceptions.APIException):
    """Ensure http 409 is returned, when it isn't player's round. """

    status_code = status.HTTP_409_CONFLICT
    default_detail = "Not your round"
