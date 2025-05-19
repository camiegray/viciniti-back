from django.http import JsonResponse, HttpResponse

class CorsErrorMiddleware:
    """Middleware to add CORS headers to all responses, including errors."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add CORS headers even for error responses
        if 'Origin' in request.headers:
            response['Access-Control-Allow-Origin'] = request.headers['Origin']
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
            response['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept, Authorization, X-Request-With'
            
            # For OPTIONS requests, return an empty response with CORS headers
            if request.method == 'OPTIONS':
                response = HttpResponse()
                response['Access-Control-Allow-Origin'] = request.headers['Origin']
                response['Access-Control-Allow-Credentials'] = 'true'
                response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
                response['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept, Authorization, X-Request-With'
                response['Content-Length'] = '0'
                return response
            
        return response
        
    def process_exception(self, request, exception):
        """Handle exceptions and still return CORS headers."""
        import traceback
        
        # Log the error
        print(f"ERROR in {request.path}: {str(exception)}")
        traceback.print_exc()
        
        # Return a response with CORS headers
        response = JsonResponse({
            'error': str(exception),
            'detail': traceback.format_exc()
        }, status=500)
        
        # Add CORS headers
        if 'Origin' in request.headers:
            response['Access-Control-Allow-Origin'] = request.headers['Origin']
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
            response['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept, Authorization, X-Request-With'
            
        return response 