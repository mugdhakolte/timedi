# from rest_framework.views import exception_handler
#
#
# def custom_exception_handler(exc, context):
#     response = exception_handler(exc, context)
#     if response is not None and isinstance(response.data, dict):
#         custom_data = {'data': response.data}
#         custom_data['data']["message"] = 'Please correct the errors below'
#         response.data = custom_data
#     return response
