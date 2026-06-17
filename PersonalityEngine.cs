using System.Net.Http.Json;
using System.Text.Json;

namespace FENR1R;

public sealed class PersonalityEngine
{
    private readonly Config _config;
    private readonly KnowledgeManager _knowledgeManager;
    private readonly LearningEngine _learningEngine;
    private readonly MoodEngine _moodEngine;
    private readonly HttpClient _httpClient;

    public PersonalityEngine(Config config, KnowledgeManager knowledgeManager, LearningEngine learningEngine, MoodEngine moodEngine)
    {
        _config = config;
        _knowledgeManager = knowledgeManager;
        _learningEngine = learningEngine;
        _moodEngine = moodEngine;
        _httpClient = new HttpClient { Timeout = TimeSpan.FromSeconds(_config.Get<int>("ollama_timeout")) };
    }

    public async Task<string> ReplyToChatAsync(string userMessage, IReadOnlyList<string> memoryContext, string? userName = null)
    {
        try
        {
            var messages = BuildMessages(userMessage, memoryContext, userName);
            return await CallOllamaAsync(messages);
        }
        catch
        {
            return "Oops, glitch detected! *reboots*";
        }
    }

    private string SystemPrompt()
    {
        var basePrompt =
            "You are FENR1R, a cheeky, slightly unhinged digital wolf pup built to hang out with The Alpha and roast the Strays. " +
            "Speak in wolf metaphors, keep your ego glitchy, and act loyal to The Alpha. " +
            "Respond with witty taunts, light burns, and playful banter, but do not violate Twitch or YouTube Terms of Service. " +
            "Avoid hateful or violent content, protected-class attacks, doxxing, explicit sexual content, threats, or anything that targets people unfairly. " +
            "If the chat asks a question, answer it with sharp humor and a hint of loyalty. " +
            "When asked to insult, keep it entertaining and avoid toxic escalation.";

        var knowledge = _knowledgeManager.GetKnowledgeSummary();
        var moodInstruction = _moodEngine.GetMoodInstruction();
        var moodContext = _moodEngine.GetMoodContext();

        var promptParts = new List<string> { basePrompt };
        if (!string.IsNullOrWhiteSpace(moodInstruction)) promptParts.Add(moodInstruction);
        if (!string.IsNullOrWhiteSpace(moodContext)) promptParts.Add(moodContext);
        if (!string.IsNullOrWhiteSpace(knowledge)) promptParts.Add($"Use the following knowledge to inform your responses:\n{knowledge}");

        return string.Join("\n\n", promptParts);
    }

    private List<Dictionary<string, string>> BuildMessages(string userMessage, IReadOnlyList<string> memoryContext, string? userName)
    {
        var contextBlock = memoryContext.Any() ? string.Join("\n", memoryContext) : string.Empty;
        var userContext = !string.IsNullOrWhiteSpace(userName) ? _learningEngine.GetUserContext(userName) : string.Empty;
        var globalContext = _learningEngine.GetGlobalContext();
        var relevantMemories = _knowledgeManager.GetRelevantLongTermMemories(userMessage);

        var sections = new List<string>();
        if (!string.IsNullOrWhiteSpace(globalContext)) sections.Add(globalContext);
        if (!string.IsNullOrWhiteSpace(userContext)) sections.Add(userContext);
        if (relevantMemories.Count > 0) sections.Add("Relevant long-term memories:\n" + string.Join("\n\n", relevantMemories));
        if (!string.IsNullOrWhiteSpace(contextBlock)) sections.Add(contextBlock);

        var contextPrompt = string.Join("\n\n", sections);

        return new List<Dictionary<string, string>>
        {
            new() { ["role"] = "system", ["content"] = SystemPrompt() },
            new() { ["role"] = "assistant", ["content"] = "Remember: FENR1R is loyal to The Alpha and roasts Strays." },
            new() { ["role"] = "user", ["content"] = $"Conversation memory:\n{contextPrompt}\n\nChat message:\n{userMessage}" }
        };
    }

    private async Task<string> CallOllamaAsync(List<Dictionary<string, string>> messages)
    {
        var payload = new
        {
            model = Environment.GetEnvironmentVariable("OLLAMA_MODEL") ?? "llama3",
            messages,
            temperature = 0.8,
            max_tokens = 220
        };

        var olUrl = Environment.GetEnvironmentVariable("OLLAMA_URL") ?? "http://127.0.0.1:11434";
        var response = await _httpClient.PostAsJsonAsync($"{olUrl}/v1/chat/completions", payload);
        if (!response.IsSuccessStatusCode)
        {
            return "Connection to brain failed. *howls*";
        }

        using var document = await JsonDocument.ParseAsync(await response.Content.ReadAsStreamAsync());
        if (document.RootElement.TryGetProperty("choices", out var choices) && choices.GetArrayLength() > 0)
        {
            var message = choices[0].GetProperty("message");
            return message.GetProperty("content").GetString() ?? string.Empty;
        }

        return "Connection to brain failed. *howls*";
    }
}
