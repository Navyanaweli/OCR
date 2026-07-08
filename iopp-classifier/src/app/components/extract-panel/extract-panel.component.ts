import { Component, Input } from '@angular/core';
import { ExtractedData, Tank } from '../../models/record.model';

@Component({
  selector: 'app-extract-panel',
  templateUrl: './extract-panel.component.html',
  styleUrls: ['./extract-panel.component.scss']
})
export class ExtractPanelComponent {
  @Input() data: ExtractedData | null = null;

  get s31() { return this.data?.section_3_1_sludge_tanks; }
  get s32() { return this.data?.section_3_2_disposal_means; }
  get s33() { return this.data?.section_3_3_bilge_water_holding_tanks; }
}
