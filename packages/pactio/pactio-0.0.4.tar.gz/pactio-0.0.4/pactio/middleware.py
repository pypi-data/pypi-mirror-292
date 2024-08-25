from pactio.decorators import pactio


class PactioMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        return pactio(view_func)(request, *view_args, **view_kwargs)
