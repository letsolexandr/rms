import os
import mimetypes
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
#from django.utils.http import  urlquote_plus
from urllib.parse import quote as urlquote_plus


def protectedMedia(request):
    if request.user.is_authenticated:
        ## TODO додати перевірку організації до якої відноситься користувач
        response = HttpResponse()
        mimetype, encoding = mimetypes.guess_type(request.path)
        protected_pass = urlquote_plus(request.path.replace('media','protected-files'))
        filename = os.path.basename(request.path)
        response['X-Accel-Redirect'] = protected_pass
        response["Content-Type"] = mimetype
        if encoding:
            response["Content-Encoding"] = encoding
        ##response['Content-Disposition'] = 'attachment; filename="' + filename + '"'
        del response['Content-Type']
        del response['Accept-Ranges']
        del response['Set-Cookie']
        del response['Cache-Control']
        del response['Expires']
        return response
    else:
        raise PermissionDenied()