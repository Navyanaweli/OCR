using System.Text.Json;
using System.Text.Json.Serialization;
using IoppClassifier.Models;

namespace IoppClassifier.Services;

public class PythonClassifierService
{
    private readonly HttpClient _httpClient;
    private readonly IConfiguration _config;
    private readonly ILogger<PythonClassifierService> _logger;

    private string ServiceUrl => _config["Python:ServiceUrl"] ?? "http://localhost:5000";

    public PythonClassifierService(
        IHttpClientFactory httpClientFactory,
        IConfiguration config,
        ILogger<PythonClassifierService> logger)
    {
        _httpClient = httpClientFactory.CreateClient();
        _config = config;
        _logger = logger;
    }

    public async Task<ClassificationRecord> ClassifyAsync(string pdfPath, string originalFilename)
    {
        using var form = new MultipartFormDataContent();

        await using var fileStream = File.OpenRead(pdfPath);
        var fileContent = new StreamContent(fileStream);
        fileContent.Headers.ContentType =
            new System.Net.Http.Headers.MediaTypeHeaderValue("application/pdf");

        form.Add(fileContent, "file", originalFilename);

        var response = await _httpClient.PostAsync($"{ServiceUrl}/classify", form);
        var json = await response.Content.ReadAsStringAsync();

        if (!response.IsSuccessStatusCode)
            throw new Exception($"Python FastAPI classification failed: {json}");

        var options = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true
        };

        var result = JsonSerializer.Deserialize<PythonResult>(json, options)
            ?? throw new Exception($"Could not parse Python response: {json}");

        return new ClassificationRecord
        {
            Filename = result.Filename ?? originalFilename,
            DocumentType = result.DocumentType ?? "Unknown",
            Reason = result.Reason ?? string.Empty,
            Tier = result.Tier ?? string.Empty,
            UploadedAt = result.UploadedAt ?? DateTime.Now.ToString("yyyy-MM-dd HH:mm")
        };
    }

    public async Task<object> ExtractAsync(string pdfPath, string originalFilename)
    {
        using var form = new MultipartFormDataContent();

        await using var fileStream = File.OpenRead(pdfPath);
        var fileContent = new StreamContent(fileStream);
        fileContent.Headers.ContentType =
            new System.Net.Http.Headers.MediaTypeHeaderValue("application/pdf");

        form.Add(fileContent, "file", originalFilename);

        var response = await _httpClient.PostAsync($"{ServiceUrl}/extract", form);
        var json = await response.Content.ReadAsStringAsync();

        if (!response.IsSuccessStatusCode)
            throw new Exception($"Python FastAPI extraction failed: {json}");

        return JsonSerializer.Deserialize<object>(json)
            ?? throw new Exception("Could not parse extraction response.");
    }

    public async Task<object> ExtractSavedAsync(string id)
    {
        var response = await _httpClient.GetAsync($"{ServiceUrl}/extract-saved/{id}");
        var json = await response.Content.ReadAsStringAsync();

        if (!response.IsSuccessStatusCode)
            throw new Exception($"Python FastAPI saved extraction failed: {json}");

        return JsonSerializer.Deserialize<object>(json)
            ?? throw new Exception("Could not parse saved extraction response.");
    }

    private class PythonResult
    {
        [JsonPropertyName("id")]
        public string? Id { get; set; }

        [JsonPropertyName("filename")]
        public string? Filename { get; set; }

        [JsonPropertyName("document_type")]
        public string? DocumentType { get; set; }


        [JsonPropertyName("reason")]
        public string? Reason { get; set; }

        [JsonPropertyName("tier")]
        public string? Tier { get; set; }

        [JsonPropertyName("uploaded_at")]
        public string? UploadedAt { get; set; }
    }
}