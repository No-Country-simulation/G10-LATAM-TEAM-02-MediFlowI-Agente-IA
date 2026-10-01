/**
 * MediFlow — Cliente API para Model Context Protocol (MCP)
 * 
 * Permite listar herramientas (tools), recursos clínicos y ejecutar acciones
 * a través de un servidor MCP compatible.
 */

import { getMcpConfig, getMcpAuthHeaders, isMcpConfigured } from '../config/mcp.config'
import type { McpServerConfig } from '../config/mcp.config'

export interface McpToolDefinition {
  name: string
  description: string
  inputSchema: Record<string, unknown>
}

export interface McpToolCallResult {
  tool: string
  success: boolean
  content: Array<{ type: string; text?: string; data?: unknown }>
  error?: string
}

export interface McpServerStatus {
  online: boolean
  serverName: string
  protocolVersion: string
  toolsCount: number
}

/**
 * Consulta el estado y disponibilidad del servidor MCP
 */
export async function checkMcpHealth(customConfig?: McpServerConfig): Promise<McpServerStatus> {
  const config = customConfig || getMcpConfig()
  const validation = isMcpConfigured(config)

  if (!validation.valid) {
    return {
      online: false,
      serverName: config.name,
      protocolVersion: 'unknown',
      toolsCount: 0,
    }
  }

  try {
    const res = await fetch(`${config.serverUrl}/health`, {
      method: 'GET',
      headers: getMcpAuthHeaders(config),
      signal: AbortSignal.timeout(config.timeoutMs),
    })

    if (!res.ok) {
      return { online: false, serverName: config.name, protocolVersion: 'unknown', toolsCount: 0 }
    }

    const data = await res.json()
    return {
      online: true,
      serverName: data.name || config.name,
      protocolVersion: data.protocolVersion || '2024-11-05',
      toolsCount: Array.isArray(data.tools) ? data.tools.length : 0,
    }
  } catch {
    return {
      online: false,
      serverName: config.name,
      protocolVersion: 'unknown',
      toolsCount: 0,
    }
  }
}

/**
 * Obtiene la lista de herramientas disponibles en el servidor MCP
 */
export async function listMcpTools(customConfig?: McpServerConfig): Promise<McpToolDefinition[]> {
  const config = customConfig || getMcpConfig()
  const validation = isMcpConfigured(config)

  if (!validation.valid) {
    return []
  }

  try {
    const res = await fetch(`${config.serverUrl}/tools`, {
      method: 'GET',
      headers: getMcpAuthHeaders(config),
      signal: AbortSignal.timeout(config.timeoutMs),
    })

    if (!res.ok) {
      throw new Error(`Error al listar tools de MCP: HTTP ${res.status}`)
    }

    const data = await res.json()
    return data.tools || []
  } catch (error) {
    console.error('Error conectando con servidor MCP:', error)
    return []
  }
}

/**
 * Invoca una herramienta clínica del servidor MCP con sus argumentos
 */
export async function callMcpTool(
  toolName: string,
  args: Record<string, unknown>,
  customConfig?: McpServerConfig
): Promise<McpToolCallResult> {
  const config = customConfig || getMcpConfig()
  const validation = isMcpConfigured(config)

  if (!validation.valid) {
    return {
      tool: toolName,
      success: false,
      content: [],
      error: `MCP no está configurado correctamente: ${validation.missing.join(', ')}`,
    }
  }

  try {
    const res = await fetch(`${config.serverUrl}/tools/call`, {
      method: 'POST',
      headers: getMcpAuthHeaders(config),
      body: JSON.stringify({ name: toolName, arguments: args }),
      signal: AbortSignal.timeout(config.timeoutMs),
    })

    if (!res.ok) {
      const errText = await res.text()
      return {
        tool: toolName,
        success: false,
        content: [],
        error: `Fallo en tool call: HTTP ${res.status} - ${errText}`,
      }
    }

    const data = await res.json()
    return {
      tool: toolName,
      success: true,
      content: data.content || [],
    }
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err)
    return {
      tool: toolName,
      success: false,
      content: [],
      error: message,
    }
  }
}
