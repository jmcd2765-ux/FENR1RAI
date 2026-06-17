namespace FENR1R;

public sealed class MoodState
{
    public string Name { get; init; } = string.Empty;
    public string CoreTone { get; init; } = string.Empty;
    public string WolfTone { get; init; } = string.Empty;
    public string HumanTone { get; init; } = string.Empty;
    public string Energy { get; init; } = string.Empty;
    public string SocialBias { get; init; } = string.Empty;
    public string SelfAwareness { get; init; } = string.Empty;
    public string ResponseStyle { get; init; } = string.Empty;

    public string Summary() =>
        $"Mood: {Name}. {CoreTone} Wolf instinct: {WolfTone}. Human mind: {HumanTone}. Energy is {Energy}, social bias is {SocialBias}. Aware note: {SelfAwareness}";
}
