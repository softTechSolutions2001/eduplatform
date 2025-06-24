# fmt: off
# isort: skip_file

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
React Hooks Generator

This module generates React hook examples for API calls based on extracted backend information.
The hooks follow React best practices and provide TypeScript integration.

Author: nanthiniSanthanam
Generated: 2025-05-04 14:17:12

Configuration Variables:
- OUTPUT_DIR: Directory where React hook files will be generated
- GENERATE_REACT_HOOKS: Boolean flag to enable/disable React hooks generation
- DETAIL_LEVEL: Level of detail for generated hooks ("basic", "standard", "comprehensive")
- BACKEND_URL: URL of the backend API server for examples
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Set, Optional

logger = logging.getLogger(__name__)


class ReactHooksGenerator:
    """Generate React hooks for API calls based on extracted backend information"""

    def __init__(self, config):
        """Initialize with configuration"""
        self.config = config
        self.detail_level = config.DETAIL_LEVEL
        self.backend_url = config.BACKEND_URL

    def generate(self, apis: Dict[str, Any], auth_info: Dict[str, Any],
                 output_dir: Path) -> None:
        """Generate React hook examples

        Args:
            apis: Extracted API endpoint information
            auth_info: Authentication configuration information
            output_dir: Directory where React hook files will be generated
        """
        logger.info("Generating React hooks for API integration")

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create index.tsx with exports and utility hooks
        self._generate_index_file(output_dir, auth_info)

        # Create base hook utilities
        self._generate_base_hooks(output_dir)

        # Generate endpoint-specific hooks
        endpoints = apis.get('endpoints', [])
        grouped_endpoints = apis.get('grouped', {})

        if grouped_endpoints:
            # Generate hooks by app
            for app_name, app_info in grouped_endpoints.items():
                if not app_info.get('endpoints'):
                    continue

                # Create app-specific file
                sanitized_app_name = app_name.split('.')[-1].lower()
                file_path = output_dir / f"{sanitized_app_name}_hooks.tsx"

                hooks_content = self._generate_hooks_file(
                    app_info.get('endpoints', []), 
                    app_name,
                    auth_info
                )

                with open(file_path, 'w') as f:
                    f.write('\n'.join(hooks_content))

                logger.info(f"Generated React hooks for {app_name}")
        else:
            # Generate a single file for all endpoints
            file_path = output_dir / "api_hooks.tsx"

            hooks_content = self._generate_hooks_file(
                endpoints,
                "API",
                auth_info
            )

            with open(file_path, 'w') as f:
                f.write('\n'.join(hooks_content))

            logger.info("Generated React hooks")

        # Create a README file with usage examples
        self._generate_readme(output_dir)

        logger.info(f"React hooks generated in {output_dir}")

    def _generate_index_file(self, output_dir: Path, auth_info: Dict[str, Any]) -> None:
        """Generate index.tsx file with exports and auth utilities

        Args:
            output_dir: Directory where React hook files will be generated
            auth_info: Authentication configuration information
        """
        index_path = output_dir / 'index.tsx'

        # Determine auth method
        primary_auth_method = auth_info.get('auth_flows', {}).get('primary_method', '')

        index_content = [
            '/**',
            ' * React hooks for API integration',
            f' * Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            ' */',
            'import React from "react";',
            '',
            '// Re-export all hooks',
            'export * from "./use_api";',
            'export * from "./api_hooks";',
        ]

        # Add app-specific exports
        grouped_endpoints = self.config.get('grouped_endpoints', True)
        if grouped_endpoints:
            index_content.append('')
            index_content.append('// App-specific hooks')

            # This is a placeholder since we don't know the exact app names at this point
            index_content.append('// export * from "./app_name_hooks";')

        index_content.extend([
            '',
            '/**',
            ' * API configuration context for global settings',
            ' */',
            'interface ApiConfig {',
            '  baseUrl: string;',
            '  defaultHeaders: Record<string, string>;',
            '}',
            '',
            'const ApiContext = React.createContext<ApiConfig>({',
            f'  baseUrl: "{self.backend_url or "http://localhost:8000"}",',
            '  defaultHeaders: {',
            '    "Content-Type": "application/json",',
            '  },',
            '});',
            '',
            '/**',
            ' * Provider component for API configuration',
            ' */',
            'interface ApiProviderProps {',
            '  baseUrl?: string;',
            '  children: React.ReactNode;',
            '}',
            '',
            'export const ApiProvider: React.FC<ApiProviderProps> = ({',
            '  baseUrl = "' + (self.backend_url or "http://localhost:8000") + '",',
            '  children,',
            '}) => {',
            '  const config = React.useMemo(',
            '    () => ({',
            '      baseUrl,',
            '      defaultHeaders: {',
            '        "Content-Type": "application/json",',
            '      },',
            '    }),',
            '    [baseUrl]',
            '  );',
            '',
            '  return (',
            '    <ApiContext.Provider value={config}>{children}</ApiContext.Provider>',
            '  );',
            '};',
            '',
            '/**',
            ' * Hook to access API configuration',
            ' */',
            'export const useApiConfig = () => React.useContext(ApiContext);',
            '',
        ])

        # Add authentication utilities based on the primary auth method
        if primary_auth_method == 'jwt':
            index_content.extend(self._generate_jwt_auth_hooks())
        elif primary_auth_method == 'token':
            index_content.extend(self._generate_token_auth_hooks())
        elif primary_auth_method == 'session':
            index_content.extend(self._generate_session_auth_hooks())
        else:
            # Default to a simple auth utilities
            index_content.extend(self._generate_default_auth_hooks())

        # Write the file
        with open(index_path, 'w') as f:
            f.write('\n'.join(index_content))

        logger.info("Generated index.tsx with auth utilities")

    def _generate_base_hooks(self, output_dir: Path) -> None:
        """Generate base API hook utilities

        Args:
            output_dir: Directory where React hook files will be generated
        """
        file_path = output_dir / 'use_api.tsx'

        content = [
            '/**',
            ' * Base API hook utilities for making requests',
            f' * Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            ' */',
            'import { useState, useEffect, useCallback } from "react";',
            'import { useApiConfig, useAuthHeader } from "./index";',
            '',
            'type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";',
            '',
            '/**',
            ' * Options for API requests',
            ' */',
            'interface ApiRequestOptions {',
            '  method?: HttpMethod;',
            '  headers?: Record<string, string>;',
            '  body?: any;',
            '  includeAuth?: boolean;',
            '  signal?: AbortSignal;',
            '}',
            '',
            '/**',
            ' * Response from API requests',
            ' */',
            'interface ApiResponse<T> {',
            '  data: T | null;',
            '  error: Error | null;',
            '  loading: boolean;',
            '  refetch: () => void;',
            '}',
            '',
            '/**',
            ' * Custom hook for making API requests',
            ' */',
            'export function useApi<T = any>(',
            '  endpoint: string,',
            '  options: ApiRequestOptions = {}',
            '): ApiResponse<T> {',
            '  const { baseUrl, defaultHeaders } = useApiConfig();',
            '  const getAuthHeader = useAuthHeader();',
            '  const [data, setData] = useState<T | null>(null);',
            '  const [error, setError] = useState<Error | null>(null);',
            '  const [loading, setLoading] = useState(true);',
            '  const [refetchIndex, setRefetchIndex] = useState(0);',
            '',
            '  const refetch = useCallback(() => setRefetchIndex(i => i + 1), []);',
            '',
            '  useEffect(() => {',
            '    // Don\'t make the request if the endpoint is empty',
            '    if (!endpoint) {',
            '      setLoading(false);',
            '      return;',
            '    }',
            '',
            '    const controller = new AbortController();',
            '    const signal = options.signal || controller.signal;',
            '',
            '    const fetchData = async () => {',
            '      setLoading(true);',
            '',
            '      try {',
            '        // Build URL',
            '        const url = endpoint.startsWith("http")',
            '          ? endpoint',
            '          : `${baseUrl}${endpoint.startsWith("/") ? "" : "/"}${endpoint}`;',
            '',
            '        // Build headers',
            '        const headers = {',
            '          ...defaultHeaders,',
            '          ...(options.headers || {}),',
            '        };',
            '',
            '        // Add auth header if requested',
            '        if (options.includeAuth !== false) {',
            '          const authHeader = getAuthHeader();',
            '          Object.assign(headers, authHeader);',
            '        }',
            '',
            '        // Build request options',
            '        const requestOptions: RequestInit = {',
            '          method: options.method || "GET",',
            '          headers,',
            '          signal,',
            '        };',
            '',
            '        // Add body for non-GET requests',
            '        if (options.body && options.method !== "GET") {',
            '          requestOptions.body =',
            '            typeof options.body === "string"',
            '              ? options.body',
            '              : JSON.stringify(options.body);',
            '        }',
            '',
            '        // Make the request',
            '        const response = await fetch(url, requestOptions);',
            '',
            '        // Parse response based on content type',
            '        const contentType = response.headers.get("content-type");',
            '        let responseData;',
            '',
            '        if (contentType?.includes("application/json")) {',
            '          responseData = await response.json();',
            '        } else {',
            '          responseData = await response.text();',
            '        }',
            '',
            '        if (!response.ok) {',
            '          // Extract error message from response if possible',
            '          const errorMessage =',
            '            typeof responseData === "object" && responseData.detail',
            '              ? responseData.detail',
            '              : response.statusText;',
            '',
            '          throw new Error(errorMessage);',
            '        }',
            '',
            '        setData(responseData);',
            '        setError(null);',
            '      } catch (err: any) {',
            '        // Ignore aborted requests',
            '        if (err.name !== "AbortError") {',
            '          setError(err);',
            '          setData(null);',
            '        }',
            '      } finally {',
            '        setLoading(false);',
            '      }',
            '    };',
            '',
            '    fetchData();',
            '',
            '    return () => {',
            '      controller.abort();',
            '    };',
            '  }, [endpoint, options.method, refetchIndex, JSON.stringify(options.body)]);',
            '',
            '  return { data, error, loading, refetch };',
            '}',
            '',
            '/**',
            ' * Custom hook for paginated API requests',
            ' */',
            'export function usePaginatedApi<T = any>(',
            '  baseEndpoint: string,',
            '  options: ApiRequestOptions = {}',
            ') {',
            '  const [page, setPage] = useState(1);',
            '  const [pageSize, setPageSize] = useState(10);',
            '',
            '  // Build the endpoint with pagination parameters',
            '  const endpoint = `${baseEndpoint}${',
            '    baseEndpoint.includes("?") ? "&" : "?"',
            '  }page=${page}&page_size=${pageSize}`;',
            '',
            '  const response = useApi<{',
            '    count: number;',
            '    next: string | null;',
            '    previous: string | null;',
            '    results: T[];',
            '  }>(endpoint, options);',
            '',
            '  // Calculate total pages',
            '  const totalPages = response.data ? Math.ceil(response.data.count / pageSize) : 0;',
            '',
            '  // Navigation functions',
            '  const goToPage = useCallback(',
            '    (newPage: number) => {',
            '      setPage(Math.max(1, Math.min(newPage, totalPages || 1)));',
            '    },',
            '    [totalPages]',
            '  );',
            '',
            '  const goToNextPage = useCallback(() => {',
            '    if (page < (totalPages || 1)) {',
            '      setPage(p => p + 1);',
            '    }',
            '  }, [page, totalPages]);',
            '',
            '  const goToPreviousPage = useCallback(() => {',
            '    if (page > 1) {',
            '      setPage(p => p - 1);',
            '    }',
            '  }, [page]);',
            '',
            '  // Change page size',
            '  const changePageSize = useCallback((newSize: number) => {',
            '    setPageSize(newSize);',
            '    setPage(1); // Reset to first page when changing page size',
            '  }, []);',
            '',
            '  return {',
            '    ...response,',
            '    results: response.data?.results || [],',
            '    count: response.data?.count || 0,',
            '    page,',
            '    pageSize,',
            '    totalPages,',
            '    goToPage,',
            '    goToNextPage,',
            '    goToPreviousPage,',
            '    changePageSize,',
            '    hasNextPage: page < (totalPages || 1),',
            '    hasPreviousPage: page > 1,',
            '  };',
            '}',
            '',
            '/**',
            ' * Custom hook for creating mutation functions (POST, PUT, PATCH, DELETE)',
            ' */',
            'export function useMutation<TData = any, TVariables = any>(',
            '  endpoint: string,',
            '  method: HttpMethod = "POST",',
            '  options: Omit<ApiRequestOptions, "method" | "body"> = {}',
            ') {',
            '  const { baseUrl, defaultHeaders } = useApiConfig();',
            '  const getAuthHeader = useAuthHeader();',
            '  const [data, setData] = useState<TData | null>(null);',
            '  const [error, setError] = useState<Error | null>(null);',
            '  const [loading, setLoading] = useState(false);',
            '',
            '  const mutate = useCallback(',
            '    async (variables?: TVariables) => {',
            '      setLoading(true);',
            '',
            '      try {',
            '        // Build URL',
            '        const url = endpoint.startsWith("http")',
            '          ? endpoint',
            '          : `${baseUrl}${endpoint.startsWith("/") ? "" : "/"}${endpoint}`;',
            '',
            '        // Build headers',
            '        const headers = {',
            '          ...defaultHeaders,',
            '          ...(options.headers || {}),',
            '        };',
            '',
            '        // Add auth header if requested',
            '        if (options.includeAuth !== false) {',
            '          const authHeader = getAuthHeader();',
            '          Object.assign(headers, authHeader);',
            '        }',
            '',
            '        // Make the request',
            '        const response = await fetch(url, {',
            '          method,',
            '          headers,',
            '          body: variables ? JSON.stringify(variables) : undefined,',
            '          signal: options.signal,',
            '        });',
            '',
            '        // Parse response based on content type',
            '        const contentType = response.headers.get("content-type");',
            '        let responseData = null;',
            '',
            '        if (contentType?.includes("application/json")) {',
            '          responseData = await response.json();',
            '        } else if (response.status !== 204) { // No content',
            '          responseData = await response.text();',
            '        }',
            '',
            '        if (!response.ok) {',
            '          // Extract error message from response if possible',
            '          const errorMessage =',
            '            typeof responseData === "object" && responseData.detail',
            '              ? responseData.detail',
            '              : response.statusText;',
            '',
            '          throw new Error(errorMessage);',
            '        }',
            '',
            '        setData(responseData);',
            '        setError(null);',
            '        return { data: responseData, error: null };',
            '      } catch (err: any) {',
            '        setError(err);',
            '        setData(null);',
            '        return { data: null, error: err };',
            '      } finally {',
            '        setLoading(false);',
            '      }',
            '    },',
            '    [endpoint, method, JSON.stringify(options)]',
            '  );',
            '',
            '  return {',
            '    mutate,',
            '    data,',
            '    error,',
            '    loading,',
            '    reset: () => {',
            '      setData(null);',
            '      setError(null);',
            '    },',
            '  };',
            '}',
            '',
            '/**',
            ' * Hook for file uploads',
            ' */',
            'export function useFileUpload<T = any>(',
            '  endpoint: string,',
            '  options: Omit<ApiRequestOptions, "method" | "body"> = {}',
            ') {',
            '  const { baseUrl } = useApiConfig();',
            '  const getAuthHeader = useAuthHeader();',
            '  const [data, setData] = useState<T | null>(null);',
            '  const [error, setError] = useState<Error | null>(null);',
            '  const [loading, setLoading] = useState(false);',
            '  const [progress, setProgress] = useState(0);',
            '',
            '  const upload = useCallback(',
            '    async (file: File, additionalData?: Record<string, any>) => {',
            '      setLoading(true);',
            '      setProgress(0);',
            '',
            '      try {',
            '        // Build URL',
            '        const url = endpoint.startsWith("http")',
            '          ? endpoint',
            '          : `${baseUrl}${endpoint.startsWith("/") ? "" : "/"}${endpoint}`;',
            '',
            '        // Create FormData',
            '        const formData = new FormData();',
            '        formData.append("file", file);',
            '',
            '        // Add any additional data',
            '        if (additionalData) {',
            '          Object.entries(additionalData).forEach(([key, value]) => {',
            '            formData.append(key, value);',
            '          });',
            '        }',
            '',
            '        // Get auth headers',
            '        const authHeader = options.includeAuth !== false ? getAuthHeader() : {};',
            '',
            '        // Make the request',
            '        const xhr = new XMLHttpRequest();',
            '        xhr.open("POST", url);',
            '',
            '        // Set auth headers if needed',
            '        Object.entries(authHeader).forEach(([key, value]) => {',
            '          xhr.setRequestHeader(key, value);',
            '        });',
            '',
            '        // Track upload progress',
            '        xhr.upload.addEventListener("progress", (event) => {',
            '          if (event.lengthComputable) {',
            '            const percentComplete = (event.loaded / event.total) * 100;',
            '            setProgress(percentComplete);',
            '          }',
            '        });',
            '',
            '        // Handle response',
            '        const responsePromise = new Promise<T>((resolve, reject) => {',
            '          xhr.onload = () => {',
            '            if (xhr.status >= 200 && xhr.status < 300) {',
            '              try {',
            '                const responseData = JSON.parse(xhr.responseText);',
            '                resolve(responseData);',
            '              } catch (e) {',
            '                resolve(xhr.responseText as unknown as T);',
            '              }',
            '            } else {',
            '              reject(new Error(`Upload failed with status ${xhr.status}`));',
            '            }',
            '          };',
            '          xhr.onerror = () => reject(new Error("Network error during upload"));',
            '        });',
            '',
            '        // Send the request',
            '        xhr.send(formData);',
            '',
            '        // Wait for response',
            '        const responseData = await responsePromise;',
            '        setData(responseData);',
            '        setError(null);',
            '        return { data: responseData, error: null };',
            '      } catch (err: any) {',
            '        setError(err);',
            '        setData(null);',
            '        return { data: null, error: err };',
            '      } finally {',
            '        setLoading(false);',
            '      }',
            '    },',
            '    [endpoint, JSON.stringify(options)]',
            '  );',
            '',
            '  return {',
            '    upload,',
            '    data,',
            '    error,',
            '    loading,',
            '    progress,',
            '    reset: () => {',
            '      setData(null);',
            '      setError(null);',
            '      setProgress(0);',
            '    },',
            '  };',
            '}',
            ''
        ]

        # Write the file
        with open(file_path, 'w') as f:
            f.write('\n'.join(content))

        logger.info("Generated base API hooks")

    def _generate_hooks_file(self, endpoints: List[Dict[str, Any]], 
                           app_name: str, auth_info: Dict[str, Any]) -> List[str]:
        """Generate a file with hooks for specific endpoints

        Args:
            endpoints: List of API endpoints
            app_name: Name of the app or group
            auth_info: Authentication information

        Returns:
            List of lines for the hooks file
        """
        content = [
            '/**',
            f' * React hooks for {app_name} API endpoints',
            f' * Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            ' */',
            'import { useApi, useMutation, usePaginatedApi, useFileUpload } from "./use_api";',
            '',
            '// Import TypeScript types',
            'import { PaginatedResponse } from "../typescript/utils";',
            '// You will need to add imports for your specific model interfaces',
        ]

        # Add additional imports based on endpoints
        model_types = set()
        response_types = set()

        for endpoint in endpoints:
            serializer_info = endpoint.get('serializer', {})
            if serializer_info:
                model_info = serializer_info.get('model', {})
                if model_info:
                    model_name = model_info.get('name', '')
                    if model_name:
                        model_types.add(model_name)

        if model_types:
            content.append('')
            content.append('// Example model imports:')
            content.append('// import {')
            for model_type in sorted(model_types):
                content.append(f'//   {model_type},')
            content.append('// } from "../typescript/models";')

        content.append('')

        # Generate hooks for each endpoint
        for endpoint in endpoints:
            hook_content = self._generate_endpoint_hook(endpoint)
            if hook_content:
                content.extend(hook_content)
                content.append('')

        return content

    def _generate_endpoint_hook(self, endpoint: Dict[str, Any]) -> List[str]:
        """Generate a React hook for a specific API endpoint

        Args:
            endpoint: API endpoint information

        Returns:
            List of lines for the hook definition
        """
        result = []

        # Get basic endpoint info
        path = endpoint.get('path', '')
        http_methods = endpoint.get('http_methods', [])
        view_info = endpoint.get('view', {})

        # Skip if no path or methods
        if not path or not http_methods:
            return result

        # Get serializer info for type hints
        serializer_info = endpoint.get('serializer', {})
        model_info = serializer_info.get('model', {}) if serializer_info else {}
        model_name = model_info.get('name', '') if model_info else ''

        # Determine hook type and name
        is_list_endpoint = (
            'list' in view_info.get('name', '').lower() or
            path.endswith('/') and not any(segment.startswith('{') for segment in path.split('/'))
        )

        is_create_endpoint = 'POST' in http_methods and not path.endswith('/')


        # Determine base name for the hook
        base_name = ''
        if view_info.get('name', ''):
            # Extract name from view name
            view_name = view_info.get('name', '')
            base_name = view_name.replace('APIView', '').replace('ViewSet', '').replace('View', '')
        else:
            # Generate from path
            path_segments = [p for p in path.split('/') if p and not p.startswith('{')]
            if path_segments:
                base_name = path_segments[-1].title()

        # Sanity check - use default if we couldn't determine a name
        if not base_name:
            base_name = 'Api'

        # Generate documentation comment
        result.append('/**')
        result.append(f' * Hook for {", ".join(method.upper() for method in http_methods)} {path}')

        # Add description from docstring if available
        docstring = view_info.get('docstring', '')
        if docstring:
            for line in docstring.split('\n'):
                if line.strip():
                    result.append(f' * {line.strip()}')

        result.append(' */')

        # Create different hooks based on endpoint characteristics
        if is_list_endpoint:
            # Paginated list endpoint
            hook_name = f'use{base_name}List'
            model_type = model_name or 'any'

            result.append(f'export function {hook_name}(options = {{}} ) {{')
            result.append(f'  return usePaginatedApi<{model_type}>(`{path}`, options);')
            result.append('}')

            # Also add a function to get all items (unpaginated)
            result.append('')
            result.append(f'export function useAll{base_name}s(options = {{}} ) {{')
            result.append('  const [allItems, setAllItems] = useState<any[]>([]);')
            result.append('  const [loading, setLoading] = useState(true);')
            result.append('  const [error, setError] = useState<Error | null>(null);')
            result.append('  const { baseUrl } = useApiConfig();')
            result.append('  const getAuthHeader = useAuthHeader();')
            result.append('')
            result.append('  useEffect(() => {')
            result.append('    const fetchAllItems = async () => {')
            result.append('      setLoading(true);')
            result.append('      try {')
            result.append('        let nextUrl = `${baseUrl}${path.startsWith("/") ? "" : "/"}${path}`;')
            result.append('        const items: any[] = [];')
            result.append('')
            result.append('        while (nextUrl) {')
            result.append('          const headers = {')
            result.append('            ...options.headers,')
            result.append('            ...getAuthHeader(),')
            result.append('          };')
            result.append('')
            result.append('          const response = await fetch(nextUrl, { headers });')
            result.append('          if (!response.ok) throw new Error("Failed to fetch data");')
            result.append('')
            result.append('          const data = await response.json();')
            result.append('          items.push(...data.results);')
            result.append('          nextUrl = data.next;')
            result.append('        }')
            result.append('')
            result.append('        setAllItems(items);')
            result.append('        setError(null);')
            result.append('      } catch (err: any) {')
            result.append('        setError(err);')
            result.append('      } finally {')
            result.append('        setLoading(false);')
            result.append('      }')
            result.append('    };')
            result.append('')
            result.append('    fetchAllItems();')
            result.append('  }, [baseUrl, JSON.stringify(options)]);')
            result.append('')
            result.append('  return { data: allItems, loading, error };')
            result.append('}')

        # For detail endpoint with GET
        if ('GET' in http_methods and any('{' in segment for segment in path.split('/'))):
            # Detail endpoint hook
            hook_name = f'use{base_name}Detail'
            model_type = model_name or 'any'

            # Extract ID parameter
            id_segment = next((s for s in path.split('/') if '{' in s), '{id}')
            id_param = id_segment.strip('{}')

            result.append('')
            result.append(f'export function {hook_name}(')
            result.append(f'  {id_param}: string | number,')
            result.append('  options = {}')
            result.append(') {')

            # Replace parameter in path
            param_path = path.replace(id_segment, `${id_param}`)

            result.append(f'  return useApi<{model_type}>(`{param_path}`, options);')
            result.append('}')

        # For create endpoint with POST
        if 'POST' in http_methods and (is_create_endpoint or '/create/' in path):
            hook_name = f'useCreate{base_name}'
            result.append('')
            result.append(f'export function {hook_name}(options = {{}}) {{')
            result.append(f'  return useMutation(`{path}`, "POST", options);')
            result.append('}')

        # For update endpoint with PUT or PATCH
        if ('PUT' in http_methods or 'PATCH' in http_methods) and any('{' in segment for segment in path.split('/')):
            # Extract ID parameter
            id_segment = next((s for s in path.split('/') if '{' in s), '{id}')
            id_param = id_segment.strip('{}')

            # Create update hook
            method = 'PUT' if 'PUT' in http_methods else 'PATCH'
            hook_name = f'useUpdate{base_name}'

            result.append('')
            result.append(f'export function {hook_name}(')
            result.append(f'  {id_param}: string | number,')
            result.append('  options = {}')
            result.append(') {')

            # Replace parameter in path
            param_path = path.replace(id_segment, `${id_param}`)

            result.append(f'  return useMutation(`{param_path}`, "{method}", options);')
            result.append('}')

        # For delete endpoint with DELETE
        if 'DELETE' in http_methods and any('{' in segment for segment in path.split('/')):
            # Extract ID parameter
            id_segment = next((s for s in path.split('/') if '{' in s), '{id}')
            id_param = id_segment.strip('{}')

            # Create delete hook
            hook_name = f'useDelete{base_name}'

            result.append('')
            result.append(f'export function {hook_name}(')
            result.append(f'  {id_param}: string | number,')
            result.append('  options = {}')
            result.append(') {')

            # Replace parameter in path
            param_path = path.replace(id_segment, `${id_param}`)

            result.append(f'  return useMutation(`{param_path}`, "DELETE", options);')
            result.append('}')

        # For file upload endpoints
        if 'file_upload' in endpoint.get('tags', []) or any('file' in field.lower() for field in serializer_info.get('fields', {}).keys()):
            hook_name = f'useUpload{base_name}'

            result.append('')
            result.append(f'export function {hook_name}(options = {{}}) {{')
            result.append(f'  return useFileUpload(`{path}`, options);')
            result.append('}')

        return result

    def _generate_jwt_auth_hooks(self) -> List[str]:
        """Generate JWT authentication hooks

        Returns:
            List of lines for JWT auth hooks
        """
        return [
            '/**',
            ' * JWT Authentication utilities',
            ' */',
            'export interface JWTTokens {',
            '  access: string;',
            '  refresh: string;',
            '}',
            '',
            '/**',
            ' * Hook to manage JWT authentication state',
            ' */',
            'export function useAuth() {',
            '  const [tokens, setTokens] = useState<JWTTokens | null>(() => {',
            '    // Load tokens from localStorage on init',
            '    const storedAccess = localStorage.getItem("jwt_access_token");',
            '    const storedRefresh = localStorage.getItem("jwt_refresh_token");',
            '    return storedAccess && storedRefresh',
            '      ? { access: storedAccess, refresh: storedRefresh }',
            '      : null;',
            '  });',
            '',
            '  const { baseUrl } = useApiConfig();',
            '',
            '  const isAuthenticated = Boolean(tokens?.access);',
            '',
            '  // Log in function',
            '  const login = useCallback(',
            '    async (username: string, password: string) => {',
            '      try {',
            '        const response = await fetch(`${baseUrl}/api/token/`, {',
            '          method: "POST",',
            '          headers: {',
            '            "Content-Type": "application/json",',
            '          },',
            '          body: JSON.stringify({ username, password }),',
            '        });',
            '',
            '        if (!response.ok) {',
            '          throw new Error("Login failed");',
            '        }',
            '',
            '        const data = await response.json();',
            '        setTokens({ access: data.access, refresh: data.refresh });',
            '',
            '        // Store tokens in localStorage',
            '        localStorage.setItem("jwt_access_token", data.access);',
            '        localStorage.setItem("jwt_refresh_token", data.refresh);',
            '',
            '        return true;',
            '      } catch (error) {',
            '        console.error("Login error:", error);',
            '        return false;',
            '      }',
            '    },',
            '    [baseUrl]',
            '  );',
            '',
            '  // Log out function',
            '  const logout = useCallback(() => {',
            '    setTokens(null);',
            '    localStorage.removeItem("jwt_access_token");',
            '    localStorage.removeItem("jwt_refresh_token");',
            '  }, []);',
            '',
            '  // Refresh token function',
            '  const refreshToken = useCallback(async () => {',
            '    if (!tokens?.refresh) return false;',
            '',
            '    try {',
            '      const response = await fetch(`${baseUrl}/api/token/refresh/`, {',
            '        method: "POST",',
            '        headers: {',
            '          "Content-Type": "application/json",',
            '        },',
            '        body: JSON.stringify({ refresh: tokens.refresh }),',
            '      });',
            '',
            '      if (!response.ok) {',
            '        throw new Error("Token refresh failed");',
            '      }',
            '',
            '      const data = await response.json();',
            '      const newTokens = {',
            '        ...tokens,',
            '        access: data.access,',
            '      };',
            '',
            '      setTokens(newTokens);',
            '      localStorage.setItem("jwt_access_token", data.access);',
            '',
            '      return true;',
            '    } catch (error) {',
            '      console.error("Token refresh error:", error);',
            '      logout(); // Clear invalid tokens',
            '      return false;',
            '    }',
            '  }, [tokens, baseUrl, logout]);',
            '',
            '  return {',
            '    tokens,',
            '    isAuthenticated,',
            '    login,',
            '    logout,',
            '    refreshToken,',
            '  };',
            '}',
            '',
            '/**',
            ' * Hook to get authentication header for API requests',
            ' */',
            'export function useAuthHeader() {',
            '  const { tokens } = useAuth();',
            '',
            '  return useCallback(() => {',
            '    return tokens?.access',
            '      ? { Authorization: `Bearer ${tokens.access}` }',
            '      : {};',
            '  }, [tokens]);',
            '}',
            '',
        ]

    def _generate_token_auth_hooks(self) -> List[str]:
        """Generate token authentication hooks

        Returns:
            List of lines for token auth hooks
        """
        return [
            '/**',
            ' * Token Authentication utilities',
            ' */',
            '/**',
            ' * Hook to manage token authentication state',
            ' */',
            'export function useAuth() {',
            '  const [token, setToken] = useState<string | null>(() => {',
            '    // Load token from localStorage on init',
            '    return localStorage.getItem("auth_token");',
            '  });',
            '',
            '  const { baseUrl } = useApiConfig();',
            '',
            '  const isAuthenticated = Boolean(token);',
            '',
            '  // Log in function',
            '  const login = useCallback(',
            '    async (username: string, password: string) => {',
            '      try {',
            '        const response = await fetch(`${baseUrl}/api/auth-token/`, {',
            '          method: "POST",',
            '          headers: {',
            '            "Content-Type": "application/json",',
            '          },',
            '          body: JSON.stringify({ username, password }),',
            '        });',
            '',
            '        if (!response.ok) {',
            '          throw new Error("Login failed");',
            '        }',
            '',
            '        const data = await response.json();',
            '        setToken(data.token);',
            '',
            '        // Store token in localStorage',
            '        localStorage.setItem("auth_token", data.token);',
            '',
            '        return true;',
            '      } catch (error) {',
            '        console.error("Login error:", error);',
            '        return false;',
            '      }',
            '    },',
            '    [baseUrl]',
            '  );',
            '',
            '  // Log out function',
            '  const logout = useCallback(() => {',
            '    setToken(null);',
            '    localStorage.removeItem("auth_token");',
            '  }, []);',
            '',
            '  return {',
            '    token,',
            '    isAuthenticated,',
            '    login,',
            '    logout,',
            '  };',
            '}',
            '',
            '/**',
            ' * Hook to get authentication header for API requests',
            ' */',
            'export function useAuthHeader() {',
            '  const { token } = useAuth();',
            '',
            '  return useCallback(() => {',
            '    return token ? { Authorization: `Token ${token}` } : {};',
            '  }, [token]);',
            '}',
            '',
        ]

    def _generate_session_auth_hooks(self) -> List[str]:
        """Generate session authentication hooks

        Returns:
            List of lines for session auth hooks
        """
        return [
            '/**',
            ' * Session Authentication utilities',
            ' */',
            '/**',
            ' * Hook to manage session authentication state',
            ' */',
            'export function useAuth() {',
            '  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => {',
            '    // Check if user data exists in localStorage as an indicator of authentication',
            '    return localStorage.getItem("user_data") !== null;',
            '  });',
            '',
            '  const [userData, setUserData] = useState<any>(() => {',
            '    const stored = localStorage.getItem("user_data");',
            '    return stored ? JSON.parse(stored) : null;',
            '  });',
            '',
            '  const { baseUrl } = useApiConfig();',
            '',
            '  // Log in function',
            '  const login = useCallback(',
            '    async (username: string, password: string) => {',
            '      try {',
            '        const response = await fetch(`${baseUrl}/accounts/login/`, {',
            '          method: "POST",',
            '          headers: {',
            '            "Content-Type": "application/json",',
            '          },',
            '          body: JSON.stringify({ username, password }),',
            '          credentials: "include", // Important for cookies',
            '        });',
            '',
            '        if (!response.ok) {',
            '          throw new Error("Login failed");',
            '        }',
            '',
            '        // Fetch user data after successful login',
            '        const userResponse = await fetch(`${baseUrl}/accounts/user/`, {',
            '          credentials: "include",',
            '        });',
            '',
            '        if (userResponse.ok) {',
            '          const userData = await userResponse.json();',
            '          setUserData(userData);',
            '          localStorage.setItem("user_data", JSON.stringify(userData));',
            '        }',
            '',
            '        setIsAuthenticated(true);',
            '        return true;',
            '      } catch (error) {',
            '        console.error("Login error:", error);',
            '        return false;',
            '      }',
            '    },',
            '    [baseUrl]',
            '  );',
            '',
            '  // Log out function',
            '  const logout = useCallback(async () => {',
            '    try {',
            '      await fetch(`${baseUrl}/accounts/logout/`, {',
            '        method: "POST",',
            '        credentials: "include",',
            '      });',
            '    } catch (error) {',
            '      console.error("Logout error:", error);',
            '    } finally {',
            '      setIsAuthenticated(false);',
            '      setUserData(null);',
            '      localStorage.removeItem("user_data");',
            '    }',
            '  }, [baseUrl]);',
            '',
            '  return {',
            '    isAuthenticated,',
            '    userData,',
            '    login,',
            '    logout,',
            '  };',
            '}',
            '',
            '/**',
            ' * Hook to get authentication header for API requests',
            ' * With session auth, we don\'t need headers but include credentials instead',
            ' */',
            'export function useAuthHeader() {',
            '  // For session auth, we don\'t need auth headers because cookies are sent automatically',
            '  // But we include the hook for API consistency with other auth methods',
            '  return useCallback(() => ({}), []);',
            '}',
            '',
        ]

    def _generate_default_auth_hooks(self) -> List[str]:
        """Generate default authentication hooks when method is unknown

        Returns:
            List of lines for default auth hooks
        """
        return [
            '/**',
            ' * Authentication utilities',
            ' * Note: Configure these hooks based on your actual authentication method',
            ' */',
            '/**',
            ' * Hook to manage authentication state',
            ' */',
            'export function useAuth() {',
            '  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);',
            '  const [authData, setAuthData] = useState<any>(null);',
            '',
            '  const { baseUrl } = useApiConfig();',
            '',
            '  // Example login function - modify to match your backend auth endpoints',
            '  const login = useCallback(',
            '    async (username: string, password: string) => {',
            '      try {',
            '        // Replace with your actual login endpoint',
            '        const response = await fetch(`${baseUrl}/api/login/`, {',
            '          method: "POST",',
            '          headers: {',
            '            "Content-Type": "application/json",',
            '          },',
            '          body: JSON.stringify({ username, password }),',
            '        });',
            '',
            '        if (!response.ok) {',
            '          throw new Error("Login failed");',
            '        }',
            '',
            '        const data = await response.json();',
            '        setAuthData(data);',
            '        setIsAuthenticated(true);',
            '',
            '        // Store auth data in localStorage or elsewhere as needed',
            '',
            '        return true;',
            '      } catch (error) {',
            '        console.error("Login error:", error);',
            '        return false;',
            '      }',
            '    },',
            '    [baseUrl]',
            '  );',
            '',
            '  // Log out function',
            '  const logout = useCallback(() => {',
            '    setIsAuthenticated(false);',
            '    setAuthData(null);',
            '    // Clear stored auth data as needed',
            '  }, []);',
            '',
            '  return {',
            '    isAuthenticated,',
            '    authData,',
            '    login,',
            '    logout,',
            '  };',
            '}',
            '',
            '/**',
            ' * Hook to get authentication header for API requests',
            ' * Modify this to return the correct auth header format for your API',
            ' */',
            'export function useAuthHeader() {',
            '  const { authData } = useAuth();',
            '',
            '  return useCallback(() => {',
            '    // Modify this to return the correct auth header format',
            '    // Example: return authData?.token ? { Authorization: `Bearer ${authData.token}` } : {};',
            '    return {};',
            '  }, [authData]);',
            '}',
            '',
        ]

    def _generate_readme(self, output_dir: Path) -> None:
        """Generate a README.md file with usage examples

        Args:
            output_dir: Directory where React hook files are generated
        """
        readme_path = output_dir / 'README.md'

        content = [
            '# React Hooks for API Integration',
            '',
            'This directory contains React hooks for integrating with the backend API.',
            '',
            '## Getting Started',
            '',
            'First, wrap your application with the `ApiProvider` to configure the base URL:',
            '',
            '```tsx',
            'import { ApiProvider } from "./hooks";',
            '',
            'function App() {',
            '  return (',
            '    <ApiProvider baseUrl="https://api.example.com">',
            '      <YourApp />',
            '    </ApiProvider>',
            '  );',
            '}',
            '```',
            '',
            '## Authentication',
            '',
            'Use the authentication hooks to manage user login/logout:',
            '',
            '```tsx',
            'import { useAuth } from "./hooks";',
            '',
            'function LoginForm() {',
            '  const { login, isAuthenticated, logout } = useAuth();',
            '  const [username, setUsername] = useState("");',
            '  const [password, setPassword] = useState("");',
            '',
            '  const handleLogin = async (e) => {',
            '    e.preventDefault();',
            '    await login(username, password);',
            '  };',
            '',
            '  return (',
            '    <div>',
            '      {isAuthenticated ? (',
            '        <button onClick={logout}>Log Out</button>',
            '      ) : (',
            '        <form onSubmit={handleLogin}>',
            '          {/* Form fields */}',
            '          <button type="submit">Log In</button>',
            '        </form>',
            '      )}',
            '    </div>',
            '  );',
            '}',
            '```',
            '',
            '## Basic API Requests',
            '',
            'Use the generated hooks to fetch data:',
            '',
            '```tsx',
            'import { useUserList, useUserDetail } from "./hooks";',
            '',
            'function UserList() {',
            '  const { results, loading, error, page, totalPages, goToPage } = useUserList();',
            '',
            '  if (loading) return <p>Loading...</p>;',
            '  if (error) return <p>Error: {error.message}</p>;',
            '',
            '  return (',
            '    <div>',
            '      <ul>',
            '        {results.map(user => (',
            '          <li key={user.id}>{user.username}</li>',
            '        ))}',
            '      </ul>',
            '      <div>',
            '        Page {page} of {totalPages}',
            '        <button',
            '          disabled={page === 1}',
            '          onClick={() => goToPage(page - 1)}',
            '        >',
            '          Previous',
            '        </button>',
            '        <button',
            '          disabled={page === totalPages}',
            '          onClick={() => goToPage(page + 1)}',
            '        >',
            '          Next',
            '        </button>',
            '      </div>',
            '    </div>',
            '  );',
            '}',
            '',
            'function UserDetail({ userId }) {',
            '  const { data, loading, error } = useUserDetail(userId);',
            '',
            '  if (loading) return <p>Loading...</p>;',
            '  if (error) return <p>Error: {error.message}</p>;',
            '  if (!data) return <p>User not found</p>;',
            '',
            '  return (',
            '    <div>',
            '      <h2>{data.username}</h2>',
            '      <p>Email: {data.email}</p>',
            '    </div>',
            '  );',
            '}',
            '```',
            '',
            '## Mutations (Create, Update, Delete)',
            '',
            'Use mutation hooks for data modifications:',
            '',
            '```tsx',
            'import { useCreateUser, useUpdateUser, useDeleteUser } from "./hooks";',
            '',
            'function CreateUserForm() {',
            '  const { mutate, loading, error } = useCreateUser();',
            '  const [formData, setFormData] = useState({ username: "", email: "" });',
            '',
            '  const handleSubmit = async (e) => {',
            '    e.preventDefault();',
            '    const result = await mutate(formData);',
            '    if (result.data) {',
            '      // Success handling',
            '    }',
            '  };',
            '',
            '  return (',
            '    <form onSubmit={handleSubmit}>',
            '      {/* Form fields */}',
            '      <button type="submit" disabled={loading}>',
            '        {loading ? "Creating..." : "Create User"}',
            '      </button>',
            '      {error && <p>Error: {error.message}</p>}',
            '    </form>',
            '  );',
            '}',
            '',
            'function UpdateUserForm({ userId }) {',
            '  const { mutate, loading } = useUpdateUser(userId);',
            '  // Implementation similar to create form',
            '}',
            '',
            'function DeleteUserButton({ userId }) {',
            '  const { mutate, loading } = useDeleteUser(userId);',
            '',
            '  const handleDelete = async () => {',
            '    if (confirm("Are you sure you want to delete this user?")) {',
            '      await mutate();',
            '    }',
            '  };',
            '',
            '  return (',
            '    <button onClick={handleDelete} disabled={loading}>',
            '      {loading ? "Deleting..." : "Delete User"}',
            '    </button>',
            '  );',
            '}',
            '```',
            '',
            '## File Uploads',
            '',
            'Use the file upload hook for handling file uploads:',
            '',
            '```tsx',
            'import { useUploadProfileImage } from "./hooks";',
            '',
            'function ImageUploader() {',
            '  const { upload, progress, loading, error, data } = useUploadProfileImage();',
            '',
            '  const handleFileChange = async (e) => {',
            '    const file = e.target.files[0];',
            '    if (file) {',
            '      await upload(file, { user_id: 123 });',
            '    }',
            '  };',
            '',
            '  return (',
            '    <div>',
            '      <input type="file" onChange={handleFileChange} disabled={loading} />',
            '      {progress > 0 && progress < 100 && (',
            '        <progress value={progress} max="100" />',
            '      )}',
            '      {error && <p>Error: {error.message}</p>}',
            '      {data && <img src={data.url} alt="Uploaded" />}',
            '    </div>',
            '  );',
            '}',
            '```',
            '',
            '## Custom API Requests',
            '',
            'For endpoints without specific hooks, use the base hooks:',
            '',
            '```tsx',
            'import { useApi, useMutation } from "./hooks/use_api";',
            '',
            'function CustomApiComponent() {',
            '  const { data, loading, error } = useApi("/custom/endpoint");',
            '  const { mutate } = useMutation("/custom/action", "POST");',
            '',
            '  // Implementation as needed',
            '}',
            '```',
        ]

        with open(readme_path, 'w') as f:
            f.write('\n'.join(content))

        logger.info("Generated README.md with usage examples")
# END OF CODE