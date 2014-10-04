import json
import asyncio
import mimetypes
import functools


class Base:
    def __init__(self, data, *, encoding='utf-8', **kwargs):
        self.data = data
        self.kwargs = kwargs
        self.encoding = encoding

    def serialize(self, request):
        return self.data.encode(self.encoding)


class Json(Base):
    def serialize(self, request):
        request.response.headers.add('Content-Type', 'application/json')
        return json.dumps(self.data).encode(self.encoding)


class Html(Base):
    def serialize(self, request):
        request.response.headers.add('Content-Type', 'text/html')
        return self.data.encode(self.encoding)


class Asset(Base):
    def serialize(self, request):
        content_type = self.kwargs.get('content_type',
                                       mimetypes.guess_type(request.path)[0])
        request.response.headers.add('Content-Type', content_type)
        return self.data


def to(serializer, **serizlizer_kwargs):
    serializer = serializer.title()
    serializer = globals()[serializer]

    def decorator(f):
        @functools.wraps(f)
        @asyncio.coroutine
        def wrapper(*args, **kwargs):
            content = f(*args, **kwargs)
            if asyncio.iscoroutine(content):
                content = (yield from content)
            return serializer(content, **serizlizer_kwargs)

        return wrapper

    return decorator
