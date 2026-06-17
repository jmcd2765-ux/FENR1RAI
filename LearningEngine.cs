using System.Text.RegularExpressions;

namespace FENR1R;

public sealed class LearningEngine
{
    private static readonly string[] GameTerms =
    {
        "valorant", "league of legends", "fortnite", "apex", "minecraft", "elden ring",
        "overwatch", "dota", "call of duty", "warcraft", "pokemon", "zelda", "hades",
        "cyberpunk", "skyrim", "among us", "roblox", "gta", "fall guys"
    };

    private readonly Dictionary<string, UserProfile> _users = new(StringComparer.OrdinalIgnoreCase);
    private readonly Dictionary<string, int> _globalTopics = new(StringComparer.OrdinalIgnoreCase);
    private readonly KnowledgeManager? _knowledgeManager;

    public LearningEngine(KnowledgeManager? knowledgeManager = null)
    {
        _knowledgeManager = knowledgeManager;
    }

    public void ObserveMessage(string username, string content, IReadOnlyDictionary<string, string>? tags)
    {
        var profile = _users.GetValueOrDefault(username) ?? new UserProfile();
        profile.Messages.Add(content);

        if (tags is not null)
        {
            if (tags.ContainsKey("subscriber"))
            {
                profile.LoyaltyScore += 2;
                profile.Tags.Add("subscriber");
            }
            if (tags.ContainsKey("bits"))
            {
                profile.LoyaltyScore += 1;
                profile.Tags.Add("bits");
            }
            if (tags.ContainsKey("vip"))
            {
                profile.Tags.Add("vip");
            }
        }

        var foundGames = ExtractGames(content);
        foreach (var game in foundGames)
        {
            profile.FavoriteGames.Add(game);
            _globalTopics[game] = _globalTopics.GetValueOrDefault(game) + 1;
        }

        var topics = ExtractTopics(content);
        profile.RecentTopics.AddRange(topics);
        foreach (var topic in topics)
        {
            _globalTopics[topic] = _globalTopics.GetValueOrDefault(topic) + 1;
        }

        _users[username] = profile;
        AutoSaveImportantKnowledge(username, content, tags);
    }

    public string GetUserContext(string username)
    {
        if (!_users.TryGetValue(username, out var profile))
        {
            return string.Empty;
        }

        var games = profile.FavoriteGames.Count > 0 ? string.Join(", ", profile.FavoriteGames.OrderBy(x => x)) : "none yet";
        var tags = profile.Tags.Count > 0 ? string.Join(", ", profile.Tags.OrderBy(x => x)) : "no special tags";
        var recent = profile.RecentTopics.Count > 0 ? string.Join("; ", profile.RecentTopics.TakeLast(5)) : "no recent topics";
        return $"User summary for {username}: favorite games: {games}. Loyalty score: {profile.LoyaltyScore}. Tags: {tags}. Recent topics: {recent}.";
    }

    public string GetGlobalContext()
    {
        if (_globalTopics.Count == 0)
        {
            return string.Empty;
        }

        var sorted = _globalTopics.OrderByDescending(kvp => kvp.Value).Take(8);
        var top = string.Join(", ", sorted.Select(kvp => $"{kvp.Key}({kvp.Value})"));
        return $"Trending chat topics and games: {top}.";
    }

    private void AutoSaveImportantKnowledge(string username, string content, IReadOnlyDictionary<string, string>? tags)
    {
        if (_knowledgeManager is null)
        {
            return;
        }

        var profile = _users[username];
        if (profile.LoyaltyScore > 5 && ExtractGames(content).Any())
        {
            var entry = $"User {username} (loyalty: {profile.LoyaltyScore}) shared: '{content}'";
            _knowledgeManager.SaveLongTermMemory(entry, "User_Insights");
        }

        foreach (var topic in _globalTopics)
        {
            if (topic.Value >= 10 && !profile.SavedTopics.Contains(topic.Key))
            {
                profile.SavedTopics.Add(topic.Key);
                var entry = $"Trending topic '{topic.Key}' mentioned {topic.Value} times in chat.";
                _knowledgeManager.SaveLongTermMemory(entry, "Trending_Topics");
            }
        }

        if (new[] { "learn", "remember", "fact", "tip", "guide" }.Any(word => content.Contains(word, StringComparison.OrdinalIgnoreCase)))
        {
            var entry = $"Knowledge from {username}: {content}";
            _knowledgeManager.SaveLongTermMemory(entry, "Learned_Facts");
        }
    }

    private static IReadOnlyCollection<string> ExtractGames(string content)
    {
        var text = content.ToLowerInvariant();
        return GameTerms.Where(term => text.Contains(term)).ToList();
    }

    private static IReadOnlyCollection<string> ExtractTopics(string content)
    {
        var words = Regex.Matches(content.ToLowerInvariant(), "[a-z0-9']+")
            .Select(match => match.Value)
            .Where(word => word.Length > 4)
            .ToList();
        return words.TakeLast(5).ToList();
    }

    private sealed class UserProfile
    {
        public List<string> Messages { get; } = new();
        public HashSet<string> FavoriteGames { get; } = new(StringComparer.OrdinalIgnoreCase);
        public int LoyaltyScore { get; set; }
        public HashSet<string> Tags { get; } = new(StringComparer.OrdinalIgnoreCase);
        public List<string> RecentTopics { get; } = new();
        public HashSet<string> SavedTopics { get; } = new(StringComparer.OrdinalIgnoreCase);
    }
}
