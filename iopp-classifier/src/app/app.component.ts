import { Component } from '@angular/core';
import { DocumentRecord } from './models/record.model';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  activeSection: 'upload' | 'iopp' | 'tank' = 'upload';
  latestRecord: DocumentRecord | null = null;

  showSection(section: 'upload' | 'iopp' | 'tank') {
    this.activeSection = section;
  }

  onClassified(record: DocumentRecord) {
    this.latestRecord = { ...record };
  }
}
