using System.Diagnostics;
using Microsoft.Extensions.Logging;
using Vizcon.OSC;

namespace FENR1R;

public sealed class VoiceEngine
{
    private readonly Config _config;
    private readonly MoodEngine _moodEngine;
    private readonly ILogger<VoiceEngine> _logger;
    private readonly UDPSender _udpSender;
    private readonly string? _ttsCommand;

    public VoiceEngine(Config config, MoodEngine moodEngine, ILogger<VoiceEngine> logger)
    {
        _config = config;
        _moodEngine = moodEngine;
        _logger = logger;

        _udpSender = new UDPSender("127.0.0.1", _config.Get<int>("vts_port"));
        _ttsCommand = DetectEspeak();
    }

    private static string? DetectEspeak()
    {
        try
        {
            using var process = new Process
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = "espeak",
                    Arguments = "--version",
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                }
            };

            process.Start();
            process.WaitForExit(2000);
            return process.ExitCode == 0 ? "espeak" : null;
        }
        catch
        {
            return null;
        }
    }

    public void Speak(string text)
    {
        if (string.IsNullOrWhiteSpace(text))
        {
            return;
        }

        try
        {
            var moodRate = _moodEngine.CurrentMood.Energy switch
            {
                "heated" => 20,
                "low" => -10,
                _ => 0
            };
            var rate = _config.Get<int>("voice_rate") + moodRate;
            rate = Math.Clamp(rate, 80, 300);

            if (!string.IsNullOrWhiteSpace(_ttsCommand))
            {
                var args = $"-s {rate} \"{text.Replace("\"", "\\\"")}\"";
                using var process = new Process
                {
                    StartInfo = new ProcessStartInfo
                    {
                        FileName = _ttsCommand,
                        Arguments = args,
                        RedirectStandardOutput = false,
                        RedirectStandardError = false,
                        UseShellExecute = false,
                        CreateNoWindow = true
                    }
                };

                process.Start();
                process.WaitForExit();
                _logger.LogInformation("Spoken text via espeak.");
            }
            else
            {
                _logger.LogWarning("No TTS engine detected. Install espeak to enable voice output.");
            }

            SendToVTube(text);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error speaking text.");
        }
    }

    private void SendToVTube(string text)
    {
        try
        {
            var message = new OscMessage("/chatbox/input", new object[] { text, true });
            _udpSender.Send(message);
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Failed to send OSC message to VTube Studio.");
        }
    }

    public async Task ListenAndRespondAsync(PersonalityEngine personalityEngine, MemoryBuffer memory, SecurityFilter security, LearningEngine learning, string source = "voice")
    {
        _logger.LogInformation("Voice listen-and-respond is not fully implemented in this C# port.");
        var sttUrl = Environment.GetEnvironmentVariable("WHISPERX_URL");
        if (string.IsNullOrWhiteSpace(sttUrl))
        {
            _logger.LogInformation("Speech-to-text is disabled because WHISPERX_URL is not configured.");
            return;
        }

        while (true)
        {
            await Task.Delay(TimeSpan.FromSeconds(5));
        }
    }
}
