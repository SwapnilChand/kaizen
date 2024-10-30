export class HttpClient {
  public async sendRequest(
    method: string,
    url: string,
    headers: Record<string, string>,
    body?: string | FormData
  ) {
    console.log("Request sent from https client");
    console.log("Sending Request:", { method, url, headers, body });

    try {
      // Validate inputs
      if (!method || !url) {
        throw new Error("Method and URL are required");
      }

      // Validate URL format
      try {
        new URL(url);
      } catch (urlError) {
        throw new Error(`Invalid URL format: ${url}`);
      }

      // Prepare request options
      const options: RequestInit = {
        method: method.toUpperCase(), // Normalize method to uppercase
        headers: { ...headers }, // Create a copy of headers
      };

      // Handle body data
      if (body) {
        if (body instanceof FormData) {
          options.body = body;
          // Remove content-type header as it will be set automatically for FormData
          delete options.headers["content-type"];
        } else if (typeof body === "string") {
          options.body = body;
          // Set content-type if not already set and body is string
          if (!options.headers["content-type"]) {
            options.headers["content-type"] = "application/json";
          }
        }
      }

      console.log("Request Options:", {
        method: options.method,
        headers: options.headers,
        bodyPresent: !!options.body,
      });

      // Make the request
      const response = await fetch(url, options);
      console.log("Response status:", response.status, response.statusText);

      // Process response headers
      const responseHeaders: Record<string, string> = {};
      response.headers.forEach((value, key) => {
        responseHeaders[key] = value;
      });

      // Get response body
      const responseBody = await response.text();
      console.log("Response Headers:", responseHeaders);
      console.log("Response Body length:", responseBody.length);

      // Only log full body if it's not too large
      if (responseBody.length < 1000) {
        console.log("Response Body:", responseBody);
      } else {
        console.log(
          "Response Body (truncated):",
          responseBody.substring(0, 1000) + "..."
        );
      }

      return {
        status: response.status,
        statusText: response.statusText,
        headers: responseHeaders,
        body: responseBody,
      };
    } catch (error) {
      console.error("Error in HttpClient.sendRequest:", {
        error: error.message,
        method,
        url,
        headerKeys: Object.keys(headers),
      });
      throw new Error(`Request failed: ${error.message}`);
    }
  }
}
