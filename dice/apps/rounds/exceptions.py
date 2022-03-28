from rest_framework import exceptions, status


class RoundExistsError(exceptions.APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Incomplete round exists, can't create new one"


class FiguresTakenError(exceptions.APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "All figures are taken, can't create new round"


class NotYourRoundError(exceptions.APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Not your round"
