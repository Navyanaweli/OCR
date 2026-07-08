import { Component, Output, EventEmitter } from '@angular/core';
import { IoppService } from '../../services/iopp.service';
import { DocumentRecord } from '../../models/record.model';

@Component({
  selector: 'app-upload',
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.scss']
})
export class UploadComponent {
  @Output() classified = new EventEmitter<DocumentRecord>();

  isDragOver = false;
  isLoading = false;
  error: string | null = null;
  result: DocumentRecord | null = null;
  allRecords: DocumentRecord[] = [];

  constructor(private ioppService: IoppService) {
    this.loadRecords();
  }

  loadRecords() {
    this.ioppService.getRecords().subscribe({
      next: (records) => this.allRecords = records,
      error: () => {}
    });
  }

  onDragOver(e: DragEvent) { e.preventDefault(); this.isDragOver = true; }
  onDragLeave() { this.isDragOver = false; }

  onDrop(e: DragEvent) {
    e.preventDefault();
    this.isDragOver = false;
    const file = e.dataTransfer?.files[0];
    if (file) this.handleFile(file);
  }

  onFileSelected(e: Event) {
    const input = e.target as HTMLInputElement;
    if (input.files?.[0]) this.handleFile(input.files[0]);
    input.value = '';
  }

  handleFile(file: File) {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      this.error = 'Please upload a valid PDF file.';
      return;
    }
    this.isLoading = true;
    this.error = null;
    this.result = null;

    this.ioppService.classify(file).subscribe({
      next: (record) => {
        this.isLoading = false;
        this.result = record;
        this.allRecords = [record, ...this.allRecords];
        this.classified.emit(record);
      },
      error: (err) => {
        this.isLoading = false;
        this.error = err.error?.error || err.error?.detail || 'Classification failed. Make sure the backend is running.';      }
    });
  }

  deleteRecord(id: string) {
    if (!confirm('Delete this document?')) return;
    this.ioppService.deleteRecord(id).subscribe({
      next: () => {
        this.allRecords = this.allRecords.filter(r => r.id !== id);
      },
      error: () => alert('Could not delete. Make sure the backend is running.')
    });
  }

  fmtSize(bytes: number): string {
    if (!bytes) return '';
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
  }

  getDocStyle(t: string) {
    if (t === 'IOPP Certificate Supplement') return { badgeCls: 'badge-iopp', docIcon: 'ti-file-certificate', label: 'IOPP' };
    if (t === 'Tank Diagram / Capacity Plan') return { badgeCls: 'badge-tank', docIcon: 'ti-chart-grid-dots', label: 'Tank Diagram' };
    return { badgeCls: 'badge-unknown', docIcon: 'ti-help-circle', label: 'Unknown' };
  }

  getTierIcon(tier: string): string {
    if (!tier) return 'ti-server';
    if (tier.includes('Tier 1')) return 'ti-text-scan-2';
    if (tier.includes('Tier 2')) return 'ti-tag';
    if (tier.includes('Tier 3')) return 'ti-tags';
    return 'ti-circle-off';
  }

  get resultStyle() { return this.result ? this.getDocStyle(this.result.document_type) : null; }
}
