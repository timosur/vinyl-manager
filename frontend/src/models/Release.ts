export interface Release {
  id: string;
  short: string;
  created_at: string;
  updated_at: string | null;
  name: string;
  tracks: Track[];
  labels: Label[];
  artists: Artist[];
}

interface Track {
  rating: number | null;
  created_at: string;
  updated_at: string | null;
  name: string;
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
