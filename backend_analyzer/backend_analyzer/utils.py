"""
Utilities for the Django Backend Analyzer.

This module contains utility functions and classes for logging,
progress tracking, and other common operations.
"""

import os
import sys
import logging
import time
from typing import Dict, List, Optional, Any, Callable, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps

# Set up the logger
logger = logging.getLogger('backend_analyzer')


class ColoredFormatter(logging.Formatter):
    """Custom formatter for colored console output."""
    
    COLORS = {
        'DEBUG': '\033[94m',     # Blue
        'INFO': '\033[92m',      # Green
        'SUCCESS': '\033[92m',   # Green
        'WARNING': '\033[93m',   # Yellow
        'ERROR': '\033[91m',     # Red
        'CRITICAL': '\033[91m',  # Red
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        # Add SUCCESS level
        if not hasattr(logging, 'SUCCESS'):
            logging.SUCCESS = 25  # Between INFO and WARNING
            logging.addLevelName(logging.SUCCESS, 'SUCCESS')
        
        # Clone the record to avoid modifying the original
        record_clone = logging.makeLogRecord(record.__dict__)
        
        # Get the log level name
        levelname = record_clone.levelname
        
        # Add color to the level name if output is to a terminal
        if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            color = self.COLORS.get(levelname, self.COLORS['RESET'])
            record_clone.levelname = f"{color}{levelname}{self.COLORS['RESET']}"
        
        return super().format(record_clone)


def setup_logging(verbose=False, log_file=None):
    """
    Set up logging configuration.
    
    Args:
        verbose: If True, set log level to DEBUG
        log_file: Optional path to a log file
    """
    # Set up root logger
    root_logger = logging.getLogger()
    
    if verbose:
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_format = '%(levelname)s - %(message)s'
    console_formatter = ColoredFormatter(console_format)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        file_formatter = logging.Formatter(file_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Add success method to logger
    def success(self, message, *args, **kwargs):
        if not hasattr(logging, 'SUCCESS'):
            logging.SUCCESS = 25  # Between INFO and WARNING
            logging.addLevelName(logging.SUCCESS, 'SUCCESS')
        self.log(logging.SUCCESS, message, *args, **kwargs)
    
    logging.Logger.success = success
    
    return root_logger


class ProgressTracker:
    """
    Track progress of operations and display status updates.
    
    This class helps visualize progress for long-running operations,
    showing completed steps, estimated time remaining, and more.
    """
    
    def __init__(self, total_steps: int, description: str = "Processing", update_interval: float = 0.1):
        self.total_steps = total_steps
        self.completed_steps = 0
        self.description = description
        self.update_interval = update_interval
        self.start_time = None
        self.last_update_time = None
        self.status_message = ""
        self.is_active = False
        
    def start(self):
        """Start the progress tracker."""
        self.completed_steps = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.is_active = True
        self._display_progress()
        
    def update(self, steps: int = 1, message: str = ""):
        """
        Update progress by a specified number of steps.
        
        Args:
            steps: Number of steps completed
            message: Optional status message to display
        """
        if not self.is_active:
            return
        
        self.completed_steps += steps
        if message:
            self.status_message = message
        
        # Only update display if enough time has passed since last update
        current_time = time.time()
        if current_time - self.last_update_time >= self.update_interval:
            self.last_update_time = current_time
            self._display_progress()
        
    def finish(self, message: str = "Completed"):
        """
        Mark the progress as completed.
        
        Args:
            message: Final message to display
        """
        if not self.is_active:
            return
        
        self.completed_steps = self.total_steps
        self.status_message = message
        self._display_progress()
        self.is_active = False
        
        # Add newline to ensure next output starts on fresh line
        if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            print()
    
    def _display_progress(self):
        """Display the current progress."""
        if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
            # Don't display progress bars in non-interactive environments
            return
        
        # Calculate progress percentage
        percentage = min(100.0, (self.completed_steps / self.total_steps) * 100)
        
        # Calculate elapsed time and ETA
        elapsed = time.time() - self.start_time
        if self.completed_steps > 0:
            rate = elapsed / self.completed_steps
            eta = rate * (self.total_steps - self.completed_steps)
            eta_str = f"ETA: {self._format_time(eta)}"
        else:
            eta_str = "ETA: ?"
        
        # Create progress bar
        bar_length = 30
        filled_length = int(bar_length * self.completed_steps / self.total_steps)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # Construct status line
        status = f"\r{self.description}: [{bar}] {percentage:.1f}% ({self.completed_steps}/{self.total_steps}) {eta_str}"
        
        if self.status_message:
            status += f" - {self.status_message}"
        
        # Write status to stdout and flush
        sys.stdout.write(status)
        sys.stdout.flush()
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds into a readable time string."""
        minutes, seconds = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"


def timed(logger_instance=None):
    """
    Decorator for timing function execution.
    
    Args:
        logger_instance: Logger to use for output. If None, uses the module logger.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            log = logger_instance or logger
            func_name = func.__name__
            
            log.debug(f"Starting {func_name}")
            start_time = time.time()
            
            result = func(*args, **kwargs)
            
            elapsed_time = time.time() - start_time
            log.debug(f"Completed {func_name} in {elapsed_time:.2f}s")
            
            return result
        return wrapper
    return decorator


class FileCacheManager:
    """
    Cache manager for file contents to avoid repeated disk reads.
    
    This improves performance when the same files need to be read multiple times.
    """
    
    def __init__(self, max_size: int = 100):
        """
        Initialize the cache manager.
        
        Args:
            max_size: Maximum number of files to keep in cache
        """
        self.cache = {}
        self.max_size = max_size
        self.access_count = {}
    
    def read_file(self, file_path: str, encoding: str = 'utf-8') -> str:
        """
        Read a file with caching.
        
        Args:
            file_path: Path to the file
            encoding: File encoding
            
        Returns:
            File contents as string
        """
        file_path = os.path.abspath(file_path)
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Update access count
        self.access_count[file_path] = self.access_count.get(file_path, 0) + 1
        
        # Return from cache if available
        if file_path in self.cache:
            return self.cache[file_path]
        
        # Read file and add to cache
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            # Manage cache size
            if len(self.cache) >= self.max_size:
                # Remove least accessed file
                least_accessed = min(self.access_count, key=self.access_count.get)
                del self.cache[least_accessed]
                del self.access_count[least_accessed]
            
            self.cache[file_path] = content
            return content
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            raise
    
    def invalidate(self, file_path: str = None):
        """
        Invalidate cache entries.
        
        Args:
            file_path: Specific file to invalidate, or None to invalidate all
        """
        if file_path:
            file_path = os.path.abspath(file_path)
            if file_path in self.cache:
                del self.cache[file_path]
                del self.access_count[file_path]
        else:
            self.cache.clear()
            self.access_count.clear()


def parallel_process(items: List[Any], process_func: Callable, max_workers: int = None, 
                     description: str = "Processing", show_progress: bool = True) -> List[Any]:
    """
    Process items in parallel using ThreadPoolExecutor.
    
    Args:
        items: List of items to process
        process_func: Function to apply to each item
        max_workers: Maximum number of worker threads
        description: Description for progress display
        show_progress: Whether to show progress
        
    Returns:
        List of results
    """
    results = []
    total_items = len(items)
    
    if total_items == 0:
        return results
    
    progress = None
    if show_progress:
        progress = ProgressTracker(total_items, description)
        progress.start()
    
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_item = {executor.submit(process_func, item): item for item in items}
            
            # Process results as they complete
            for future in as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    logger.error(f"Error processing {item}: {exc}")
                
                if progress:
                    progress.update(1)
    finally:
        if progress:
            progress.finish()
    
    return results


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length, adding suffix if truncated.
    
    Args:
        text: Text to truncate
        max_length: Maximum length of the output string
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix 