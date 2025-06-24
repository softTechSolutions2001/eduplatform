// frontend/src/courseBuilder/utils/virtualization.ts
import { RefObject, useCallback, useEffect, useState } from 'react';

interface VirtualizationOptions {
    itemHeight: number;
    overscan?: number;
    container: RefObject<HTMLElement>;
}

export const useVirtualization = <T>(
    items: T[],
    options: VirtualizationOptions
) => {
    const { itemHeight, overscan = 3, container } = options;
    const [visibleRange, setVisibleRange] = useState({ start: 0, end: 10 });

    const updateVisibleItems = useCallback(() => {
        if (!container.current) return;

        const { scrollTop, clientHeight } = container.current;
        const start = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
        const visibleCount = Math.ceil(clientHeight / itemHeight) + 2 * overscan;
        const end = Math.min(items.length, start + visibleCount);

        setVisibleRange({ start, end });
    }, [container, items.length, itemHeight, overscan]);

    useEffect(() => {
        const element = container.current;
        if (!element) return;

        updateVisibleItems();

        const handleScroll = () => {
            window.requestAnimationFrame(updateVisibleItems);
        };

        element.addEventListener('scroll', handleScroll);
        window.addEventListener('resize', updateVisibleItems);

        return () => {
            element.removeEventListener('scroll', handleScroll);
            window.removeEventListener('resize', updateVisibleItems);
        };
    }, [container, updateVisibleItems]);

    const visibleItems = items.slice(visibleRange.start, visibleRange.end);
    const containerHeight = items.length * itemHeight;
    const offsetY = visibleRange.start * itemHeight;

    return {
        visibleItems,
        containerHeight,
        offsetY,
    };
};
