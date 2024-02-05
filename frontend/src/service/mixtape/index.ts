import { Track } from "@/models/Release";
import { doRequest } from "../request";

interface MatchingTracksResponse {
  matched_by: string;
  matches: string;
  tracks: Track[];
}

class MixtapeService {
  public async getMatchingTracks(style: string, bpm: string, key: string): Promise<MatchingTracksResponse | null> {
    try {
      const response = await doRequest('/api/v1/mixtape/tracks/matching', {
        method: 'GET',
        params: {
          style,
          bpm,
          key,
        },
      });
      if (response.status === 200) return response.data;
    } catch (error) {
      console.error(error);
    }

    return null;
  }
}

export const mixtapeService = new MixtapeService();
