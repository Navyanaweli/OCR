using System.Text.Json;
using IoppClassifier.Models;

namespace IoppClassifier.Services;

/// <summary>
/// Lightweight persistent store backed by a local records.json file.
/// Thread-safe via a SemaphoreSlim for concurrent requests.
/// </summary>
public class RecordsService
{
    private readonly string _recordsPath;
    private readonly SemaphoreSlim _lock = new(1, 1);

    public RecordsService(IConfiguration config)
    {
        _recordsPath = config["Storage:RecordsFile"] ?? "records.json";
        if (!File.Exists(_recordsPath))
            File.WriteAllText(_recordsPath, "[]");
    }

    public async Task<List<ClassificationRecord>> GetAllAsync()
    {
        await _lock.WaitAsync();
        try
        {
            var json = await File.ReadAllTextAsync(_recordsPath);
            return JsonSerializer.Deserialize<List<ClassificationRecord>>(json,
                new JsonSerializerOptions { PropertyNameCaseInsensitive = true })
                ?? new List<ClassificationRecord>();
        }
        finally { _lock.Release(); }
    }

    public async Task AddAsync(ClassificationRecord record)
    {
        await _lock.WaitAsync();
        try
        {
            var records = await ReadAsync();
            records.Insert(0, record);
            await WriteAsync(records);
        }
        finally { _lock.Release(); }
    }

    public async Task<bool> DeleteAsync(string id)
    {
        await _lock.WaitAsync();
        try
        {
            var records = await ReadAsync();
            var existing = records.FirstOrDefault(r => r.Id == id);
            if (existing is null) return false;
            records.Remove(existing);
            await WriteAsync(records);
            return true;
        }
        finally { _lock.Release(); }
    }

    private async Task<List<ClassificationRecord>> ReadAsync()
    {
        var json = await File.ReadAllTextAsync(_recordsPath);
        return JsonSerializer.Deserialize<List<ClassificationRecord>>(json,
            new JsonSerializerOptions { PropertyNameCaseInsensitive = true })
            ?? new List<ClassificationRecord>();
    }

    private async Task WriteAsync(List<ClassificationRecord> records)
    {
        var json = JsonSerializer.Serialize(records,
            new JsonSerializerOptions { WriteIndented = true });
        await File.WriteAllTextAsync(_recordsPath, json);
    }
}