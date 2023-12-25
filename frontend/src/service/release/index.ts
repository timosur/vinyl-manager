import { Release, Track } from '@/models/Release';
import { doRequest } from '../request';

const convertToBase64 = async (file: Blob): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = error => reject(error);
    reader.readAsDataURL(file);
  });
}

class ReleaseService {
  public async get(): Promise<any | null> {
    try {
      const response = await doRequest('/api/v1/release', {
        method: 'GET',
      });
      if (response.status === 200) return response.data;
    } catch (error) {
      console.error(error);
    }
    return null;
  }

  public async getById(id: string): Promise<any | null> {
    try {
      const response = await doRequest(`/api/v1/release/${id}`, {
        method: 'GET',
      });
      if (response.status !== 200) return null;

      // convert base64 to blob for each track audio attribute
      const tracks = await Promise.all(response.data.tracks.map(async (track: Track) => {
        if (!track.audio) return track;
        const audio = track.audio as string;
        track.audio = await fetch(audio).then(res => res.blob());
        return track;
      }));

      response.data.tracks = tracks;

      return response.data;
    } catch (error) {
      console.error(error);
    }
    return null;
  }

  public async update(id: string, data: Release, analysis: boolean): Promise<any | null> {
    try {
      // convert audio to base64 for each track audio attribute
      const tracks = await Promise.all(data.tracks.map(async (track: Track) => {
        if (!track.audio) return track;
        const audio = track.audio as Blob;
        track.audio = await convertToBase64(audio);
        return track;
      }));
      data.tracks = tracks;

      const response = await doRequest(`/api/v1/release/${id}?analysis=${analysis}`, {
        method: 'PUT',
        data,
      });

      // convert base64 to blob for each track audio attribute
      const updatedTracks = await Promise.all(response.data.tracks.map(async (track: Track) => {
        if (!track.audio) return track;
        const audio = track.audio as string;
        track.audio = await fetch(audio).then(res => res.blob());
        return track;
      }));

      response.data.tracks = updatedTracks;

      if (response.status === 200) return response.data;
    } catch (error) {
      console.error(error);
    }
    return null;
  }

  public async discogsSync(): Promise<any | null> {
    try {
      const response = await doRequest('/api/v1/release/sync-discogs?username=timosur', {
        method: 'POST',
      });
      if (response.status === 200) return response.data;
    } catch (error) {
      console.error(error);
    }
    return null;
  }

  public async importDeejayDeCSV(file: File): Promise<any | null> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await doRequest('/api/v1/release/import-deejay-de-csv', {
        method: 'POST',
        data: formData,
      });
      if (response.status === 200) return response.data;
    } catch (error) {
      console.error(error);
    }
    return null;
  }

  public async deleteItem(type: 'track' | 'label' | 'artist', releaseId: string, itemId: string): Promise<any | null> {
    try {
      const response = await doRequest(`/api/v1/release/${releaseId}/${type}/${itemId}`, {
        method: 'DELETE',
      });
      if (response.status === 200) return response.data;
    } catch (error) {
      console.error(error);
    }
    return null;
  }

  public async addItem(type: 'track' | 'label' | 'artist', releaseId: string, name: string): Promise<any | null> {
    try {
      const response = await doRequest(`/api/v1/release/${releaseId}/${type}/empty?name=${name}`, {
        method: 'POST',
      });
      if (response.status === 200) return response.data;
    } catch (error) {
      console.error(error);
    }
    return null;
  }
}

export const releaseService = new ReleaseService();
