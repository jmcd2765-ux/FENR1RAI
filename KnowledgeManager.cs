namespace FENR1R;

public sealed class KnowledgeManager
{
    private readonly string _knowledgeDir;
    private readonly LongTermMemory _longTermMemory;

    public KnowledgeManager(string knowledgeDir = "knowledge")
    {
        _knowledgeDir = knowledgeDir;
        Directory.CreateDirectory(_knowledgeDir);
        _longTermMemory = new LongTermMemory();
    }

    public Dictionary<string, string> LoadAll()
    {
        var documents = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        foreach (var filePath in Directory.EnumerateFiles(_knowledgeDir, "*.txt"))
        {
            try
            {
                var content = File.ReadAllText(filePath);
                documents[Path.GetFileNameWithoutExtension(filePath)] = content.Trim();
            }
            catch
            {
                documents[Path.GetFileNameWithoutExtension(filePath)] = string.Empty;
            }
        }

        return documents;
    }

    public string GetKnowledgeSummary()
    {
        var documents = LoadAll();
        var lines = documents
            .Where(kvp => !string.IsNullOrWhiteSpace(kvp.Value))
            .Select(kvp => $"Knowledge section: {kvp.Key}\n{kvp.Value}");

        var ltmSummary = _longTermMemory.GetAllSummaries();
        if (!string.IsNullOrWhiteSpace(ltmSummary))
        {
            lines = lines.Append($"Long-Term Memory:\n{ltmSummary}");
        }

        return string.Join("\n\n", lines);
    }

    public void SaveLongTermMemory(string entry, string category = "General")
    {
        _longTermMemory.SaveEntry(entry, category);
    }

    public IReadOnlyList<string> GetRelevantLongTermMemories(string query, int limit = 5)
    {
        return _longTermMemory.GetRelevantMemories(query, limit);
    }
}
