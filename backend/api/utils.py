from rest_framework.response import Response
from rest_framework import status

def standard_response(code, data=None, success=True, status_code=status.HTTP_200_OK, message=None):
    """
    Standardizes API responses.
    
    Args:
        code (str): The Message Code (api.codes).
        data (dict, optional): The data payload. Defaults to None.
        success (bool): Success status. Defaults to True.
        status_code (int): HTTP status code. Defaults to 200.
        message (str, optional): Optional debug message (should generally be avoided in prod favor of codes).
    """
    response_data = {
        "status": "success" if success else "error",
        "code": code,
        "data": data if data is not None else {}
    }
    
    if message:
        response_data['message'] = message
        
    return Response(response_data, status=status_code)
