using Microsoft.Extensions.Logging;
using TwitchLib.Client;
using TwitchLib.Client.Events;
using TwitchLib.Client.Models;
using TwitchLib.Communication.Clients;
using TwitchLib.Communication.Models;

namespace FENR1R;

public sealed class FENR1RBot
{
    private readonly Config _config;
    private readonly ILogger<FENR1RBot> _logger;
    private readonly TwitchClient _client;
    private readonly PersonalityEngine _personality;
    private readonly MemoryBuffer _memory;
    private readonly SecurityFilter _security;
    private readonly VoiceEngine _voice;
    private readonly KnowledgeManager _knowledge;
    private readonly LearningEngine _learning;
    private readonly MoodEngine _mood;
    private readonly int _cooldown;
    private DateTime _lastResponseTime;

    public FENR1RBot(Config config, ILoggerFactory loggerFactory)
    {
        _config = config;
        _logger = loggerFactory.CreateLogger<FENR1RBot>();
        _knowledge = new KnowledgeManager();
        _learning = new LearningEngine(_knowledge);
        _mood = new MoodEngine();

        var token = Environment.GetEnvironmentVariable("TWITCH_TOKEN") ?? string.Empty;
        var channel = Environment.GetEnvironmentVariable("TWITCH_CHANNEL") ?? string.Empty;

        if (string.IsNullOrWhiteSpace(token))
            throw new InvalidOperationException("TWITCH_TOKEN not set. Please configure .env or environment variables.");
        if (string.IsNullOrWhiteSpace(channel))
            throw new InvalidOperationException("TWITCH_CHANNEL not set. Please configure .env or environment variables.");

        var credentials = new ConnectionCredentials(channel, token);
        var customClient = new WebSocketClient();
        _client = new TwitchClient(customClient);
        _client.Initialize(credentials, channel);

        _client.OnJoinedChannel += OnJoinedChannel;
        _client.OnMessageReceived += OnMessageReceived;
        _client.OnConnectionError += OnConnectionError;

        _personality = new PersonalityEngine(_config, _knowledge, _learning, _mood);
        _memory = new MemoryBuffer(_config.Get<int>("memory_age"));
        _security = new SecurityFilter();
        _voice = new VoiceEngine(_config, _mood, loggerFactory.CreateLogger<VoiceEngine>());
        _cooldown = _config.Get<int>("cooldown");
        _lastResponseTime = DateTime.MinValue;
    }

    public async Task ConnectAsync()
    {
        await _client.ConnectAsync();
    }

    private Task OnJoinedChannel(object? sender, OnJoinedChannelArgs e)
    {
        _logger.LogInformation("Joined channel {Channel}", e.Channel);
        _ = Task.Run(() => _voice.ListenAndRespondAsync(_personality, _memory, _security, _learning, "voice"));
        return Task.CompletedTask;
    }

    private async Task OnMessageReceived(object? sender, OnMessageReceivedArgs e)
    {
        try
        {
            if (e.ChatMessage.IsMe || e.ChatMessage.BotUsername == e.ChatMessage.Username)
                return;

            var priority = CalculatePriority(e.ChatMessage);
            if (priority < 1) return;

            if (DateTime.UtcNow - _lastResponseTime < TimeSpan.FromSeconds(_cooldown)) return;

            var userMessage = e.ChatMessage.Message;
            var memoryContext = _memory.GetRecentContext("chat");
            var badges = e.ChatMessage.Badges != null ? e.ChatMessage.Badges.ToDictionary(kvp => kvp.Key, kvp => kvp.Value.ToString()) : new Dictionary<string, string>();
            _learning.ObserveMessage(e.ChatMessage.Username, userMessage, badges);
            _mood.ObserveChat(e.ChatMessage.Username, userMessage, badges);

            var rawResponse = await _personality.ReplyToChatAsync(userMessage, memoryContext, e.ChatMessage.Username);
            var safeResponse = _security.FilterResponse(rawResponse);
            if (string.IsNullOrWhiteSpace(safeResponse)) return;

            await _client.SendMessageAsync(e.ChatMessage.Channel, safeResponse);
            _logger.LogInformation("Responded to {User}: {Response}", e.ChatMessage.Username, safeResponse);

            _memory.AddMessage("chat", $"User: {userMessage}");
            _memory.AddMessage("chat", $"FENR1R: {safeResponse}");
            _lastResponseTime = DateTime.UtcNow;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing message from Twitch chat.");
        }
    }

    private Task OnConnectionError(object? sender, OnConnectionErrorArgs e)
    {
        _logger.LogError("Twitch connection error: {Error}", e.Error.Message);
        return Task.CompletedTask;
    }

    private int CalculatePriority(TwitchLib.Client.Models.ChatMessage message)
    {
        var content = message.Message.ToLowerInvariant();
        if (content.Contains("fenr1r") || content.Contains("?")) return 3;
        if (message.Bits > 0) return 2;
        if (message.Badges?.Any(b => b.Key == "subscriber") == true) return 2;
        return 0;
    }
}
