using System.Text.RegularExpressions;

namespace FENR1R;

public sealed class SecurityFilter
{
    private readonly List<Regex> _denyPatterns = new()
    {
        new Regex(@"\b(hate|racist|sexist|violent|threat|dox|explicit|self[- ]harm|suicide|bully|harass|abuse)\b", RegexOptions.IgnoreCase | RegexOptions.Compiled),
        new Regex(@"\b(fuck|shit|cunt|asshole|damn|bitch|die|kill|punch|slap)\b", RegexOptions.IgnoreCase | RegexOptions.Compiled)
    };

    public string FilterResponse(string response)
    {
        if (string.IsNullOrWhiteSpace(response))
        {
            return string.Empty;
        }

        foreach (var pattern in _denyPatterns)
        {
            if (pattern.IsMatch(response))
            {
                return string.Empty;
            }
        }

        return response.Trim();
    }
}
