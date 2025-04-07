import argparse
import asyncio
import sys
import psutil
from rich.console import Console
from rich.table import Table
from core.crawler import AdvancedCrawler
from core.scanner import DirectoryScanner
from core.utils import save_results, clean_cache

console = Console()

def show_banner():
    # استخدام raw string لتجنب تحذير أحرف الهروب
    banner = r"""
    [bold cyan]
     _   _ _   _ _  __  __           _     
    | | | | | | | |/ / | \ \    /\  / \    
    | | | | |_| | ' / |  \ \  /  \/   \   
    | |_| |  _  | . \ |   \ \/ /\ \ /\ /   
     \___/|_| |_|_|\_\|    \__/  \_\_/ \_  
    [/]
    [bold magenta]HyperScan v2.0[/]
    [bold yellow]Advanced Web Scanner | Termux Edition[/]
    """
    console.print(banner)

async def main():
    show_banner()
    parser = argparse.ArgumentParser(description="HyperScan v2.0 - Advanced Web Scanner")
    parser.add_argument("-u", "--url", help="Target URL (e.g., http://example.com)", required=True)
    parser.add_argument("-w", "--wordlist", help="Path to wordlist (for scanning mode)")
    parser.add_argument("-t", "--threads", type=int, default=30, help="Max concurrent tasks")
    parser.add_argument("-o", "--output", default="results", help="Output directory")
    parser.add_argument("-p", "--proxies", help="Path to proxy file (single proxy: http://proxy:port)")
    parser.add_argument("-f", "--format", choices=["txt", "json"], default="txt", help="Output format")

    args = parser.parse_args()

    # التحقق من المدخلات
    if not args.url.startswith(("http://", "https://")):
        console.print("[bold red]Error:[/] URL must start with http:// or https://")
        sys.exit(1)

    # إعداد الوكيل (سلسلة نصية واحدة)
    proxy = None
    if args.proxies and os.path.isfile(args.proxies):
        with open(args.proxies, 'r') as f:
            proxy = f.readline().strip()  # قراءة أول سطر كوكيل واحد

    # تحديد عدد المهام بناءً على الموارد
    cpu_count = psutil.cpu_count()
    mem = psutil.virtual_memory().available / (1024 * 1024)  # MB
    max_concurrent = min(args.threads, cpu_count * 2 if mem > 512 else cpu_count)

    if args.wordlist:
        # وضع فحص الدلائل
        scanner = DirectoryScanner(args.url, args.wordlist, proxy=proxy)
        results = await scanner.run(max_concurrent)
        
        # عرض النتائج
        table = Table(title="Directory Scan Results", show_lines=True)
        table.add_column("URL", style="cyan")
        table.add_column("Status", style="bold green")
        table.add_column("Size (bytes)", style="yellow")
        table.add_column("Notes", style="magenta")
        
        for item in results:
            table.add_row(item['url'], str(item['status']), str(item['size']), item['extra'])
        
        console.print(table)
        filename = save_results(results, args.output, args.format)
        console.print(f"[green]Saved to {filename}[/]")
    else:
        # وضع الزحف
        crawler = AdvancedCrawler(args.url, proxy=proxy)
        results = await crawler.start()
        
        # عرض النتائج
        console.print(f"\n[bold]Discovered URLs:[/] {len(results['urls'])}")
        console.print(f"[bold]Emails Found:[/] {len(results['emails'])}")
        console.print(f"[bold]JS Files:[/] {len(results['js_files'])}")
        console.print(f"[bold]API Endpoints:[/] {len(results['api_endpoints'])}\n")
        
        filename = save_results(results, args.output, args.format)
        console.print(f"[green]Saved to {filename}[/]")

    clean_cache()

if __name__ == "__main__":
    asyncio.run(main())
