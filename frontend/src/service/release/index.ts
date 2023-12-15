import { doRequest } from '../request';

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
}

export const releaseService = new ReleaseService();
