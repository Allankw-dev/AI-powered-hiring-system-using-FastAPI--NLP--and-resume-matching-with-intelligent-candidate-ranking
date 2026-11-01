"""Look for committed secrets.

    python -m scripts.scan_secrets              # scan the files git tracks (used by CI)
    python -m scripts.scan_secrets --history    # also scan every past commit (slow, report only)

Matches are always printed REDACTED. Exit code 1 if the current files contain a secret.
"""
import re
import subprocess  # nosec B404
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

PATTERNS = {
    "database URL with password": re.compile(r"postgres(?:ql)?(?:\+\w+)?://[^:/\s'\"]+:[^@\s'\"<>{}$]{4,}@[\w.-]+"),
    "Anthropic API key": re.compile(r"sk-ant-[A-Za-z0-9_-]{16,}"),
    "Google API key": re.compile(r"AIza[0-9A-Za-z_-]{30,}"),
    "Resend API key": re.compile(r"\bre_[A-Za-z0-9]{20,}"),
    "private key block": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "hard-coded secret assignment": re.compile(
        r"""(?ix)\b(?:SECRET_KEY|API_KEY|[A-Z_]*PASSWORD|[A-Z_]*TOKEN)\b\s*[=:]\s*['"][A-Za-z0-9/_+=!@#$%^&*.-]{16,}['"]"""
    ),
}
# Test fixtures and docs legitimately contain fake credentials.
GENERIC_SKIP = ("tests/", ".env.example", "SECURITY_AUDIT.md", "UPGRADE_NOTES.md", "scripts/scan_secrets.py")
BINARY_SUFFIXES = {".png", ".jpg", ".jpeg", ".pdf", ".db", ".sqlite3", ".zip", ".woff", ".woff2", ".ico"}


def _redact(match: str) -> str:
    return match[:10] + "…<redacted>"


def tracked_files() -> list[Path]:
    out = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True, text=True, check=False).stdout  # nosec B603 B607
    return [REPO / line for line in out.splitlines() if line]


def scan_text(text: str, name: str) -> list[str]:
    skip_generic = any(s in name for s in GENERIC_SKIP)
    findings = []
    for label, pattern in PATTERNS.items():
        if skip_generic and label in {"hard-coded secret assignment", "database URL with password"}:
            continue
        for m in pattern.finditer(text):
            findings.append(f"{name}: {label}: {_redact(m.group(0))}")
    return findings


def scan_tree() -> list[str]:
    findings = []
    for path in tracked_files():
        if path.suffix.lower() in BINARY_SUFFIXES or not path.is_file():
            continue
        try:
            findings += scan_text(path.read_text(encoding="utf-8", errors="ignore"), str(path.relative_to(REPO)))
        except OSError:
            continue
    return findings


def scan_history() -> dict[str, int]:
    log = subprocess.run(  # nosec B603 B607
        ["git", "log", "--all", "-p", "--no-color"], cwd=REPO, capture_output=True, text=True, errors="ignore", check=False
    ).stdout
    counts: dict[str, int] = {}
    for line in log.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            for label, pattern in PATTERNS.items():
                if pattern.search(line):
                    counts[label] = counts.get(label, 0) + 1
    return counts


def main() -> int:
    findings = scan_tree()
    if findings:
        print("Secrets found in tracked files:")
        print("\n".join("  " + f for f in findings))
    else:
        print("OK: no secrets found in tracked files.")
    if "--history" in sys.argv:
        hist = scan_history()
        print("\nGit history (rotate anything listed here, deleting the file is not enough):")
        print("\n".join(f"  {label}: {n} line(s)" for label, n in hist.items()) or "  clean")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
