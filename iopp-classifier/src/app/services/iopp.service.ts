import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { DocumentRecord, ExtractedData } from '../models/record.model';

@Injectable({ providedIn: 'root' })
export class IoppService {
  private api = environment.apiUrl;

  constructor(private http: HttpClient) {}

  classify(file: File): Observable<DocumentRecord> {
    const fd = new FormData();
    fd.append('file', file);
    return this.http.post<DocumentRecord>(`${this.api}/classify`, fd);
  }

  getRecords(): Observable<DocumentRecord[]> {
    return this.http.get<DocumentRecord[]>(`${this.api}/classify/records`);
  }

  deleteRecord(id: string): Observable<any> {
    return this.http.delete(`${this.api}/classify/records/${id}`);
  }

  extractSaved(id: string): Observable<ExtractedData> {
    return this.http.get<ExtractedData>(`${this.api}/classify/extract-saved/${id}`);
  }
}