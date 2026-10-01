import { describe, it, expect } from 'vitest'
import { getMcpAuthHeaders, isMcpConfigured } from './mcp.config'
import type { McpServerConfig } from './mcp.config'

describe('Configuración MCP (mcp.config.ts)', () => {
  const dummyConfig: McpServerConfig = {
    name: 'test-mcp',
    serverUrl: 'http://localhost:8001/mcp',
    apiKey: 'mcp-secret-key-123',
    transport: 'sse',
    enabled: true,
    timeoutMs: 10000,
    allowedTools: ['tool_a', 'tool_b'],
  }

  it('obtiene headers con autenticación Bearer y API key cuando se define apiKey', () => {
    const headers = getMcpAuthHeaders(dummyConfig)
    expect(headers['Authorization']).toBe('Bearer mcp-secret-key-123')
    expect(headers['X-MCP-API-Key']).toBe('mcp-secret-key-123')
    expect(headers['Content-Type']).toBe('application/json')
  })

  it('valida correctamente una configuración activa con servidor y apiKey', () => {
    const validation = isMcpConfigured(dummyConfig)
    expect(validation.valid).toBe(true)
    expect(validation.missing).toHaveLength(0)
  })

  it('detecta si MCP está deshabilitado', () => {
    const disabledConfig = { ...dummyConfig, enabled: false }
    const validation = isMcpConfigured(disabledConfig)
    expect(validation.valid).toBe(false)
    expect(validation.missing[0]).toContain('VITE_MCP_ENABLED')
  })
})
