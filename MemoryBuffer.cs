using System.Collections.Concurrent;

namespace FENR1R;

public sealed class MemoryBuffer
{
    private readonly ConcurrentDictionary<string, Queue<(DateTime Timestamp, string Message)>> _buffers = new();
    private readonly TimeSpan _maxAge;

    public MemoryBuffer(int maxAgeSeconds)
    {
        _maxAge = TimeSpan.FromSeconds(maxAgeSeconds);
    }

    public void AddMessage(string source, string message)
    {
        var queue = _buffers.GetOrAdd(source, _ => new Queue<(DateTime, string)>());
        lock (queue)
        {
            queue.Enqueue((DateTime.UtcNow, message));
            Cleanup(source, queue);
        }
    }

    public IReadOnlyList<string> GetRecentContext(string source)
    {
        if (!_buffers.TryGetValue(source, out var queue))
        {
            return Array.Empty<string>();
        }

        lock (queue)
        {
            Cleanup(source, queue);
            return queue.Select(item => item.Message).ToList();
        }
    }

    private void Cleanup(string source, Queue<(DateTime Timestamp, string Message)> queue)
    {
        while (queue.Count > 0 && DateTime.UtcNow - queue.Peek().Timestamp > _maxAge)
        {
            queue.Dequeue();
        }
    }
}
