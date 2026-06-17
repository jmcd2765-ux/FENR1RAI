using System.Text.RegularExpressions;

namespace FENR1R;

public sealed class LongTermMemory
{
    private readonly string _logDir;
    private readonly List<MemoryEntry> _entries = new();

    public LongTermMemory(string logDir = "LongTermMemoryLog")
    {
        _logDir = logDir;
        Directory.CreateDirectory(_logDir);
        LoadAllLogs();
    }

    public void LoadAllLogs()
    {
        _entries.Clear();
        foreach (var filePath in Directory.EnumerateFiles(_logDir, "*.txt"))
        {
            try
            {
                var content = File.ReadAllText(filePath);
                if (!string.IsNullOrWhiteSpace(content))
                {
                    _entries.Add(new MemoryEntry
                    {
                        Filename = Path.GetFileName(filePath),
                        Content = content,
                        Date = ExtractDate(content)
                    });
                }
            }
            catch
            {
                // ignore invalid log files
            }
        }
    }

    public void SaveEntry(string entry, string category = "General")
    {
        var timestamp = DateTime.UtcNow.ToString("yyyyMMdd_HHmmss");
        var filename = $"{timestamp}_{category}_Memory--FENR1R.txt";
        var filepath = Path.Combine(_logDir, filename);
        var content = $"Long-Term Memory Entry: {category}\nDate: {DateTime.UtcNow:yyyy-MM-dd HH:mm:ss}\n\n{entry}\n\nCitation: Auto-saved from chat interaction.";

        File.WriteAllText(filepath, content);
        _entries.Add(new MemoryEntry
        {
            Filename = filename,
            Content = content,
            Date = DateTime.UtcNow.ToString("yyyy-MM-dd")
        });
    }

    public IReadOnlyList<string> GetRelevantMemories(string query, int limit = 5)
    {
        if (string.IsNullOrWhiteSpace(query))
        {
            return Array.Empty<string>();
        }

        var queryTerms = query.Split(' ', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
            .Select(term => term.ToLowerInvariant())
            .ToHashSet();

        var relevant = new List<string>();
        foreach (var entry in _entries)
        {
            var lowerContent = entry.Content.ToLowerInvariant();
            if (queryTerms.Any(term => lowerContent.Contains(term)))
            {
                relevant.Add(entry.Content);
            }

            if (relevant.Count >= limit)
            {
                break;
            }
        }

        return relevant;
    }

    public string GetAllSummaries()
    {
        if (_entries.Count == 0)
        {
            return "No long-term memories available.";
        }

        return string.Join("\n", _entries.Select((entry, index) =>
            $"Memory {index + 1} ({entry.Date}): {entry.Content[..Math.Min(200, entry.Content.Length)]}..."));
    }

    private static string ExtractDate(string content)
    {
        var match = Regex.Match(content, @"^Date:\s*(.+)$", RegexOptions.Multiline);
        return match.Success ? match.Groups[1].Value.Trim() : DateTime.UtcNow.ToString("yyyy-MM-dd");
    }

    private sealed class MemoryEntry
    {
        public string Filename { get; init; } = string.Empty;
        public string Content { get; init; } = string.Empty;
        public string Date { get; init; } = string.Empty;
    }
}
