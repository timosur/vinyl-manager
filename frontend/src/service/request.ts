import axios, { AxiosRequestConfig, AxiosResponse } from 'axios';

// add 401 interceptor
axios.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    return Promise.reject(error);
  },
);

export async function doRequest<T = any>(
  url: string,
  options: AxiosRequestConfig,
): Promise<AxiosResponse<T>> {
  const headers = options.headers || {};

  // add environment variable API_URL as prefix to url when on the server
  // use typeof window to check if we are on the server or client
  if (typeof window === 'undefined') {
    url = `${process.env.API_URL}${url}`;
  }

  const response = await axios(url, {
    headers,
    ...options,
  });

  return response;
}