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

class BackupService {
  public async export(): Promise<any | null> {
    try {
      const response = await doRequest('/api/v1/backup/export', {
        method: 'GET',
      });
      if (response.status !== 200) return null;

      // Download response.data as file
      const blob = new Blob([response.data], { type: 'application/octet-stream' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'collection-backup.sql';
      a.click();
      window.URL.revokeObjectURL(url);
      return response.data;
    } catch (error) {
      console.error(error);
    }
    return null;
  }

  public async import(file: File): Promise<any | null> {
    try {
      const formData = new FormData();
      formData.append('backup_file', file);
      const response = await doRequest('/api/v1/backup/import', {
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

export const backupService = new BackupService();
