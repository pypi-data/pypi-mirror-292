import os
import fnmatch
from typing import List, Optional
import logging

def get_directory_info(
    dir_path: str,
    include_project_structure: bool = True,
    include_file_contents: bool = True,
    exclude_patterns: Optional[List[str]] = None,
    log_path: Optional[str] = None
) -> str:
    """
    Retrieves information from a local directory.

    Args:
        dir_path (str): Path to the local directory.
        include_project_structure (bool): Include project structure.
        include_file_contents (bool): Include file contents.
        exclude_patterns (List[str], optional): Additional patterns to exclude.
        log_path (str, optional): Path to save the log.

    Returns:
        str: Formatted directory information.
    """
    logger = logging.getLogger(__name__)
    
    try:
        dir_name = os.path.basename(dir_path)
        output = [f"Directory Name: {dir_name}"]

        if include_project_structure:
            project_structure = _get_project_structure(dir_path, exclude_patterns)
            output.append("\nProject Structure:")
            output.append(project_structure)

        if include_file_contents:
            file_contents = _get_file_contents(dir_path, exclude_patterns)
            output.append("\nFile Contents:")
            output.append(file_contents)

        result = "\n".join(output)
        
        if log_path:
            with open(log_path, 'w', encoding='utf-8') as file:
                file.write(result)

        return result

    except Exception as e:
        logger.error(f"Error retrieving directory information: {str(e)}")
        raise

def _get_project_structure(dir_path: str, exclude_patterns: Optional[List[str]] = None) -> str:
    """
    Retrieves the project structure, excluding specified patterns for both files and directories.
    """
    exclude_patterns = exclude_patterns or []
    structure = []

    for root, dirs, files in os.walk(dir_path, topdown=True):
        rel_path = os.path.relpath(root, dir_path)
        level = rel_path.count(os.sep)
        indent = ' ' * 4 * level
        subindent = ' ' * 4 * (level + 1)

        if any(fnmatch.fnmatch(os.path.basename(root), pattern) for pattern in exclude_patterns):
            dirs[:] = []
            continue

        if rel_path != '.':
            structure.append(f"{indent}{os.path.basename(root)}/")

        files = sorted([f for f in files if not any(fnmatch.fnmatch(f, pattern) for pattern in exclude_patterns)])
        structure.extend(f"{subindent}{f}" for f in files)

        dirs[:] = sorted([d for d in dirs if not any(fnmatch.fnmatch(d, pattern) for pattern in exclude_patterns)])

    return '\n'.join(structure)

def _get_file_contents(dir_path: str, exclude_patterns: Optional[List[str]] = None) -> str:
    """
    Retrieves the contents of files, excluding patterns.
    """
    logger = logging.getLogger(__name__)
    exclude_patterns = exclude_patterns or []
    contents = []
    for root, dirs, files in os.walk(dir_path):
        dirs[:] = [d for d in dirs if not any(fnmatch.fnmatch(d, pattern) for pattern in exclude_patterns)]
        
        for file in files:
            if not any(fnmatch.fnmatch(file, pattern) for pattern in exclude_patterns):
                relative_path = os.path.relpath(os.path.join(root, file), dir_path)
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    contents.append(f"\nFile: {relative_path}\n{file_content}")
                except Exception as e:
                    logger.warning(f"Could not read file {relative_path}: {str(e)}")
    return "\n".join(contents)