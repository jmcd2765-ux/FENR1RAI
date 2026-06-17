using Microsoft.Extensions.Logging;

namespace FENR1R;

internal static class Program
{
    private static async Task Main()
    {
        DotEnvLoader.Load(".env");

        using var loggerFactory = LoggingConfig.SetupLogging(LogLevel.Information);
        var logger = loggerFactory.CreateLogger("FENR1R");

        try
        {
            var config = Config.Load("config.json");
            var bot = new FENR1RBot(config, loggerFactory);
            await bot.ConnectAsync();
            logger.LogInformation("FENR1R is running. Press Ctrl+C to exit.");
            await Task.Delay(Timeout.Infinite);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Fatal error while starting FENR1R.");
        }
    }
}
