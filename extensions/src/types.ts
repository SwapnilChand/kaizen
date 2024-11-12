export interface ApiEndpoint {
  method: string;
  name: string;
  headers: Record<string, string>;
  queryParams: Record<string, string>;
  formData: Record<string, string>;
  body: string;
  bodyType: string;
  lastUsed: string;
}
