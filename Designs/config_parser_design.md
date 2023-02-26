RYML has decided to stop working and I don't want to spend any more time trying
to figure out why.

Let's make a parser that implements the small subset of YAML that
Config.{h,cpp} rely on.

Config needs to serialize the following types:

* std::string
* bool
* int

Bool will be serialized like ints, with additional requirements on
deserialization.

Serialization looks like this:
```
ConfigMarshall cm(out_);
cm.Append("microphone", microphone_);  // string
cm.Append("rows", rows_);              // int
cm.Append("use_cpu", use_cpu_);        // bool
cm.Write("config.yml");
```

Deserialization looks like this:
```
ConfigMarshall cm(out_);
cm.Load("config.yml");
cm.Get("microphone", microphone_);  // string
cm.Get("rows", rows_);              // int
cm.Get("use_cpu", use_cpu_);        // bool
```

Interface:
```
class ConfigMarshal {
public:
  ConfigMarshall(wxTextCtrl *out);

  bool Save(const std::filesystem::path& path);
  bool Load(const std::filesystem::path& path);

  template <typename T>
  bool Append(const std::string& key, const T& value);

  template <typename T>
  bool Get(const std::string& key, T& value);

private:
  std::map<std::string, std::string> kv_str_;
  std::map<std::string, int> kv_int_;
  std::map<std::string, bool> kv_bool_;
}
```

