import * as vscode from 'vscode';
import { ApiRequestView } from './apiRequestView';
import { HttpClient } from '../utils/httpClient';

interface Collection {
    name: string;
    requests: ApiRequest[];
}

interface ApiRequest {
    name: string;
    method: string;
    url: string;
    headers: Record<string, string>;
    body: string;
}

export class ApiRequestProvider {
    private context: vscode.ExtensionContext;
    private view: ApiRequestView | undefined;
    private httpClient: HttpClient;
    private collections: Collection[] = [];
    private environment: Record<string, string> = {};
    private apiHistory: ApiRequest[] = []; 

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.httpClient = new HttpClient();
        this.handleApiRequest = this.handleApiRequest.bind(this);
        this.loadCollections();
        this.loadEnvironment();
        this.loadApiHistory(); 
    }

    public openApiRequestView(endpoint?: ApiRequest) {
        if (!this.view) {
            this.view = new ApiRequestView(this.context, this.handleApiRequest);
        }
        
        // Show the view
        this.view.show();

        // If an endpoint is provided, populate its details
        if (endpoint) {
            this.populateFields(endpoint);
        }

        this.updateCollectionsView();
    }

    private populateFields(endpoint: ApiRequest) {
        // Assuming you have methods in your ApiRequestView to set these values
        if (this.view) {
            this.view.setMethod(endpoint.method); // Method setter in ApiRequestView
            this.view.setUrl(endpoint.url);       // URL setter in ApiRequestView
            this.view.setHeaders(endpoint.headers); // Headers setter in ApiRequestView
            this.view.setBody(endpoint.body);     // Body setter in ApiRequestView
        }
    }

    private async handleApiRequest(
        method: string, 
        url: string, 
        headers: Record<string, string>, 
        queryParams: Record<string, string>, 
        formData: Record<string, string>, 
        body: string,
        bodyType: string
    ): Promise<void> {
        try {
            // Append query params to URL
            const urlObj = new URL(url);
            Object.entries(queryParams).forEach(([key, value]) => {
                urlObj.searchParams.append(key, value);
            });

            // Prepare body
            let requestBody: string | FormData | undefined;
            if (bodyType === 'form-data') {
                requestBody = new FormData();
                Object.entries(formData).forEach(([key, value]) => {
                    (requestBody as FormData).append(key, value);
                });
            } else if (bodyType === 'raw' && body) {
                requestBody = body;
            }

            const startTime = Date.now();
            const response = await this.httpClient.sendRequest(
                urlObj.toString(), 
                method, 
                headers, 
                requestBody
            );
            const endTime = Date.now();
            const responseTime = endTime - startTime;
            const responseSize = JSON.stringify(response).length;

            // Create an API request object
            const apiRequest: ApiRequest = {
                name: `${method} ${url}`,
                method,
                url,
                headers,
                body,
            };

            // Add to API history and save it
            this.apiHistory.push(apiRequest);
            // await this.saveApiHistory(); // Save in MessagePack format

            this.view?.postMessage({
                command: 'receiveResponse',
                response,
                time: responseTime,
                size: responseSize
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Error sending request: ${error}`);
        }
    }

    private loadApiHistory() {
        // Load existing API history from global state if needed
        this.apiHistory = this.context.globalState.get('apiHistory', []);
    }

    private loadCollections() {
        this.collections = this.context.globalState.get('apiCollections', []);
    }

    private saveCollections() {
        this.context.globalState.update('apiCollections', this.collections);
    }

    private updateCollectionsView() {
        this.view?.postMessage({
            command: 'updateCollections',
            collections: this.collections
        });
    }

    public setEnvironmentVariable(key: string, value: string) {
        this.environment[key] = value;
        this.saveEnvironment();
    }

    private loadEnvironment() {
        this.environment = this.context.globalState.get('apiEnvironment', {});
    }

    private saveEnvironment() {
        this.context.globalState.update('apiEnvironment', this.environment);
    }
}