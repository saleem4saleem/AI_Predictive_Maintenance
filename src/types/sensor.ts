export interface SensorLatestResponse {
  asset_id: number;
  timestamp: string | null;
  vibration: number | null;
  temperature: number | null;
  pressure: number | null;
  current_value: number | null;
  speed: number | null;
  flow: number | null;
  runtime_hours?: number | null;
}

export interface SensorHistoryPoint {
  timestamp: string;
  vibration: number | null;
  temperature: number | null;
  pressure: number | null;
  current_value: number | null;
  speed: number | null;
  flow: number | null;
  runtime_hours?: number | null;
}

export interface SensorHistoryResponse {
  asset_id: number;
  history: SensorHistoryPoint[];
}
