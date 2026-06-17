using System.Text.Json;

namespace FENR1R;

public sealed class Config
{
    private readonly Dictionary<string, object> _settings = new();
    private readonly Dictionary<string, object> _defaults = new()
    {
        ["memory_age"] = 600,
        ["cooldown"] = 10,
        ["voice_rate"] = 180,
        ["voice_volume"] = 0.9,
        ["voice_pitch"] = 0,
        ["ollama_timeout"] = 20,
        ["audio_duration"] = 3,
        ["vts_port"] = 9000,
        ["log_level"] = "Information"
    };

    public string ConfigFilePath { get; }

    private Config(string configFilePath)
    {
        ConfigFilePath = configFilePath;
    }

    public static Config Load(string configFilePath)
    {
        var config = new Config(configFilePath);
        if (File.Exists(configFilePath))
        {
            var text = File.ReadAllText(configFilePath);
            try
            {
                var parsed = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(text);
                if (parsed is not null)
                {
                    foreach (var kvp in parsed)
                    {
                        config._settings[kvp.Key] = DeserializeJsonElement(kvp.Value);
                    }
                }
            }
            catch
            {
                config._settings.Clear();
            }
        }

        foreach (var kvp in config._defaults)
        {
            if (!config._settings.ContainsKey(kvp.Key))
            {
                config._settings[kvp.Key] = kvp.Value;
            }
        }

        if (!File.Exists(configFilePath))
        {
            config.Save();
        }

        return config;
    }

    public void Save()
    {
        var json = JsonSerializer.Serialize(_settings, new JsonSerializerOptions { WriteIndented = true });
        File.WriteAllText(ConfigFilePath, json);
    }

    public T Get<T>(string key)
    {
        if (_settings.TryGetValue(key, out var value))
        {
            return value switch
            {
                T typed => typed,
                JsonElement element => DeserializeJsonElement(element) is T casted ? casted : default!,
                _ => value is IConvertible convertible ? (T)Convert.ChangeType(convertible, typeof(T)) : default!
            };
        }

        if (_defaults.TryGetValue(key, out var defaultValue) && defaultValue is T defaultTyped)
        {
            return defaultTyped;
        }

        return default!;
    }

    public void Set(string key, object value)
    {
        _settings[key] = value;
        Save();
    }

    private static object DeserializeJsonElement(JsonElement element)
    {
        return element.ValueKind switch
        {
            JsonValueKind.String => element.GetString() ?? string.Empty,
            JsonValueKind.Number => element.TryGetInt64(out var longValue) ? longValue : element.GetDouble(),
            JsonValueKind.True => true,
            JsonValueKind.False => false,
            _ => element.ToString() ?? string.Empty
        };
    }
}
