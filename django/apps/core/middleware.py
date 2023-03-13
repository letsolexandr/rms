import json
from django.utils.deprecation import MiddlewareMixin
# from pycallgraph import Config
# from pycallgraph import PyCallGraph
# from pycallgraph.globbing_filter import GlobbingFilter
# from pycallgraph.output import GraphvizOutput
import time
from django.conf import settings
from django.contrib.messages.middleware import MessageMiddleware

from rest_framework.renderers import JSONRenderer


class CustomRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        res = {

            'msg': 'dsadasdasdsad',
            'data': data,
        }
        return super().render(res, accepted_media_type, renderer_context)

class DeserializeJson(MiddlewareMixin):
    def process_request(self, request):
        ##l =dir(request.POST)
        in_data = request.POST
        request.POST._mutable = True
        for key in request.POST.keys():
            value = request.POST.get(key)
            if type(value) == str:
                try:
                    value_json = json.loads(value)
                    setattr(request, key, value_json)
                except Exception as e:
                    pass
        out_data = request.POST
        ##aise Exception 


# class PyCallGraphMiddleware(MiddlewareMixin):
#     VALID_OUTPUT_TYPE = ['png', 'dot', 'pdf', 'json']
#     DEFAULT_EXCLUDE = ['*.__unicode__', '*.__str__']

#     def process_view(self, request, callback, callback_args, callback_kwargs):
#         """Створює візуальну діаграму проходження запиту, та виклику функційта методів
#         Параметри вказуються в адресному рядку, наприклад:
#         /someview?graph=app.docugroups=true
#         Детальний опис:
#         -   https://graphviz.org/
#         -   https://pycallgraph.readthedocs.io/en/develop/guide/command_line_usage.html
#         Параметри:
#         graph - перелік модулів,які будуть всклюсені у фінальну візуалізацію, наприклад:
#         graph=document.*,django.core.* -
#         exclude_extra - перелік модулів які необхідно виключити з візуальзації
#         groups - групувати за модулями
#         graph_output - формат вихідного файло, за замовчуванням - png
#         """
#         if settings.DEBUG and 'graph' in request.GET:
#             visualize_modules = request.GET['graph'].split(',')
#             exclude_extra = request.GET.get('exclude_extra', '').split(',')
#             exclude = PyCallGraphMiddleware.DEFAULT_EXCLUDE + exclude_extra
#             graph_output = request.GET.get('graph_output', 'png')
#             groups = request.GET.get('groups', False)
#             max_depth = int(request.GET.get('max_depth', 99999))
#             tool = request.GET.get('tool', 'dot')
#             ## Roadmap

#             if graph_output not in PyCallGraphMiddleware.VALID_OUTPUT_TYPE:
#                 raise Exception(f'"{graph_output}" not in "{PyCallGraphMiddleware.VALID_OUTPUT_TYPE}"')

#             output_file = 'pycallgraph-{}-{}.{}'.format(time.time(), tool, graph_output)

#             output = GraphvizOutput(output_file=output_file, tool=tool, output_type=graph_output)

#             config = Config(groups=groups, max_depth=max_depth)
#             config.trace_filter = GlobbingFilter(include=visualize_modules, exclude=exclude)

#             pycallgraph = PyCallGraph(output=output, config=config)
#             pycallgraph.start()

#             self.pycallgraph = pycallgraph

#     def process_response(self, request, response):
#         if settings.DEBUG and 'graph' in request.GET and hasattr(self, 'pycallgraph'):
#             self.pycallgraph.done()

#         return response


from django.core.exceptions import RequestDataTooBig
from .exceptions import ToLargeFileException
from django.conf import settings



class CheckUploadFileSize(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        return response

    def process_exception(self, request, exception):
        if isinstance(exception, RequestDataTooBig):
            raise ToLargeFileException( 
                f'Розмір завантаженого файлу перевищує встановлений ліміт в {settings.DATA_UPLOAD_MAX_MEMORY_SIZE / 1024} mb')


class CustomMessageMiddleware(MessageMiddleware):
    # def __init__(self, get_response):
    #     self.get_response = get_response
    #
    # def __call__(self, request):
    #     response = self.get_response(request)
    #     if hasattr(response, 'data'):
    #         response.data.update({'info_messages': 'dsadasdasdasdasdadsa'})
    #     return response

    def process_response(self, request, response):
        """
        Update the storage backend (i.e., save the messages).

        Raise ValueError if not all messages could be stored and DEBUG is True.
        """
        # A higher middleware layer may return a request which does not contain
        # messages storage, so make no assumption that it will be there.
        if hasattr(response, 'data'):
            response.data.update({'info_messages': 'dsadasdasdasdasdadsa'})
            print(response.data)
            response._is_rendered = False
            response.render()
            # response['Age-X-data'] = 'dsadasdas'
        return response
