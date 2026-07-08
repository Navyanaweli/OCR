import { Component, OnInit, Input, SimpleChanges, OnChanges } from '@angular/core';
import { IoppService } from '../../services/iopp.service';
import { DocumentRecord, ExtractedData } from '../../models/record.model';

@Component({
  selector: 'app-storage',
  templateUrl: './storage.component.html',
  styleUrls: ['./storage.component.scss']
})
export class StorageComponent implements OnInit, OnChanges {
  @Input() newRecord: DocumentRecord | null = null;
  @Input() filterType: 'iopp' | 'tank' | 'all' = 'all';

  allRecords: DocumentRecord[] = [];
  expandedId: string | null = null;
  loadingId: string | null = null;
  extractedMap: { [id: string]: ExtractedData } = {};

  constructor(private ioppService: IoppService) {}

  ngOnInit() { this.loadRecords(); }

  ngOnChanges(changes: SimpleChanges) {
    if (changes.newRecord?.currentValue) {
      const r = changes.newRecord.currentValue as DocumentRecord;
      this.allRecords = [r, ...this.allRecords.filter(x => x.id !== r.id)];
    }
  }

  loadRecords() {
    this.ioppService.getRecords().subscribe({
      next: (records) => this.allRecords = records,
      error: () => {}
    });
  }

  get records(): DocumentRecord[] {
    if (this.filterType === 'iopp') return this.allRecords.filter(r => r.document_type === 'IOPP Certificate Supplement');
    if (this.filterType === 'tank') return this.allRecords.filter(r => r.document_type === 'Tank Diagram / Capacity Plan');
    return this.allRecords;
  }

  get title(): string {
    if (this.filterType === 'iopp') return 'IOPP Documents';
    if (this.filterType === 'tank') return 'Tank Diagram Documents';
    return 'All Documents';
  }

  get eyebrow(): string {
    if (this.filterType === 'iopp') return 'Extracted Module';
    if (this.filterType === 'tank') return 'Future Module';
    return 'Storage';
  }

  get description(): string {
    if (this.filterType === 'iopp') return 'IOPP documents appear here. Click View to extract sludge tanks, disposal means, and bilge water holding tanks.';
    if (this.filterType === 'tank') return 'Tank Diagram documents appear here. Extraction is not implemented yet.';
    return '';
  }

  get emptyMessage(): string {
    if (this.filterType === 'iopp') return 'No IOPP documents uploaded yet.';
    if (this.filterType === 'tank') return 'No Tank Diagram documents uploaded yet.';
    return 'No documents uploaded yet.';
  }

  toggleDetail(id: string) {
    if (this.expandedId === id) { this.expandedId = null; return; }
    this.expandedId = id;
    if (!this.extractedMap[id]) this.loadExtracted(id);
  }

  loadExtracted(id: string) {
    this.loadingId = id;
    this.ioppService.extractSaved(id).subscribe({
      next: (data) => { this.extractedMap[id] = data; this.loadingId = null; },
      error: () => { this.loadingId = null; }
    });
  }

  deleteRecord(id: string) {
    if (!confirm('Delete this document?')) return;
    this.ioppService.deleteRecord(id).subscribe({
      next: () => {
        this.allRecords = this.allRecords.filter(r => r.id !== id);
        if (this.expandedId === id) this.expandedId = null;
      },
      error: () => alert('Could not delete.')
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
    if (t === 'Tank Diagram / Capacity Plan') return { badgeCls: 'badge-tank', docIcon: 'ti-chart-grid-dots', label: 'Tank' };
    return { badgeCls: 'badge-unknown', docIcon: 'ti-help-circle', label: 'Unknown' };
  }
}
