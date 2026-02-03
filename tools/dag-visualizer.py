#!/usr/bin/env python3
"""
vBRIEF DAG Visualizer

Generates Mermaid diagram from vBRIEF Plan edges and items.
Useful for visualizing workflow dependencies and execution order.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set


class DAGVisualizer:
    """Generates Mermaid diagrams from vBRIEF Plans."""
    
    # Status to color mapping
    STATUS_COLORS = {
        "draft": "#f0f0f0",
        "proposed": "#e1e8f5",
        "approved": "#d0e8ff",
        "pending": "#e0e0e0",
        "running": "#ffeb99",
        "completed": "#90ee90",
        "blocked": "#ffcccc",
        "cancelled": "#d0d0d0"
    }
    
    # Status to symbol mapping
    STATUS_SYMBOLS = {
        "draft": "◇",
        "proposed": "◈",
        "approved": "◆",
        "pending": "○",
        "running": "⟳",
        "completed": "✓",
        "blocked": "✖",
        "cancelled": "−"
    }
    
    def __init__(self, plan: Dict):
        self.plan = plan
        self.items = plan.get("items", [])
        self.edges = plan.get("edges", [])
        self.item_map = self._build_item_map(self.items)
    
    def _build_item_map(self, items: List[Dict], prefix: str = "") -> Dict[str, Dict]:
        """Build map of item ID to item for lookup."""
        item_map = {}
        for item in items:
            item_id = item.get("id")
            if item_id:
                full_id = f"{prefix}.{item_id}" if prefix else item_id
                item_map[full_id] = item
                
                # Recursively process subItems
                sub_items = item.get("subItems", [])
                if sub_items:
                    item_map.update(self._build_item_map(sub_items, full_id))
        
        return item_map
    
    def _sanitize_id(self, item_id: str) -> str:
        """Sanitize ID for use in Mermaid."""
        return item_id.replace(".", "_").replace("-", "_")
    
    def _get_node_label(self, item_id: str) -> str:
        """Generate node label with title and status."""
        item = self.item_map.get(item_id, {})
        title = item.get("title", item_id)
        status = item.get("status", "unknown")
        symbol = self.STATUS_SYMBOLS.get(status, "?")
        
        return f"{title}<br/>{symbol} {status}"
    
    def _get_node_style(self, item_id: str) -> str:
        """Generate style for node based on status."""
        item = self.item_map.get(item_id, {})
        status = item.get("status", "pending")
        color = self.STATUS_COLORS.get(status, "#e0e0e0")
        
        return f"fill:{color}"
    
    def generate_mermaid(self, format: str = "TB") -> str:
        """
        Generate Mermaid diagram.
        
        Args:
            format: Graph direction (TB, LR, RL, BT)
            
        Returns:
            Mermaid diagram as string
        """
        lines = [f"graph {format}"]
        
        # Generate nodes
        node_ids = set()
        for item_id in self.item_map.keys():
            safe_id = self._sanitize_id(item_id)
            label = self._get_node_label(item_id)
            lines.append(f"    {safe_id}[\"{label}\"]")
            node_ids.add(item_id)
        
        # Generate edges
        for edge in self.edges:
            from_id = edge.get("from")
            to_id = edge.get("to")
            edge_type = edge.get("type", "blocks")
            
            if from_id and to_id:
                safe_from = self._sanitize_id(from_id)
                safe_to = self._sanitize_id(to_id)
                
                # Choose arrow style based on edge type
                if edge_type == "blocks":
                    arrow = "-->|blocks|"
                elif edge_type == "informs":
                    arrow = "-.->|informs|"
                elif edge_type == "invalidates":
                    arrow = "==>|invalidates|"
                elif edge_type == "suggests":
                    arrow = "-.->|suggests|"
                else:
                    arrow = f"-->|{edge_type}|"
                
                lines.append(f"    {safe_from} {arrow} {safe_to}")
        
        # Add styles
        lines.append("")
        for item_id in node_ids:
            safe_id = self._sanitize_id(item_id)
            style = self._get_node_style(item_id)
            lines.append(f"    style {safe_id} {style}")
        
        return "\n".join(lines)
    
    def generate_legend(self) -> str:
        """Generate legend for status symbols."""
        lines = ["## Status Legend", ""]
        for status, symbol in self.STATUS_SYMBOLS.items():
            color = self.STATUS_COLORS[status]
            lines.append(f"- {symbol} `{status}` (color: {color})")
        
        return "\n".join(lines)


def visualize_plan(file_path: str, output_format: str = "markdown", direction: str = "TB"):
    """
    Visualize a vBRIEF Plan as a DAG.
    
    Args:
        file_path: Path to vBRIEF JSON file
        output_format: Output format (markdown, mermaid, html)
        direction: Graph direction (TB, LR, RL, BT)
    """
    # Load document
    try:
        with open(file_path, 'r') as f:
            doc = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    plan = doc.get("plan", {})
    edges = plan.get("edges", [])
    
    if not edges:
        print("No edges found in Plan. Nothing to visualize.", file=sys.stderr)
        print("\nPlan items:", file=sys.stderr)
        for item in plan.get("items", []):
            print(f"  - {item.get('title', '(no title)')}", file=sys.stderr)
        sys.exit(1)
    
    visualizer = DAGVisualizer(plan)
    
    if output_format == "mermaid":
        # Output raw Mermaid
        print(visualizer.generate_mermaid(direction))
    
    elif output_format == "markdown":
        # Output Markdown with embedded Mermaid
        plan_title = plan.get("title", "Plan Visualization")
        print(f"# {plan_title}\n")
        print("```mermaid")
        print(visualizer.generate_mermaid(direction))
        print("```\n")
        print(visualizer.generate_legend())
    
    elif output_format == "html":
        # Output HTML with Mermaid.js
        plan_title = plan.get("title", "Plan Visualization")
        mermaid_code = visualizer.generate_mermaid(direction)
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{plan_title}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({{ startOnLoad: true }});
    </script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            color: #333;
        }}
        .legend {{
            margin-top: 30px;
            padding: 15px;
            background: #f5f5f5;
            border-radius: 5px;
        }}
        .legend h2 {{
            margin-top: 0;
        }}
        .legend ul {{
            list-style: none;
            padding: 0;
        }}
        .legend li {{
            margin: 5px 0;
        }}
    </style>
</head>
<body>
    <h1>{plan_title}</h1>
    <div class="mermaid">
{mermaid_code}
    </div>
    <div class="legend">
        <h2>Status Legend</h2>
        <ul>
"""
        for status, symbol in visualizer.STATUS_SYMBOLS.items():
            html += f"            <li>{symbol} <code>{status}</code></li>\n"
        
        html += """        </ul>
    </div>
</body>
</html>"""
        print(html)
    
    else:
        print(f"Unknown output format: {output_format}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Visualize vBRIEF Plan DAG as Mermaid diagram",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate Markdown with embedded Mermaid
  %(prog)s plan.vbrief.json > diagram.md
  
  # Generate HTML with interactive diagram
  %(prog)s plan.vbrief.json --format html > diagram.html
  
  # Generate raw Mermaid for embedding
  %(prog)s plan.vbrief.json --format mermaid
  
  # Change graph direction to left-right
  %(prog)s plan.vbrief.json --direction LR
"""
    )
    
    parser.add_argument("file", help="vBRIEF JSON file to visualize")
    parser.add_argument(
        "-f", "--format",
        choices=["markdown", "mermaid", "html"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    parser.add_argument(
        "-d", "--direction",
        choices=["TB", "LR", "RL", "BT"],
        default="TB",
        help="Graph direction: TB=top-bottom, LR=left-right, RL=right-left, BT=bottom-top (default: TB)"
    )
    
    args = parser.parse_args()
    
    visualize_plan(args.file, args.format, args.direction)
