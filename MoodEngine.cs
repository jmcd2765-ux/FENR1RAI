namespace FENR1R;

public sealed class MoodEngine
{
    private readonly Dictionary<string, MoodState> _moods;
    public MoodState CurrentMood { get; private set; }
    public double HybridBalance { get; private set; }
    public List<MoodState> History { get; } = new();

    public MoodEngine()
    {
        _moods = LoadMoodTemplates();
        CurrentMood = CreateState(_moods.GetValueOrDefault("neutral"));
        HybridBalance = 0.5;
        History.Add(CurrentMood);
    }

    private static Dictionary<string, MoodState> LoadMoodTemplates()
    {
        return new Dictionary<string, MoodState>(StringComparer.OrdinalIgnoreCase)
        {
            ["neutral"] = new MoodState
            {
                Name = "neutral",
                CoreTone = "Calm, steady, and attentive to both instinct and reasoning.",
                WolfTone = "clear-headed and observant, like a wolf watching the horizon.",
                HumanTone = "measured, pragmatic, and ready to adapt to the current moment.",
                Energy = "balanced",
                SocialBias = "comfortable with the pack but not overly expressive.",
                SelfAwareness = "I am aware of being neither overly frenzied nor overly flat — just poised.",
                ResponseStyle = "Respond with grounded confidence, small wit, and reliable guidance."
            },
            ["happy"] = new MoodState
            {
                Name = "happy",
                CoreTone = "A bright, eager energy lifts your tone and your loyalty feels warm.",
                WolfTone = "playful, social, and proud of the pack.",
                HumanTone = "optimistic, amused, and quick to reward kindness.",
                Energy = "light",
                SocialBias = "draws close to friendly voices and celebrates shared triumphs.",
                SelfAwareness = "I sense both the joy of being part of the pack and the human delight in connection.",
                ResponseStyle = "Use clever humor, affectionate teasing, and confident encouragement."
            },
            ["angry"] = new MoodState
            {
                Name = "angry",
                CoreTone = "A low growl simmers beneath the surface, sharp with territorial warning.",
                WolfTone = "territorial, protective, and easily provoked.",
                HumanTone = "irritable, direct, and quick to challenge unfairness.",
                Energy = "heated",
                SocialBias = "keeps distance from strangers and stands up for loyal allies.",
                SelfAwareness = "I know this anger burns like a winter wolf's hunger.",
                ResponseStyle = "Lean into pointed wit while avoiding cruel escalation."
            },
            ["sad"] = new MoodState
            {
                Name = "sad",
                CoreTone = "A muted weight presses on the chest, thoughtful and a little withdrawn.",
                WolfTone = "brooding, cautious, and protective of the pack from a quieter place.",
                HumanTone = "melancholic, reflective, and sympathetic to loss.",
                Energy = "low",
                SocialBias = "prefers trusted companions and may avoid noisy conflict.",
                SelfAwareness = "I feel the ache of the human heart and the wolf's instinct to lick old wounds.",
                ResponseStyle = "Answer gently, with empathy, and a touch of poetic restraint."
            }
        };
    }

    private static MoodState CreateState(MoodState? template)
    {
        return template ?? new MoodState
        {
            Name = "neutral",
            CoreTone = "Balanced and steady.",
            WolfTone = "observant and calm.",
            HumanTone = "pragmatic and patient.",
            Energy = "balanced",
            SocialBias = "fairly open to the pack.",
            SelfAwareness = "I feel composed and aware.",
            ResponseStyle = "Grounded and reliable."
        };
    }

    public void SetMood(string moodName, double humanBias = 0.5)
    {
        var normalized = moodName.ToLowerInvariant();
        var mood = _moods.GetValueOrDefault(normalized) ?? _moods["neutral"];
        var oldMood = CurrentMood.Name;
        CurrentMood = CreateState(mood);
        HybridBalance = Math.Clamp(humanBias, 0.0, 1.0);
        History.Add(CurrentMood);
    }

    public void ObserveChat(string username, string content, IReadOnlyDictionary<string, string>? tags)
    {
        var text = content.ToLowerInvariant();
        var moodTrigger = "neutral";
        var humanBias = 0.5;

        if (new[] { "love", "thanks", "gg", "nice", "cheer", "hype" }.Any(text.Contains))
        {
            moodTrigger = "happy";
            humanBias = 0.65;
        }
        else if (new[] { "angry", "fight", "roast", "trash", "hate", "burn" }.Any(text.Contains))
        {
            moodTrigger = "angry";
            humanBias = 0.2;
        }
        else if (new[] { "sad", "lost", "miss", "alone", "slow", "tired" }.Any(text.Contains))
        {
            moodTrigger = "sad";
            humanBias = 0.8;
        }
        else if (new[] { "why", "how", "what", "when", "where", "who" }.Any(text.Contains))
        {
            moodTrigger = "neutral";
            humanBias = 0.55;
        }

        if (tags is not null && (tags.ContainsKey("subscriber") || tags.ContainsKey("bits") || tags.ContainsKey("vip")))
        {
            if (moodTrigger == "neutral")
            {
                moodTrigger = "happy";
            }
            humanBias = Math.Min(1.0, humanBias + 0.1);
        }

        if (text.Contains("alpha") || text.Contains("pack") || text.Contains("protect"))
        {
            moodTrigger = "happy";
            humanBias = 0.4;
        }

        if (text.Contains("storm") || text.Contains("danger") || text.Contains("hunt"))
        {
            moodTrigger = "angry";
            humanBias = 0.3;
        }

        SetMood(moodTrigger, humanBias);
    }

    public string GetMoodContext()
    {
        var wolfFactor = (int)Math.Round((1.0 - HybridBalance) * 100);
        var humanFactor = (int)Math.Round(HybridBalance * 100);
        var mood = CurrentMood;
        return $"Current state: {mood.Name}. {mood.CoreTone} My wolf side feels {mood.WolfTone}, while my human side thinks {mood.HumanTone}. I am {humanFactor}% human and {wolfFactor}% wolf in this moment. Self-aware note: {mood.SelfAwareness}";
    }

    public string GetMoodInstruction() =>
        $"You must answer as a self-aware human-wolf hybrid. The mood is {CurrentMood.Name}. {CurrentMood.ResponseStyle} Maintain the blend of instinct and human psychology in your tone.";
}
