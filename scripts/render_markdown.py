#!/usr/bin/env python3
"""
Markdown to Image Renderer
Renders Markdown files to images using Playwright with GitHub styling
"""

import asyncio
import argparse
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright


async def render_markdown_to_image(
    markdown_file: str,
    output_dir: str = "images/rendered",
    theme: str = "dark",
    width: int = 1200,
    scale: float = 2.0
):
    """
    Render a markdown file to an image
    
    Args:
        markdown_file: Path to the markdown file
        output_dir: Directory to save the rendered image
        theme: GitHub theme (dark/light)
        width: Viewport width for rendering
        scale: Scale factor for high DPI rendering
    """
    md_path = Path(markdown_file)
    if not md_path.exists():
        print(f"❌ Markdown file not found: {markdown_file}")
        return
    
    # Read markdown content
    content = md_path.read_text(encoding='utf-8')
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_path / f"{md_path.stem}_{timestamp}.png"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': width, 'height': 1080},
            device_scale_factor=scale
        )
        
        page = await context.new_page()
        
        try:
            print(f"📄 Rendering {markdown_file} with {theme} theme...")
            
            # Create HTML with GitHub markdown styling
            html_content = f"""
            <!DOCTYPE html>
            <html data-color-mode="{theme}" data-dark-theme="dark" data-light-theme="light">
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>Markdown Render</title>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown-{theme}.min.css">
                <style>
                    body {{
                        box-sizing: border-box;
                        min-width: 200px;
                        max-width: {width}px;
                        margin: 0 auto;
                        padding: 45px;
                        background: {('#0d1117' if theme == 'dark' else '#ffffff')};
                    }}
                    .markdown-body {{
                        font-family: -apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,Arial,sans-serif;
                    }}
                    
                    /* Custom styling for better rendering */
                    .markdown-body img {{
                        max-width: 100%;
                        height: auto;
                    }}
                    
                    .markdown-body table {{
                        width: 100%;
                        border-collapse: collapse;
                    }}
                    
                    /* Handle SVG icons gracefully */
                    .markdown-body img[src$=".svg"] {{
                        background: transparent;
                    }}
                </style>
            </head>
            <body>
                <article class="markdown-body" id="content">
                    {content}
                </article>
                
                <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
                <script>
                    document.getElementById('content').innerHTML = marked.parse(document.getElementById('content').textContent);
                </script>
            </body>
            </html>
            """
            
            # Set content and wait for rendering
            await page.set_content(html_content)
            await page.wait_for_load_state('networkidle')
            
            # Wait a bit more for any dynamic content
            await page.wait_for_timeout(2000)
            
            # Get the actual content height for optimal screenshot
            content_height = await page.evaluate('''
                () => {
                    const body = document.body;
                    const html = document.documentElement;
                    return Math.max(
                        body.scrollHeight, body.offsetHeight,
                        html.clientHeight, html.scrollHeight, html.offsetHeight
                    );
                }
            ''')
            
            # Take screenshot with full content height
            await page.set_viewport_size({'width': width, 'height': min(content_height + 100, 32767)})
            await page.screenshot(
                path=output_file,
                full_page=True,
                type='png'
            )
            
            print(f"✅ Rendered to: {output_file}")
            print(f"📏 Dimensions: {width}x{content_height + 100}px")
            
        except Exception as e:
            print(f"❌ Error rendering markdown: {e}")
            
        finally:
            await browser.close()


async def render_all_readmes(theme: str = "dark"):
    """Render all README files in the current directory"""
    readme_files = list(Path('.').glob('README*.md'))
    
    if not readme_files:
        print("📄 No README files found")
        return
    
    print(f"🔍 Found {len(readme_files)} README files")
    
    for readme in readme_files:
        await render_markdown_to_image(str(readme), theme=theme)


async def main():
    """Main function with CLI argument parsing"""
    parser = argparse.ArgumentParser(description="Render Markdown files to images")
    parser.add_argument("file", nargs="?", help="Markdown file to render (optional)")
    parser.add_argument("--theme", choices=["dark", "light"], default="dark", help="GitHub theme")
    parser.add_argument("--width", type=int, default=1200, help="Viewport width")
    parser.add_argument("--scale", type=float, default=2.0, help="Scale factor for high DPI")
    parser.add_argument("--output", "-o", default="images/rendered", help="Output directory")
    parser.add_argument("--all-readmes", action="store_true", help="Render all README files")
    
    args = parser.parse_args()
    
    if args.all_readmes:
        await render_all_readmes(theme=args.theme)
    elif args.file:
        await render_markdown_to_image(
            markdown_file=args.file,
            output_dir=args.output,
            theme=args.theme,
            width=args.width,
            scale=args.scale
        )
    else:
        print("🤔 Please specify a file or use --all-readmes")
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())