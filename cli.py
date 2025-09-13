#!/usr/bin/env python3
import os
import sys
import argparse
import re
import datetime
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from dotenv import load_dotenv

from .modes import MODES
from .backend import SGPTBackend

console = Console()

def load_env():
    # Load .env from current directory or user's home config
    home_env = Path.home() / ".config" / "sgpt-terminal" / ".env"
    local_env = Path(".env")
    if home_env.exists():
        load_dotenv(home_env)
    if local_env.exists():
        load_dotenv(local_env, override=True)

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="sgpt",
        description="SGPT: your terminal copilot (OpenAI or Ollama backend)."
    )
    p.add_argument("prompt", nargs="*", help="Your question or request.")
    p.add_argument("-m", "--mode", choices=sorted(MODES.keys()), default="default",
                   help="Answer style / domain specialization.")
    p.add_argument("-b", "--backend", choices=["openai", "ollama"], default="openai",
                   help="Choose cloud (openai) or local (ollama) backend.")
    p.add_argument("--model", default=None, help="Model name (e.g., gpt-4o-mini or llama3).")
    p.add_argument("-f", "--file", default=None, help="Optional file to include as context (text only).")
    p.add_argument("--dry-run", action="store_true", help="Print settings and exit.")
    p.add_argument("-q", "--quiet", action="store_true", help="Print only the raw answer (no panels).")
    p.add_argument("--exec", dest="exec_mode", action="store_true", help="Execute generated command with confirmation.")
    return p

def read_context_file(path: str) -> str:
    fp = Path(path)
    if not fp.exists():
        raise FileNotFoundError(f"Context file not found: {path}")
    if fp.stat().st_size > 512 * 1024:
        raise ValueError("Context file too large (>512KB). Provide a smaller file.")
    return fp.read_text(errors="ignore")

def main(argv=None) -> int:
    load_env()
    parser = build_parser()
    args = parser.parse_args(argv)

    user_prompt = " ".join(args.prompt).strip()
    if not user_prompt:
        console.print("[red]No prompt given. Try: sgpt -m bash 'list open TCP ports with nmap'[/red]")
        return 1

    system_prompt = MODES[args.mode]["system"]
    if args.file:
        try:
            file_text = read_context_file(args.file)
            user_prompt += f"\n\n[CONTEXT FROM FILE {args.file}]\n{file_text}\n[/CONTEXT]"
        except Exception as e:
            console.print(f"[yellow]Warning: Could not read context file: {e}[/yellow]")

    backend = args.backend
    model = args.model or ("gpt-4o-mini" if backend == "openai" else "llama3")  # sensible defaults

    if args.dry_run:
        console.print(Panel.fit(
            f"Backend: {backend}\nModel: {model}\nMode: {args.mode}\nPrompt: {user_prompt[:300]}...",
            title="sgpt dry-run"
        ))
        return 0

    try:
        engine = SGPTBackend(backend=backend, model=model)
        answer = engine.chat(system_prompt, user_prompt)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return 2


    # Optional execution mode with confirmation
    if args.exec_mode:
        def extract_command(text: str) -> str:
            # Prefer first fenced code block
            m = re.search(r"```(?:bash|sh|zsh|shell)?\s*([\s\S]*?)```", text, re.IGNORECASE)
            cmd = ""
            if m:
                cmd = m.group(1).strip()
            else:
                # Fallback: first non-empty line
                for line in text.splitlines():
                    s = line.strip()
                    if not s:
                        continue
                    # strip typical prompt chars
                    s = re.sub(r'^\$\s*', '', s)
                    cmd = s
                    break
            # If multiple lines, ask to confirm entire block
            return cmd

        import subprocess, re, time
        cmd_to_run = extract_command(answer)
        if not cmd_to_run:
            console.print("[red]No runnable command found in the response.[/red]")
            return 3

        console.print(
    Panel.fit(
        Markdown(f"**About to execute:**\n\n```bash\n{cmd_to_run}\n```"),
        title="confirm"
	    )
	)

        try:
            confirm = input("Run this command? [y/N]: ").strip().lower()
        except EOFError:
            confirm = "n"
        if confirm != "y":
            console.print("[yellow]Aborted by user.[/yellow]")
            return 0

        # Run command
        try:
            result = subprocess.run(cmd_to_run, shell=True, capture_output=True, text=True)
            stdout, stderr = result.stdout, result.stderr
            rc = result.returncode

            # Log execution
            log_dir = Path.home() / ".local" / "share" / "sgpt-terminal"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "run.log"
            ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(log_file, "a") as lf:
                lf.write(f"[{ts}] rc={rc} mode={args.mode} backend={backend}:{model}\nCMD:\n{cmd_to_run}\n--- stdout ---\n{stdout}\n--- stderr ---\n{stderr}\n====\n")

            console.print("[green]--- Command Output ---[/green]")
            if stdout.strip():
                console.print(stdout)
            if stderr.strip():
                console.print("[red]--- Errors ---[/red]")
                console.print(stderr)
            console.print(f"[cyan]Exit code: {rc}[/cyan]")
        except Exception as e:
            console.print(f"[red]Execution failed: {e}[/red]")
            return 4

    return 0


if __name__ == "__main__":
    sys.exit(main())
