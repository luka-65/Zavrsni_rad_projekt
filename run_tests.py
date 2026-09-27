import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
REPORT = ROOT / "test-results.txt"

BACKEND_GROUPS = {
    "test_strategies": "Strategije (MA, RSI, Bollinger)",
    "test_backtester": "Backtester (izvršenje i metrike)",
    "test_api": "API i validacija",
    "test_market_data": "Tržišni podaci (Binance, granice, cache)",
    "test_persistence": "Persistencija (SQLite i povijest)",
}

ANSI = re.compile(r"\x1b\[[0-9;]*m")


def backend_python():
    venv = BACKEND / "venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    return str(venv) if venv.exists() else sys.executable


def run(command, cwd):
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "FORCE_COLOR": "0", "NO_COLOR": "1"}
    completed = subprocess.run(command, cwd=cwd, env=env, capture_output=True,
                               text=True, encoding="utf-8", errors="replace")
    return completed.returncode, ANSI.sub("", completed.stdout + completed.stderr)


def backend_tests():
    code, output = run([backend_python(), "-X", "utf8", "-m", "unittest", "discover", "-s", "tests", "-v"], BACKEND)
    results = re.findall(r"^test_\w+ \((test_\w+)\.\w+\)\n.*? \.\.\. (ok|FAIL|ERROR)", output, re.MULTILINE)
    groups = Counter(module for module, _ in results)
    failed = Counter(module for module, status in results if status != "ok")
    rows = [(BACKEND_GROUPS.get(module, module), groups[module], failed[module]) for module in BACKEND_GROUPS]
    total = re.search(r"^Ran (\d+) tests?", output, re.MULTILINE)
    return {
        "name": "Backend (Python unittest)",
        "passed": code == 0,
        "count": f"{total.group(1) if total else '?'} testova",
        "groups": rows,
        "output": output,
    }


def frontend_command(*arguments):
    npx = shutil.which("npx") or "npx"
    return [npx, *arguments]


def frontend_tests():
    code, output = run(frontend_command("ng", "test", "--watch=false", "--reporters=verbose"), FRONTEND)
    total = re.search(r"Tests\s+(?:(\d+) failed \| )?(\d+) passed \((\d+)\)", output)
    count = f"{total.group(3)} testova" if total else "?"
    lines = [line.strip() for line in output.splitlines()]
    tests = [line.replace("|frontend| ", "") for line in lines if line.startswith(("✓", "×"))]
    summary = [line for line in lines if line.startswith(("Test Files", "Tests ", "Errors", "Duration"))]
    return {
        "name": "Frontend (Angular + Vitest)",
        "passed": code == 0,
        "count": count,
        "groups": [],
        "output": "\n".join(tests + [""] + summary) if tests else output,
    }


def e2e_tests():
    npm = shutil.which("npm") or "npm"
    script = "test:e2e:prikaz" if "--prikazi" in sys.argv else "test:e2e"
    code, output = run([npm, "run", script], FRONTEND)
    return {
        "name": "E2E graf (Playwright + Edge)",
        "passed": code == 0 and "PROLAZ" in output,
        "count": "1 scenarij",
        "groups": [],
        "output": output,
    }


def write_report(suites):
    lines = [
        "IZVJEŠTAJ AUTOMATSKIH TESTOVA — Simulator trgovanja kriptovalutama",
        f"Datum izvođenja: {datetime.now().strftime('%d. %m. %Y. %H:%M')}",
        "",
        "SAŽETAK",
        f"{'Skupina':45} {'Opseg':>14}   Rezultat",
    ]
    for suite in suites:
        lines.append(f"{suite['name']:45} {suite['count']:>14}   {'PROLAZ' if suite['passed'] else 'PAD'}")
        for group, count, failed in suite["groups"]:
            status = "PROLAZ" if not failed else f"PAD ({failed})"
            lines.append(f"  - {group:41} {count:>11} t.   {status}")
    for suite in suites:
        lines += ["", "=" * 100, suite["name"].upper(), "=" * 100, suite["output"].rstrip()]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    suites = []
    steps = [("Backend testovi", backend_tests), ("Frontend testovi", frontend_tests)]
    if "--bez-e2e" not in sys.argv:
        steps.append(("E2E test grafa (pokreće razvojni poslužitelj, traje oko minutu)", e2e_tests))

    for title, step in steps:
        print(f"{title}...", flush=True)
        suite = step()
        print(f"  {suite['count']}: {'PROLAZ' if suite['passed'] else 'PAD'}", flush=True)
        suites.append(suite)

    write_report(suites)
    print(f"\nIzvještaj je spremljen u {REPORT}")
    sys.exit(0 if all(suite["passed"] for suite in suites) else 1)


if __name__ == "__main__":
    main()
