/**
 * File: frontend/src/courseBuilder/utils/generateTempId.ts
 * Version: 2.1.0
 * Date Created: 2025-06-14 16:05:29
 * Date Revised: 2025-06-14 16:05:29 UTC
 * Current User: sujibeautysalon
 * Last Modified By: sujibeautysalon
 *
 * Enhanced Temporary ID Generation Utility with SSR Compatibility
 *
 * This utility provides robust temporary ID generation for optimistic UI updates
 * before server persistence. It includes comprehensive fallback strategies,
 * environment detection, and performance optimizations.
 *
 * Key Features:
 * - SSR compatibility with proper environment detection
 * - Multiple fallback strategies for missing crypto APIs
 * - Performance optimizations with caching and validation
 * - Comprehensive type safety with proper guards
 * - Collision detection and prevention mechanisms
 * - Testing utilities for development and debugging
 *
 * Version 2.1.0 Changes (Surgical Fixes from Code Review):
 * - FIXED: SSR compatibility with environment detection
 * - FIXED: Enhanced fallback strategies for missing crypto APIs
 * - FIXED: Type safety with proper guards and validation
 * - FIXED: Performance optimizations with caching mechanisms
 * - FIXED: Collision detection and prevention
 * - FIXED: Comprehensive error handling with graceful degradation
 * - FIXED: Testing utilities and debugging helpers
 * - FIXED: Memory management and cleanup mechanisms
 *
 * Connected Files:
 * - frontend/src/courseBuilder/store/courseSlice.ts - Uses temp IDs for state management
 * - frontend/src/courseBuilder/components/ModuleCard.tsx - Temp IDs for new modules
 * - frontend/src/courseBuilder/components/LessonCard.tsx - Temp IDs for new lessons
 * - frontend/src/courseBuilder/api/courseBuilderAPI.ts - Filters temp IDs before API calls
 */

// ✅ FIX 1: Enhanced type definitions
export type TempId = `temp_${string}`;
export type PermanentId = number | string;
export type AnyId = TempId | PermanentId;

// ✅ FIX 2: Environment detection interface
interface CryptoSupport {
    hasRandomUUID: boolean;
    hasGetRandomValues: boolean;
    hasSubtle: boolean;
    environment: 'browser' | 'node' | 'webworker' | 'unknown';
}

// ✅ FIX 3: Performance tracking interface
interface IdGenerationStats {
    totalGenerated: number;
    methodsUsed: Record<string, number>;
    collisions: number;
    lastGenerated: number;
}

// ✅ FIX 4: Configuration interface
interface TempIdConfig {
    prefix: string;
    enableCollisionDetection: boolean;
    maxCacheSize: number;
    enablePerformanceTracking: boolean;
    fallbackMethods: ('crypto' | 'timestamp' | 'random' | 'counter')[];
}

// ✅ FIX 5: Internal state management
class TempIdGenerator {
    private static instance: TempIdGenerator;
    private generatedIds = new Set<string>();
    private counter = 0;
    private stats: IdGenerationStats;
    private config: TempIdConfig;
    private cryptoSupport: CryptoSupport;

    private constructor() {
        this.stats = {
            totalGenerated: 0,
            methodsUsed: {},
            collisions: 0,
            lastGenerated: 0,
        };

        this.config = {
            prefix: 'temp_',
            enableCollisionDetection: true,
            maxCacheSize: 10000,
            enablePerformanceTracking: false,
            fallbackMethods: ['crypto', 'timestamp', 'random', 'counter'],
        };

        this.cryptoSupport = this.detectCryptoSupport();
    }

    public static getInstance(): TempIdGenerator {
        if (!TempIdGenerator.instance) {
            TempIdGenerator.instance = new TempIdGenerator();
        }
        return TempIdGenerator.instance;
    }

    // ✅ FIX 6: Comprehensive environment detection
    private detectCryptoSupport(): CryptoSupport {
        const support: CryptoSupport = {
            hasRandomUUID: false,
            hasGetRandomValues: false,
            hasSubtle: false,
            environment: 'unknown',
        };

        // Detect environment
        if (typeof window !== 'undefined') {
            support.environment = 'browser';
        } else if (typeof global !== 'undefined' && global.process?.versions?.node) {
            support.environment = 'node';
        } else if (typeof self !== 'undefined' && typeof importScripts === 'function') {
            support.environment = 'webworker';
        }

        // Check crypto API availability
        try {
            if (typeof crypto !== 'undefined') {
                // Check for randomUUID (modern browsers and Node 16+)
                if (typeof crypto.randomUUID === 'function') {
                    try {
                        crypto.randomUUID();
                        support.hasRandomUUID = true;
                    } catch (e) {
                        // Function exists but might not be available in current context
                    }
                }

                // Check for getRandomValues
                if (typeof crypto.getRandomValues === 'function') {
                    try {
                        crypto.getRandomValues(new Uint32Array(1));
                        support.hasGetRandomValues = true;
                    } catch (e) {
                        // Function exists but might not be available in current context
                    }
                }

                // Check for subtle crypto
                if (crypto.subtle) {
                    support.hasSubtle = true;
                }
            }
        } catch (e) {
            // Crypto API not available
        }

        return support;
    }

    // ✅ FIX 7: Multiple ID generation strategies
    private generateWithCrypto(): string | null {
        if (!this.cryptoSupport.hasRandomUUID) return null;

        try {
            const uuid = crypto.randomUUID();
            this.updateStats('crypto');
            return `${this.config.prefix}${uuid}`;
        } catch (error) {
            console.warn('Failed to generate crypto UUID:', error);
            return null;
        }
    }

    private generateWithCryptoRandom(): string | null {
        if (!this.cryptoSupport.hasGetRandomValues) return null;

        try {
            const array = new Uint32Array(4);
            crypto.getRandomValues(array);
            const uuid = Array.from(array, (num) => num.toString(16).padStart(8, '0')).join('-');
            this.updateStats('crypto');
            return `${this.config.prefix}${uuid}`;
        } catch (error) {
            console.warn('Failed to generate crypto random:', error);
            return null;
        }
    }

    private generateWithTimestamp(): string {
        const timestamp = Date.now();
        const random = Math.random().toString(36).substring(2, 9);
        const microtime = performance?.now ? performance.now().toString(36).substring(2, 6) : '';
        this.updateStats('timestamp');
        return `${this.config.prefix}${timestamp}_${random}${microtime}`;
    }

    private generateWithRandom(): string {
        const random1 = Math.random().toString(36).substring(2, 11);
        const random2 = Math.random().toString(36).substring(2, 11);
        const timestamp = Date.now().toString(36);
        this.updateStats('random');
        return `${this.config.prefix}${timestamp}_${random1}_${random2}`;
    }

    private generateWithCounter(): string {
        this.counter = (this.counter + 1) % Number.MAX_SAFE_INTEGER;
        const timestamp = Date.now();
        const random = Math.random().toString(36).substring(2, 6);
        this.updateStats('counter');
        return `${this.config.prefix}${timestamp}_${this.counter}_${random}`;
    }

    // ✅ FIX 8: Collision detection and prevention
    private ensureUnique(id: string): string {
        if (!this.config.enableCollisionDetection) {
            return id;
        }

        let uniqueId = id;
        let attempts = 0;
        const maxAttempts = 10;

        while (this.generatedIds.has(uniqueId) && attempts < maxAttempts) {
            this.stats.collisions++;
            const suffix = Math.random().toString(36).substring(2, 6);
            uniqueId = `${id}_${suffix}`;
            attempts++;
        }

        if (attempts === maxAttempts) {
            // Final fallback with timestamp
            uniqueId = `${id}_${Date.now()}_${Math.random().toString(36).substring(2, 4)}`;
        }

        return uniqueId;
    }

    // ✅ FIX 9: Cache management
    private addToCache(id: string): void {
        if (this.generatedIds.size >= this.config.maxCacheSize) {
            // Remove oldest entries (simple FIFO)
            const idsToRemove = Array.from(this.generatedIds).slice(0, Math.floor(this.config.maxCacheSize * 0.1));
            idsToRemove.forEach(oldId => this.generatedIds.delete(oldId));
        }

        this.generatedIds.add(id);
    }

    // ✅ FIX 10: Statistics tracking
    private updateStats(method: string): void {
        if (!this.config.enablePerformanceTracking) return;

        this.stats.totalGenerated++;
        this.stats.methodsUsed[method] = (this.stats.methodsUsed[method] || 0) + 1;
        this.stats.lastGenerated = Date.now();
    }

    // ✅ FIX 11: Main generation method with fallback chain
    public generate(): TempId {
        const startTime = performance?.now ? performance.now() : Date.now();
        let id: string | null = null;

        // Try each configured method in order
        for (const method of this.config.fallbackMethods) {
            switch (method) {
                case 'crypto':
                    id = this.generateWithCrypto() || this.generateWithCryptoRandom();
                    break;
                case 'timestamp':
                    id = this.generateWithTimestamp();
                    break;
                case 'random':
                    id = this.generateWithRandom();
                    break;
                case 'counter':
                    id = this.generateWithCounter();
                    break;
            }

            if (id) break;
        }

        // Ultimate fallback
        if (!id) {
            id = `${this.config.prefix}fallback_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
            this.updateStats('fallback');
        }

        // Ensure uniqueness
        const uniqueId = this.ensureUnique(id);
        this.addToCache(uniqueId);

        // Performance tracking
        if (this.config.enablePerformanceTracking && performance?.now) {
            const duration = performance.now() - startTime;
            if (duration > 1) {
                console.warn(`Slow temp ID generation: ${duration.toFixed(2)}ms`);
            }
        }

        return uniqueId as TempId;
    }

    // ✅ FIX 12: Configuration methods
    public configure(newConfig: Partial<TempIdConfig>): void {
        this.config = { ...this.config, ...newConfig };
    }

    public getStats(): Readonly<IdGenerationStats> {
        return { ...this.stats };
    }

    public getCryptoSupport(): Readonly<CryptoSupport> {
        return { ...this.cryptoSupport };
    }

    // ✅ FIX 13: Cache management methods
    public clearCache(): void {
        this.generatedIds.clear();
    }

    public getCacheSize(): number {
        return this.generatedIds.size;
    }

    public isInCache(id: string): boolean {
        return this.generatedIds.has(id);
    }

    // ✅ FIX 14: Testing and debugging utilities
    public enablePerformanceTracking(): void {
        this.config.enablePerformanceTracking = true;
    }

    public disablePerformanceTracking(): void {
        this.config.enablePerformanceTracking = false;
    }

    public resetStats(): void {
        this.stats = {
            totalGenerated: 0,
            methodsUsed: {},
            collisions: 0,
            lastGenerated: 0,
        };
    }
}

// ✅ FIX 15: Public API functions

/**
 * Generate a unique temporary ID with comprehensive fallback strategies
 * Uses crypto.randomUUID() when available, with multiple fallback methods
 *
 * @returns A unique temporary ID string prefixed with 'temp_'
 *
 * @example
 * ```typescript
 * const tempId = generateTempId();
 * console.log(tempId); // "temp_123e4567-e89b-12d3-a456-426614174000"
 * ```
 */
export const generateTempId = (): TempId => {
    return TempIdGenerator.getInstance().generate();
};

/**
 * Check if an ID is a temporary ID
 *
 * @param id - The ID to check (can be string or number)
 * @returns True if the ID is a temporary ID, false otherwise
 *
 * @example
 * ```typescript
 * isTempId('temp_123'); // true
 * isTempId(123); // false
 * isTempId('regular_id'); // false
 * ```
 */
export const isTempId = (id: AnyId): id is TempId => {
    return typeof id === 'string' && id.startsWith('temp_');
};

/**
 * Validate that a temporary ID is properly formatted
 *
 * @param id - The ID to validate
 * @returns True if valid temporary ID format, false otherwise
 */
export const isValidTempId = (id: string): id is TempId => {
    if (!isTempId(id)) return false;

    // Check minimum length (prefix + some content)
    if (id.length < 10) return false;

    // Check for valid characters (alphanumeric, hyphens, underscores)
    const validPattern = /^temp_[a-zA-Z0-9_-]+$/;
    return validPattern.test(id);
};

/**
 * Extract the non-temporary part of a temp ID
 *
 * @param tempId - The temporary ID
 * @returns The ID without the 'temp_' prefix
 */
export const extractTempIdCore = (tempId: TempId): string => {
    return tempId.replace(/^temp_/, '');
};

/**
 * Filter out temporary IDs from an array of IDs
 * Useful for API calls that shouldn't include temporary IDs
 *
 * @param ids - Array of IDs (mixed temporary and permanent)
 * @returns Array containing only permanent IDs
 *
 * @example
 * ```typescript
 * const mixed = ['temp_123', 456, 'temp_789', 'permanent'];
 * const permanent = filterTempIds(mixed); // [456, 'permanent']
 * ```
 */
export const filterTempIds = <T extends AnyId>(ids: T[]): Exclude<T, TempId>[] => {
    return ids.filter((id): id is Exclude<T, TempId> => !isTempId(id));
};

/**
 * Filter to get only temporary IDs from an array
 *
 * @param ids - Array of IDs (mixed temporary and permanent)
 * @returns Array containing only temporary IDs
 */
export const filterOnlyTempIds = <T extends AnyId>(ids: T[]): TempId[] => {
    return ids.filter((id): id is TempId => isTempId(id));
};

/**
 * Replace temporary IDs in an array with permanent IDs
 *
 * @param ids - Array of IDs that may contain temporary IDs
 * @param tempToPermanentMap - Map from temporary ID to permanent ID
 * @returns Array with temporary IDs replaced by permanent IDs
 */
export const replaceTempIds = <T extends AnyId>(
    ids: T[],
    tempToPermanentMap: Map<TempId, PermanentId>
): (PermanentId | Exclude<T, TempId>)[] => {
    return ids.map(id => {
        if (isTempId(id) && tempToPermanentMap.has(id)) {
            return tempToPermanentMap.get(id)!;
        }
        return id as Exclude<T, TempId>;
    });
};

// ✅ FIX 16: Configuration and utility functions

/**
 * Configure the temp ID generator
 *
 * @param config - Configuration options
 */
export const configureTempIdGenerator = (config: Partial<TempIdConfig>): void => {
    TempIdGenerator.getInstance().configure(config);
};

/**
 * Get generation statistics (only available when performance tracking is enabled)
 *
 * @returns Statistics about ID generation
 */
export const getTempIdStats = (): Readonly<IdGenerationStats> => {
    return TempIdGenerator.getInstance().getStats();
};

/**
 * Get information about crypto support in current environment
 *
 * @returns Information about available crypto APIs
 */
export const getCryptoSupport = (): Readonly<CryptoSupport> => {
    return TempIdGenerator.getInstance().getCryptoSupport();
};

/**
 * Clear the internal cache of generated IDs
 * Useful for testing or memory management
 */
export const clearTempIdCache = (): void => {
    TempIdGenerator.getInstance().clearCache();
};

/**
 * Check if a specific ID is in the generation cache
 *
 * @param id - The ID to check
 * @returns True if ID is in cache, false otherwise
 */
export const isTempIdInCache = (id: string): boolean => {
    return TempIdGenerator.getInstance().isInCache(id);
};

// ✅ FIX 17: Testing utilities (development only)

/**
 * Enable performance tracking for debugging
 * Should only be used in development
 */
export const enableTempIdPerformanceTracking = (): void => {
    if (process.env.NODE_ENV === 'development') {
        TempIdGenerator.getInstance().enablePerformanceTracking();
    }
};

/**
 * Disable performance tracking
 */
export const disableTempIdPerformanceTracking = (): void => {
    TempIdGenerator.getInstance().disablePerformanceTracking();
};

/**
 * Reset generation statistics
 * Useful for testing
 */
export const resetTempIdStats = (): void => {
    TempIdGenerator.getInstance().resetStats();
};

/**
 * Generate multiple temp IDs for testing
 *
 * @param count - Number of IDs to generate
 * @returns Array of temporary IDs
 */
export const generateMultipleTempIds = (count: number): TempId[] => {
    const generator = TempIdGenerator.getInstance();
    return Array.from({ length: count }, () => generator.generate());
};

// ✅ FIX 18: Type guards and validation utilities

/**
 * Type guard to check if value is a valid ID
 *
 * @param value - Value to check
 * @returns True if value is a valid ID type
 */
export const isValidId = (value: unknown): value is AnyId => {
    return (
        typeof value === 'string' ||
        typeof value === 'number'
    );
};

/**
 * Type guard for permanent IDs
 *
 * @param id - ID to check
 * @returns True if ID is permanent (not temporary)
 */
export const isPermanentId = (id: AnyId): id is PermanentId => {
    return !isTempId(id);
};

/**
 * Ensure an ID is a permanent ID, throw error if temporary
 *
 * @param id - ID to validate
 * @returns The permanent ID
 * @throws Error if ID is temporary
 */
export const ensurePermanentId = (id: AnyId): PermanentId => {
    if (isTempId(id)) {
        throw new Error(`Expected permanent ID, got temporary ID: ${id}`);
    }
    return id;
};

/**
 * Convert unknown value to valid ID with validation
 *
 * @param value - Value to convert
 * @returns Valid ID
 * @throws Error if value cannot be converted to valid ID
 */
export const toValidId = (value: unknown): AnyId => {
    if (typeof value === 'string' || typeof value === 'number') {
        return value;
    }

    if (value === null || value === undefined) {
        throw new Error('ID cannot be null or undefined');
    }

    throw new Error(`Invalid ID type: ${typeof value}`);
};

// Export types for external use
export type {
    AnyId,
    CryptoSupport,
    IdGenerationStats, PermanentId, TempId, TempIdConfig
};
