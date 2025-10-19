const { spawn } = require('child_process');
const readline = require('readline');

class MCPServer {
  constructor() {
    this.process = null;
    this.roots = [
      "/Users/lchtangen/Documents/SampleMind AI/SampleMind-AI---Beta"
    ];
    this.messageId = 1;
    this.pendingRequests = new Map();
  }

  start() {
    return new Promise((resolve) => {
      this.process = spawn('npx', [
        '-y',
        '@modelcontextprotocol/server-filesystem'
      ], {
        stdio: ['pipe', 'pipe', 'pipe']
      });

      // Handle server output line by line
      const rl = readline.createInterface({
        input: this.process.stdout,
        terminal: false
      });

      rl.on('line', (line) => {
        try {
          const message = JSON.parse(line);
          console.log('[MCP Server]', JSON.stringify(message, null, 2));
          
          // Handle responses to our requests
          if (message.id && this.pendingRequests.has(message.id)) {
            const { resolve } = this.pendingRequests.get(message.id);
            this.pendingRequests.delete(message.id);
            resolve(message);
          }
        } catch (e) {
          console.error('Error parsing message:', e);
        }
      });

      this.process.stderr.on('data', (data) => {
        console.error(`[MCP Error] ${data}`);
      });

      // Wait for server to be ready
      setTimeout(() => {
        this.initialize().then(() => {
          console.log('MCP server initialized');
          resolve();
        });
      }, 1000);
    });
  }

  async sendRequest(method, params = {}) {
    const id = this.messageId++;
    const message = {
      jsonrpc: '2.0',
      method,
      params,
      id
    };

    return new Promise((resolve) => {
      this.pendingRequests.set(id, { resolve });
      this.process.stdin.write(JSON.stringify(message) + '\n');
    });
  }

  async initialize() {
    // First, send the initialize request with minimal capabilities
    const initResponse = await this.sendRequest('initialize', {
      protocolVersion: '1.0',
      clientInfo: {
        name: 'MCP Test Client',
        version: '0.1.0'
      },
      capabilities: {}
    });

    if (initResponse.error) {
      throw new Error(`Initialization failed: ${initResponse.error.message}`);
    }

    // Set initial roots after successful initialization
    await this.setRoots(this.roots);
    
    return initResponse.result;
  }

  async setRoots(paths) {
    // Set roots using the standard MCP filesystem protocol
    const response = await this.sendRequest('filesystem/setRoots', {
      roots: paths.map(path => ({
        path,
        capabilities: {
          read: true,
          write: true
        }
      }))
    });

    if (response.error) {
      console.warn('Failed to set roots using filesystem/setRoots, trying fallback...');
      
      // Fallback to initialize with roots
      const initResponse = await this.sendRequest('initialize', {
        protocolVersion: '1.0',
        clientInfo: {
          name: 'MCP Test Client',
          version: '0.1.0'
        },
        rootDirectories: paths.map(path => ({
          path,
          capabilities: ['read', 'write']
        })),
        capabilities: {}
      });

      if (initResponse.error) {
        throw new Error(`Failed to set roots: ${initResponse.error.message}`);
      }
      
      return initResponse.result;
    }
    
    return response.result;
  }

  async listDirectory(path) {
    // First try the standard MCP filesystem protocol
    try {
      const response = await this.sendRequest('filesystem/readDirectory', { path });
      if (!response.error) {
        return response.result || [];
      }
    } catch (e) {
      console.warn('filesystem/readDirectory failed, trying fallback methods...');
    }

    // Fallback methods if the standard method fails
    const methods = [
      'filesystem/listDirectory',
      'fs/readDirectory',
      'fs/listDirectory',
      'readDirectory',
      'listDirectory'
    ];

    for (const method of methods) {
      try {
        const response = await this.sendRequest(method, { path });
        if (!response.error) {
          console.log(`Successfully listed directory using method: ${method}`);
          return response.result || [];
        }
      } catch (e) {
        // Continue to next method
      }
    }
    
    throw new Error('Failed to list directory. No compatible method found.');
  }

  stop() {
    if (this.process) {
      this.process.kill();
      this.process = null;
    }
  }
}

// Example usage
async function testMCP() {
  const mcp = new MCPServer();
  
  try {
    console.log('Starting MCP server...');
    await mcp.start();
    
    console.log('Listing root directory...');
    const result = await mcp.listDirectory('/');
    console.log('Directory contents:', result);
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    console.log('Stopping MCP server...');
    mcp.stop();
  }
}

testMCP();
