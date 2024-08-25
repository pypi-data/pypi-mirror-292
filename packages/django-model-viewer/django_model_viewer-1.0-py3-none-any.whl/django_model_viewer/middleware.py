class AppendApplication:
    def __init__(self, get_response):
        print(f'Package init: {get_response}')
        self.get_response = get_response

    def __call__(self, request):
        print(f'Package request: {request}')
        response = self.get_response(request)
        return response