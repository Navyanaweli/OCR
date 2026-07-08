using System.Text.Json.Serialization;

namespace IoppClassifier.Models;

public class ClassificationRecord
{
    [JsonPropertyName("id")]
    public string Id { get; set; } = Guid.NewGuid().ToString();

    [JsonPropertyName("filename")]
    public string Filename { get; set; } = string.Empty;

    [JsonPropertyName("document_type")]
    public string DocumentType { get; set; } = string.Empty;

    [JsonPropertyName("reason")]
    public string Reason { get; set; } = string.Empty;

    [JsonPropertyName("tier")]
    public string Tier { get; set; } = string.Empty;

    [JsonPropertyName("uploaded_at")]
    public string UploadedAt { get; set; } = DateTime.Now.ToString("yyyy-MM-dd HH:mm");

    [JsonPropertyName("size_bytes")]
    public long SizeBytes { get; set; }
}