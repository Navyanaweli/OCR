export interface DocumentRecord {
  id: string;
  filename: string;
  document_type: string;
  reason: string;
  tier: string;
  uploaded_at: string;
  size_bytes: number;
  extracted?: ExtractedData | null;
}

export interface Tank {
  tank_identification: string;
  frames_from: string;
  frames_to: string;
  lateral_position: string;
  volume_m3: number;
}

export interface SludgeTanks {
  description: string;
  tanks: Tank[];
  total_volume_m3: number | null;
}

export interface DisposalMeans {
  description: string;
  incinerator_for_sludge: boolean;
  auxiliary_boiler: boolean;
  other_acceptable_means: boolean;
  other_means_description: string;
}

export interface BilgeWaterTanks {
  description: string;
  tanks: Tank[];
  total_volume_m3: number | null;
}

export interface ExtractedData {
  section_3_1_sludge_tanks: SludgeTanks;
  section_3_2_disposal_means: DisposalMeans;
  section_3_3_bilge_water_holding_tanks: BilgeWaterTanks;
}
