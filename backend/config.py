VALID_EXTENSIONS = [
    # Programming languages
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rb", ".rs", ".cpp", ".c", ".cs", ".kt", ".swift", ".php",

    # Web frontend
    ".html", ".htm", ".css", ".scss", ".sass", ".vue", ".astro",

    # Config/infra
    ".json", ".yaml", ".yml", ".toml", ".ini", ".env",

    # Markdown/docs
    ".md", ".mdx", ".txt",

    # Notebooks
    ".ipynb",
]

EXCLUDE_DIRS = {
    # Common system and metadata
    ".git", ".github", ".vscode", ".idea", ".DS_Store", "__pycache__",

    # JS/Node ecosystem
    "node_modules", "dist", "build", ".next", ".turbo", "out", "coverage",

    # Python
    ".mypy_cache", ".pytest_cache", "venv", "env", "site-packages",

    # Java/Gradle
    "target", ".gradle", ".idea", ".settings",

    # Rust
    "target",

    # Go
    "bin", "pkg",

    # Misc
    ".cache", "logs", "snapshots", "checkpoints",
}

CHUNK_LINES = 30

CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
