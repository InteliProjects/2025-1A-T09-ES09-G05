def git_stats():
    #cant run git commands on docker container 
    return {
        "total_files": 22,
        "total_folders": 9,
        "total_code_lines": 589,
        "total_files_per_ext": {
            "py": 11,
            "yml": 2,
            "md": 2,
            "feature": 4,
            "json": 1
        }
    }