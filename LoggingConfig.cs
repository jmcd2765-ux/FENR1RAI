using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

namespace FENR1R;

public static class LoggingConfig
{
    public static ILoggerFactory SetupLogging(LogLevel level)
    {
        var serviceCollection = new ServiceCollection();
        serviceCollection.AddLogging(builder =>
        {
            builder.ClearProviders();
            builder.AddSimpleConsole(options =>
            {
                options.TimestampFormat = "yyyy-MM-dd HH:mm:ss ";
                options.IncludeScopes = false;
            });
            builder.SetMinimumLevel(level);
        });

        var serviceProvider = serviceCollection.BuildServiceProvider();
        return serviceProvider.GetRequiredService<ILoggerFactory>();
    }
}
