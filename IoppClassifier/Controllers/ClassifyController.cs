using Microsoft.AspNetCore.Mvc;
using IoppClassifier.Services;

namespace IoppClassifier.Controllers;

[ApiController]
[Route("[controller]")]
public class ClassifyController : ControllerBase
{
    private readonly PythonClassifierService _classifier;
    private readonly RecordsService _records;
    private readonly IConfiguration _config;
    private readonly ILogger<ClassifyController> _logger;

    public ClassifyController(
        PythonClassifierService classifier,
        RecordsService records,
        IConfiguration config,
        ILogger<ClassifyController> logger)
    {
        _classifier = classifier;
        _records = records;
        _config = config;
        _logger = logger;
    }

    [HttpGet]
    public IActionResult Health() =>
        Ok(new { message = "C# IOPP API is running" });

    [HttpGet("records")]
    public async Task<IActionResult> GetRecords()
    {
        var records = await _records.GetAllAsync();
        return Ok(records);
    }

    [HttpDelete("records/{id}")]
    public async Task<IActionResult> DeleteRecord(string id)
    {
        var uploadDir = _config["Storage:UploadDir"] ?? "uploads";
        var filePath = Path.Combine(uploadDir, id + ".pdf");

        if (System.IO.File.Exists(filePath))
            System.IO.File.Delete(filePath);

        var deleted = await _records.DeleteAsync(id);

        if (!deleted)
            return NotFound(new { error = "Record not found." });

        return Ok(new { deleted = id });
    }

    [HttpPost]
    public async Task<IActionResult> ClassifyDocument(IFormFile file)
    {
        if (file is null || file.Length == 0)
            return BadRequest(new { error = "No file uploaded." });

        if (!file.FileName.EndsWith(".pdf", StringComparison.OrdinalIgnoreCase))
            return BadRequest(new { error = "Only PDF files are allowed." });

        var uploadDir = _config["Storage:UploadDir"] ?? "uploads";
        Directory.CreateDirectory(uploadDir);

        var uniqueId = Guid.NewGuid().ToString();
        var filePath = Path.Combine(uploadDir, uniqueId + ".pdf");

        try
        {
            await using (var stream = System.IO.File.Create(filePath))
                await file.CopyToAsync(stream);

            var record = await _classifier.ClassifyAsync(filePath, file.FileName);

            record.Id = uniqueId;
            record.Filename = file.FileName;
            record.SizeBytes = new FileInfo(filePath).Length;

            await _records.AddAsync(record);

            return Ok(record);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Classification failed");

            if (System.IO.File.Exists(filePath))
                System.IO.File.Delete(filePath);

            return StatusCode(500, new { error = ex.Message });
        }
    }

    [HttpPost("extract")]
    public async Task<IActionResult> ExtractDocument(IFormFile file)
    {
        if (file is null || file.Length == 0)
            return BadRequest(new { error = "No file uploaded." });

        if (!file.FileName.EndsWith(".pdf", StringComparison.OrdinalIgnoreCase))
            return BadRequest(new { error = "Only PDF files are allowed." });

        var tempDir = Path.Combine(Path.GetTempPath(), "iopp-extract");
        Directory.CreateDirectory(tempDir);

        var filePath = Path.Combine(tempDir, Guid.NewGuid() + ".pdf");

        try
        {
            await using (var stream = System.IO.File.Create(filePath))
                await file.CopyToAsync(stream);

            var result = await _classifier.ExtractAsync(filePath, file.FileName);
            return Ok(result);
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { error = ex.Message });
        }
        finally
        {
            if (System.IO.File.Exists(filePath))
                System.IO.File.Delete(filePath);
        }
    }

    [HttpGet("extract-saved/{id}")]
    public async Task<IActionResult> ExtractSaved(string id)
    {
        var uploadDir = _config["Storage:UploadDir"] ?? "uploads";
        var filePath = Path.Combine(uploadDir, id + ".pdf");

        if (!System.IO.File.Exists(filePath))
            return NotFound(new { error = "Saved PDF file not found." });

        try
        {
            var result = await _classifier.ExtractAsync(filePath, id + ".pdf");
            return Ok(result);
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { error = ex.Message });
        }
    }
}