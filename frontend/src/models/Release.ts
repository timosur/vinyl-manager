export interface Release {
  [key: string]: any;
  id: string;
  short: string;
  year: string;
  format: string;
  genre: string;
  purchased_at: string;
  styles: string;
  thumb: string;
  created_at: string;
  updated_at: string | null;
  name: string;
  notes: string;
  tracks: Track[];
  labels: Label[];
  artists: Artist[];
}

export interface Track {
  rating: number | null;
  created_at?: string;
  updated_at?: string | null;
  name: string;
  key: string;
  bpm: number;
  genre: string;
  audio: Blob | string;
  length: number;
  id: string;
  side: string;
  release_id: string;
}

interface Label {
  id: string;
  name: string;
  created_at: string;
  release_id: string;
  updated_at: string | null;
}

interface Artist {
  name: string;
  created_at: string;
  id: string;
  release_id: string;
  updated_at: string | null;
}
