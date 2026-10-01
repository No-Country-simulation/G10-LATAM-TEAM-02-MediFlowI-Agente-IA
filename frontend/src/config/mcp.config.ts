/**
 * MediFlow — Configuración y Conexión para Model Context Protocol (MCP)
 * 
 * Este archivo centraliza la configuración de servidores MCP externos o locales
 * para conectar herramientas de agentes y modelos de IA en el Frontend.
 * 
 * IMPORTANTE: Las credenciales y claves privadas NUNCA deben escribirse fijas en el código.
 * Se inyectan en tiempo de ejecución o compilación mediante variables de entorno Vite (VITE_MCP_*).
 */

export type McpTransportType = 'sse' | 'websocket' | 'http'

export interface McpServerConfig {
  /** Nombre amigable del servidor MCP (ej: "mediflow-clinical-tools") */
  name: string
  /** URL base o endpoint del servidor MCP */
  serverUrl: string
  /** Clave API o token Bearer para autenticarse con el servidor MCP */
  apiKey?: string
  /** Protocolo de transporte utilizado para streaming de contexto y ejecución de tools */
  transport: McpTransportType
  /** Indica si la conexión MCP está activa */
  enabled: boolean
  /** Tiempo límite de respuesta en milisegundos */
  timeoutMs: number
  /** Catálogo de herramientas o prompts clínicos permitidos */
  allowedTools: string[]
}

/**
 * Obtiene la configuración activa del servidor MCP a partir de variables de entorno seguras
 */
export function getMcpConfig(): McpServerConfig {
  const env = import.meta.env

  return {
    name: env.VITE_MCP_SERVER_NAME || 'mediflow-mcp-agent',
    serverUrl: env.VITE_MCP_SERVER_URL || 'http://localhost:8001/mcp',
    apiKey: env.VITE_MCP_API_KEY || '',
    transport: (env.VITE_MCP_TRANSPORT as McpTransportType) || 'sse',
    enabled: env.VITE_MCP_ENABLED === 'true',
    timeoutMs: Number(env.VITE_MCP_TIMEOUT_MS) || 15000,
    allowedTools: env.VITE_MCP_ALLOWED_TOOLS
      ? env.VITE_MCP_ALLOWED_TOOLS.split(',').map((t: string) => t.trim())
      : ['consultar_cie10', 'resumir_historia_clinica', 'calcular_urgencia'],
  }
}

/**
 * Genera los headers HTTP de autenticación para solicitudes hacia el servidor MCP
 */
export function getMcpAuthHeaders(config: McpServerConfig = getMcpConfig()): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'X-Client-Source': 'mediflow-frontend',
  }

  if (config.apiKey) {
    headers['Authorization'] = `Bearer ${config.apiKey}`
    headers['X-MCP-API-Key'] = config.apiKey
  }

  return headers
}

/**
 * Valida si la configuración actual cuenta con los parámetros mínimos para operar
 */
export function isMcpConfigured(config: McpServerConfig = getMcpConfig()): { valid: boolean; missing: string[] } {
  const missing: string[] = []

  if (!config.enabled) {
    return { valid: false, missing: ['VITE_MCP_ENABLED debe ser "true"'] }
  }

  if (!config.serverUrl) {
    missing.push('VITE_MCP_SERVER_URL')
  }

  return {
    valid: missing.length === 0,
    missing,
  }
}
