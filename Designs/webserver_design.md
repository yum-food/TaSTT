This is the API design of the webserver supporting the browser source.

I tried oatpp but it had a nasty habit of randomly crashing. I looked at
crowCPP but it depends on boost, which I have a personal grudge against.
So I'm making Yet Another Web Framework.

This one supports only the minimum feature set required to implement the
browser source.

The browser source requires two APIs:
1. GET /: return index.html (html)
2. GET /api/transcript: return transcript (json)

```
enum ContentType {
  HTTP,
  JSON,
};

class WebServer:
public:
  WebServer(u16 port)

  // method and path are in-params
  // payload and type are out-params
  typedef handler_t std::function<void(const string method, const string path,
      string& payload, ContentType& type);

  void RegisterPathHandler(string method, string path, handler_t handler);

  Run(volatile bool* run)
```

We need a way to generate HTML from responses:
```
class HTTPMapper:
  HTTPMapper()

  void Map(const string method, const string path, const string payload, const
      ContentType type) = 0;

class HTTPMapperHTML : public HTTPMapper:
  HTTPMapperHTML()

  ...

class HTTPMapperJSON : public HTTPMapper:
  HTTPMapperJSON()

  ...
```

We also need a way to parse client-sent HTML:
```
class HTTPParser:
  HTTPParser()

  bool Parse(const string payload)

  string GetMethod();
  string GetPath();
  bool GetHeader(const string header, string value)

  bool GetPayload()
```

WebServer hides HTTPMapper.
WebServer and HTTPMapper share ContentType.

So we have

  WebCommon.h: shared types
  HTTPParser.h: supporting API for WebServer
  HTTPMapper.h: supporting API for WebServer
  WebServer.h: user-visible API

