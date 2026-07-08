import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';

import { AppComponent } from './app.component';
import { UploadComponent } from './components/upload/upload.component';
import { StorageComponent } from './components/storage/storage.component';
import { ExtractPanelComponent } from './components/extract-panel/extract-panel.component';

@NgModule({
  declarations: [
    AppComponent,
    UploadComponent,
    StorageComponent,
    ExtractPanelComponent
  ],
  imports: [BrowserModule, HttpClientModule],
  bootstrap: [AppComponent]
})
export class AppModule {}
