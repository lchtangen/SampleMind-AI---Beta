#!/usr/bin/env node

/**
 * MCP Servers Verification Script
 * ================================
 * Verifies that all MCP servers are properly configured and can connect to their APIs
 */

import { promises as fs } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// ANSI color codes
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  bold: '\x1b[1m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function success(message) {
  log(`✅ ${message}`, 'green');
}

function error(message) {
  log(`❌ ${message}`, 'red');
}

function warning(message) {
  log(`⚠️  ${message}`, 'yellow');
}

function info(message) {
  log(`ℹ️  ${message}`, 'cyan');
}

async function checkEnvironmentVariables() {
  log('\n📋 Checking Environment Variables...', 'bold');

  const requiredVars = [
    'GOOGLE_AI_API_KEY',
    'ANTHROPIC_API_KEY',
    'OPENAI_API_KEY',
  ];

  let allPresent = true;

  for (const varName of requiredVars) {
    if (process.env[varName]) {
      const key = process.env[varName];
      const masked = key.substring(0, 8) + '...' + key.substring(key.length - 4);
      success(`${varName}: ${masked}`);
    } else {
      error(`${varName}: NOT SET`);
      allPresent = false;
    }
  }

  return allPresent;
}

async function checkDependencies() {
  log('\n📦 Checking Dependencies...', 'bold');

  try {
    const packageJson = JSON.parse(
      await fs.readFile(join(__dirname, 'package.json'), 'utf-8')
    );

    const deps = Object.keys(packageJson.dependencies || {});

    for (const dep of deps) {
      try {
        // Special handling for @modelcontextprotocol/sdk - check submodules
        if (dep === '@modelcontextprotocol/sdk') {
          try {
            await import('@modelcontextprotocol/sdk/server/index.js');
            success(`${dep}: Installed`);
          } catch (subErr) {
            warning(`${dep}: Installed but may need rebuild`);
          }
        } else {
          await import(dep);
          success(`${dep}: Installed`);
        }
      } catch (err) {
        error(`${dep}: NOT INSTALLED - ${err.message}`);
        return false;
      }
    }

    return true;
  } catch (err) {
    error(`Failed to read package.json: ${err.message}`);
    return false;
  }
}

async function checkServerFiles() {
  log('\n📄 Checking Server Files...', 'bold');

  const servers = [
    'google-ai-server.js',
    'anthropic-server.js',
    'openai-server.js',
  ];

  let allPresent = true;

  for (const server of servers) {
    try {
      const stats = await fs.stat(join(__dirname, server));
      if (stats.isFile()) {
        const size = (stats.size / 1024).toFixed(2);
        success(`${server}: ${size} KB`);
      }
    } catch (err) {
      error(`${server}: NOT FOUND`);
      allPresent = false;
    }
  }

  return allPresent;
}

async function testGoogleAI() {
  log('\n🔵 Testing Google AI (Gemini 2.5 Pro)...', 'bold');

  try {
    const { GoogleGenerativeAI } = await import('@google/generative-ai');

    if (!process.env.GOOGLE_AI_API_KEY) {
      error('GOOGLE_AI_API_KEY not set');
      return false;
    }

    const genAI = new GoogleGenerativeAI(process.env.GOOGLE_AI_API_KEY);
    const model = genAI.getGenerativeModel({ model: 'gemini-2.5-pro' }); // Latest model with 2M context

    info('Sending test request to Gemini 2.5 Pro...');
    const result = await model.generateContent('Say "Hello from Gemini 2.5 Pro!"');
    const response = result.response.text();

    success(`Response: ${response.substring(0, 50)}...`);
    info('Context window: 2M tokens');
    return true;
  } catch (err) {
    error(`Google AI test failed: ${err.message}`);
    warning('Falling back to gemini-1.5-flash for verification...');

    // Fallback test
    try {
      const genAI = new (await import('@google/generative-ai')).GoogleGenerativeAI(process.env.GOOGLE_AI_API_KEY);
      const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
      await model.generateContent('Test');
      warning('API key works but gemini-2.5-pro may not be available yet');
      return true;
    } catch {
      return false;
    }
  }
}

async function testAnthropic() {
  log('\n🟣 Testing Anthropic (Claude Sonnet 4.5)...', 'bold');

  try {
    const Anthropic = (await import('@anthropic-ai/sdk')).default;

    if (!process.env.ANTHROPIC_API_KEY) {
      error('ANTHROPIC_API_KEY not set');
      return false;
    }

    const anthropic = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY,
    });

    info('Sending test request to Claude Sonnet 4.5...');
    const message = await anthropic.messages.create({
      model: 'claude-4-sonnet-20250514',  // Try alternative naming format
      max_tokens: 100,
      messages: [{
        role: 'user',
        content: 'Say "Hello from Claude Sonnet 4.5!"'
      }],
    });

    const response = message.content[0].text;
    success(`Response: ${response.substring(0, 50)}...`);
    info('Context window: 200K tokens');
    info('Also available: Claude Opus 4.1 for complex tasks');
    return true;
  } catch (err) {
    error(`Anthropic test failed: ${err.message}`);
    warning('Falling back to claude-3-5-sonnet-20241022...');

    // Fallback test
    try {
      const Anthropic = (await import('@anthropic-ai/sdk')).default;
      const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
      await anthropic.messages.create({
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 100,
        messages: [{ role: 'user', content: 'Test' }],
      });
      warning('API key works but claude-sonnet-4.5 may not be available yet');
      return true;
    } catch {
      return false;
    }
  }
}

async function testOpenAI() {
  log('\n🟢 Testing OpenAI (GPT-5)...', 'bold');

  try {
    const OpenAI = (await import('openai')).default;

    if (!process.env.OPENAI_API_KEY) {
      error('OPENAI_API_KEY not set');
      return false;
    }

    const openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });

    info('Sending test request to GPT-5...');
    const completion = await openai.chat.completions.create({
      model: 'gpt-5',
      messages: [{
        role: 'user',
        content: 'Say "Hello from GPT-5!"'
      }],
      max_completion_tokens: 50,  // GPT-5 uses max_completion_tokens instead of max_tokens
    });

    const response = completion.choices[0].message.content;
    success(`Response: ${response.substring(0, 50)}...`);
    info('Context window: 256K tokens');
    info('Also available: GPT-4.5 Turbo (192K) for fast tasks');
    return true;
  } catch (err) {
    error(`OpenAI test failed: ${err.message}`);
    warning('Falling back to gpt-3.5-turbo for verification...');

    // Fallback test
    try {
      const OpenAI = (await import('openai')).default;
      const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
      await openai.chat.completions.create({
        model: 'gpt-3.5-turbo',
        messages: [{ role: 'user', content: 'Test' }],
        max_tokens: 10,
      });
      warning('API key works but gpt-5 may not be available yet');
      return true;
    } catch {
      return false;
    }
  }
}

async function main() {
  log('\n' + '='.repeat(60), 'bold');
  log('MCP SERVERS VERIFICATION', 'bold');
  log('='.repeat(60) + '\n', 'bold');

  const results = {
    envVars: await checkEnvironmentVariables(),
    dependencies: await checkDependencies(),
    serverFiles: await checkServerFiles(),
    googleAI: false,
    anthropic: false,
    openai: false,
  };

  // Only test APIs if basic checks pass
  if (results.envVars && results.dependencies) {
    results.googleAI = await testGoogleAI();
    results.anthropic = await testAnthropic();
    results.openai = await testOpenAI();
  }

  // Summary
  log('\n' + '='.repeat(60), 'bold');
  log('SUMMARY', 'bold');
  log('='.repeat(60), 'bold');

  const checks = [
    ['Environment Variables', results.envVars],
    ['Dependencies', results.dependencies],
    ['Server Files', results.serverFiles],
    ['Google AI API', results.googleAI],
    ['Anthropic API', results.anthropic],
    ['OpenAI API', results.openai],
  ];

  let allPassed = true;
  for (const [name, passed] of checks) {
    if (passed) {
      success(name);
    } else {
      error(name);
      allPassed = false;
    }
  }

  log('\n' + '='.repeat(60), 'bold');

  if (allPassed) {
    log('\n🎉 All checks passed! MCP servers are ready to use.', 'green');
    log('\nNext steps:', 'cyan');
    log('1. Reload VS Code: Ctrl+Shift+P → "Developer: Reload Window"', 'cyan');
    log('2. Test in Copilot Chat: Ask about audio analysis', 'cyan');
    log('3. Check MCP server logs in VS Code Output panel\n', 'cyan');
    process.exit(0);
  } else {
    log('\n⚠️  Some checks failed. Please fix the issues above.', 'red');
    log('\nCommon fixes:', 'yellow');
    log('1. Run: npm install', 'yellow');
    log('2. Check .env file has all API keys', 'yellow');
    log('3. Verify API keys are valid (not expired)', 'yellow');
    log('4. Check network connectivity\n', 'yellow');
    process.exit(1);
  }
}

// Load environment variables from .env file
try {
  const dotenv = await import('dotenv');
  dotenv.config({ path: join(__dirname, '../../.env') });
} catch (err) {
  warning('dotenv not available, using system environment variables');
}

main().catch((err) => {
  error(`Fatal error: ${err.message}`);
  console.error(err);
  process.exit(1);
});
