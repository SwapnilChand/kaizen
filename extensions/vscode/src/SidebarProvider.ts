import * as fs from 'fs';
import * as path from 'path';
import * as msgpack from 'msgpack-lite'; 
import * as vscode from 'vscode';
import { ApiRequestProvider } from './apiRequest/apiRequestProvider';
import { log } from './extension';
import { ApiEndpoint } from './types';
import { TestManagementProvider } from './testManagement/testManagementProvider';
import { ChatRepoProvider } from './chatRepo/chatRepoProvider'; 
import { DocManagementProvider } from './docManagement/docManagementProvider'; 

export class SidebarProvider implements vscode.WebviewViewProvider {
    _view?: vscode.WebviewView;
    _doc?: vscode.TextDocument;
    private apiRequestProvider: ApiRequestProvider;
    private apiHistory: ApiEndpoint[] = [];
    private showHistory: boolean = false;
    private context: vscode.ExtensionContext;
    private testManagementProvider: TestManagementProvider;
    private chatRepoProvider: ChatRepoProvider; 
    private docManagementProvider: DocManagementProvider; 

    constructor(private readonly _extensionUri: vscode.Uri, context: vscode.ExtensionContext) {
        this.apiRequestProvider = new ApiRequestProvider(context);
        this.context = context;
        this.loadApiHistory();
        this.testManagementProvider = new TestManagementProvider(context);
        this.chatRepoProvider = new ChatRepoProvider(context); // Initialize ChatRepoProvider
        this.docManagementProvider = new DocManagementProvider(context); // Initialize DocManagementProvider

        // Register command to update API history
        context.subscriptions.push(
            vscode.commands.registerCommand('vscode-api-client.updateApiHistory', (endpoint: ApiEndpoint) => {
                this.updateApiHistory(endpoint);
            })
        );
    }

    private loadApiHistory() {
        try {
            const history = this.context.globalState.get<ApiEndpoint[]>('apiHistory', []);
            this.apiHistory = history || [];
        } catch (error) {
            console.error('Error loading API history:', error);
            this.apiHistory = [];
        }
    }

    private async saveApiHistory() {
        try {
            console.log("Saving API History...");
    
            // Update global state with current API history
            await this.context.globalState.update('apiHistory', this.apiHistory);
    
            // Define file path for saving the API history
            const folderPath = path.join(this.context.extensionPath, 'api_history');
            
            // Create directory if it doesn't exist
            if (!fs.existsSync(folderPath)) {
                fs.mkdirSync(folderPath);
                console.log(`Created folder at ${folderPath}`);
            }
    
            // Define file path for the MessagePack file
            const filePath = path.join(folderPath, 'history.msgpack');
    
            // Write API history to MessagePack file
            // const packedData = msgpack.encode(this.apiHistory); // Encode data using MessagePack
            // fs.writeFileSync(filePath, packedData); // Write packed data to file
            
            // vscode.window.showInformationMessage('API history Saved');
        } catch (error) {
            console.error('Error saving API history:', error); // Log any errors encountered
            // vscode.window.showErrorMessage(`Failed to save API history: ${error.message}`);
        }
    }

    public refresh() {
        if (this._view) {
            console.log('Refreshing webview content');
            this._view.webview.html = this._getHtmlForWebview(this._view.webview);
        }
    }

    public resolveWebviewView(webviewView: vscode.WebviewView) {
        this._view = webviewView;
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri],
        };

        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

        webviewView.webview.onDidReceiveMessage(async (data) => {
            log("Received message on sidebar");
            switch (data.type) {
                case "onInfo": {
                    if (!data.value) {
                        return;
                    }
                    vscode.window.showInformationMessage(data.value);
                    break;
                }
                case "onError": {
                    if (!data.value) {
                        return;
                    }
                    vscode.window.showErrorMessage(data.value);
                    break;
                }
                case "openApiManagement": {
                    if (!data.value) {
                        return;
                    }
                    this.openWebview(data.value);
                    break;
                }
                case "backButton": {
                    this.showHistory = false;
                    this.refresh();
                    break;
                }
                case "newRequest": {
                    this.openApiRequestView();
                    break;
                }
                case "deleteEndpoint": {
                    this.deleteEndpoint(data.name, data.method);
                    break;
                }
                case "openChatRepo": { // Handle opening the chat repo view
                    this.chatRepoProvider.openChatRepoView();
                    break;
                }
                case "openDocManagement": { // Handle opening the doc management view
                    this.docManagementProvider.openDocManagementView();
                    break;
                }
                case "exportApiHistory": {
                    await this.saveApiHistory(); // Call the save function when export is requested
                    break;
                }
                case "reloadEndpoint": { 
                    await this.loadApiHistory(); 
                    const selectedEndpoint = this.apiHistory.find(endpoint => 
                        endpoint.name === data.value.name && endpoint.method === data.value.method
                    );
                
                    if (selectedEndpoint) {
                        this.apiRequestProvider.openApiRequestView(selectedEndpoint); // Pass the selected endpoint
                    } else {
                        vscode.window.showErrorMessage(`No history found for ${data.value.name} with method ${data.value.method}`);
                    }
                }
            }
        });
    }

    public revive(panel: vscode.WebviewView) {
        this._view = panel;
    }

    private _getHtmlForWebview(webview: vscode.Webview) {
        log("HTML Web View Loaded");

        const scriptUri = webview.asWebviewUri(
            vscode.Uri.joinPath(this._extensionUri, "out", "sidebar.js")
        );

        const styleSidebarUri = webview.asWebviewUri(
            vscode.Uri.joinPath(this._extensionUri, "media", "sidebar.css")
        );

        const nonce = getNonce();

        const csp = `
          default-src 'none';
          script-src ${webview.cspSource} 'nonce-${nonce}';
          style-src ${webview.cspSource};
          img-src ${webview.cspSource} https:;
          font-src ${webview.cspSource};
        `;

        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="Content-Security-Policy" content="${csp}">
            <link href="${styleSidebarUri}" rel="stylesheet">
        </head>
        <body>
        ${this.showHistory
            ? `<button id="back-button">Back</button>${this.getHistoryHtml()}`
            : `<div id="buttons">
               <button class="webview-button" data-webview="apiManagement">API Management</button>
               <button class="webview-button" data-webview="documentation">Doc Management [Coming Soon]</button>
               <button class="webview-button" data-webview="testManagement">Test Management [Coming Soon]</button>
               <button class="webview-button" data-webview="chatRepo">Chat Repo</button> 
               <button class="webview-button" data-webview="codeReview">Code Review [Coming Soon]</button>
             </div>`
          }
        <script nonce="${nonce}" src="${scriptUri}"></script>
        </body>
        </html>`;
    }

    private getHistoryHtml() {
      return `
      <div id="sidebar-container">
          <div id="history-header">
              <h3>API History</h3>
              <button id="new-request-btn">New Request</button>
              <button id="export-history-btn">Export History</button>
          </div>
          <input type="text" id="filter-history" placeholder="Filter history">
          <ul id="api-history">
              ${this.apiHistory.map(endpoint => `
                  <li class="api-endpoint ${endpoint.method.toLowerCase()}">
                      <span class="method">${endpoint.method}</span>
                      <span class="name">${endpoint.name}</span>
                      <span class="last-used">${new Date(endpoint.lastUsed).toLocaleString()}</span>
                      <button class="delete-btn" data-name="${endpoint.name}" data-method="${endpoint.method}">X</button>
                  </li>
              `).join('')}
          </ul>
      </div>`;
  }

  private async openWebview(webviewType: string) {
      if (webviewType === 'apiManagement') {
          if (this.apiRequestProvider) {
              console.log("Opening API Request View");
              this.apiRequestProvider.openApiRequestView();
              this.showHistory = true;
              this.refresh();
          } else {
              console.error("apiRequestProvider is not initialized");
              vscode.window.showErrorMessage("API Management is not available");
          }
      } else if (webviewType === 'testManagement') {
          if (this.testManagementProvider) {
              console.log("Opening Test Management View");
              await this.testManagementProvider.openTestManagementView();
          } else {
              console.error("testManagementProvider is not initialized");
              vscode.window.showErrorMessage("Test Management is not available");
          }
      } else if (webviewType === 'chatRepo') { // Handle opening chat repo view
          if (this.chatRepoProvider) {
              console.log("Opening Chat Repo View");
              await this.chatRepoProvider.openChatRepoView();
          } else {
              console.error("chatRepoProvider is not initialized");
              vscode.window.showErrorMessage("Chat Repo is not available");
          }
      } else if (webviewType === 'documentation') { // Handle opening doc management view
          if (this.docManagementProvider) {
              console.log("Opening Documentation Management View");
              await this.docManagementProvider.openDocManagementView();
          } else {
              console.error("docManagementProvider is not initialized");
              vscode.window.showErrorMessage("Documentation Management is not available");
          }
      } else {
          const panel = vscode.window.createWebviewPanel(
              webviewType,
              this.getWebviewTitle(webviewType),
              vscode.ViewColumn.One,
              {
                  enableScripts: true,
                  localResourceRoots: [this._extensionUri],
              }
          );

          panel.webview.html = await this.getWebviewContent(webviewType);
      }
  }

  private openApiRequestView(endpoint?: ApiEndpoint) {
    if (this.apiRequestProvider) {
        console.log("Opening API Request View");
        if (endpoint) {
            this.apiRequestProvider.openApiRequestView(endpoint); // Pass the selected endpoint
        } else {
            this.apiRequestProvider.openApiRequestView(); // Open without pre-populating if no endpoint is provided
        }
    } else {
        console.error("apiRequestProvider is not initialized");
        vscode.window.showErrorMessage("API Request is not available");
    }
}

  private getWebviewTitle(webviewType: string): string {
      switch (webviewType) {
          case 'apiManagement':
              return 'API Management';
          case 'apiRequest':
              return 'API Request';
          case 'chatRepo':
              return 'Chat Repo';
          case 'documentation':
              return 'Documentation';
          case 'codeReview':
              return 'Code Review';
          case 'testManagement':
              return 'Test Case';
          default:
              return 'Webview';
      }
  }

  private async getWebviewContent(webviewType: string): Promise<string> {
      const filePath = vscode.Uri.joinPath(this._extensionUri, webviewType, 'index.html');
      const fileContent = await vscode.workspace.fs.readFile(filePath);
      return fileContent.toString();
  }

  private updateApiHistory(endpoint: ApiEndpoint) {
      const existingIndex = this.apiHistory.findIndex(
          e => e.name === endpoint.name && e.method === endpoint.method
      );

      if (existingIndex !== -1) {
          this.apiHistory[existingIndex].lastUsed = endpoint.lastUsed;
          const [updatedEndpoint] = this.apiHistory.splice(existingIndex, 1);
          this.apiHistory.unshift(updatedEndpoint);
      } else {
          this.apiHistory.unshift(endpoint);
          this.apiHistory = this.apiHistory.slice(0, 10);
      }

     
      this.refresh();
  }

  private deleteEndpoint(name: string, method: string) {
      this.apiHistory = this.apiHistory.filter(
          endpoint => !(endpoint.name === name && endpoint.method === method)
      );
      this.saveApiHistory();
      this.refresh();
  }
}

function getNonce() {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < 32; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}