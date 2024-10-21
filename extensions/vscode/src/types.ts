export interface ApiEndpoint {
    method: string;
    name: string;
    lastUsed: string;
    url: string; 
    headers: Record<string, string>; 
    body: string; 
}