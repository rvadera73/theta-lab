"""
MCP Server for Unified Master Reports
Exposes report generation as tools accessible to Claude and options-trader skill
"""

import asyncio
import json
from mcp.server import Server, Notification
from mcp.server.stdio import stdio_server
from mcp.server.models import Tool, TextContent, Image, ResourceTemplate
from mcp.types import (
    Resource,
    TextResourceContents,
    ToolCall,
    ToolResult,
    ToolUse,
)
import sys
from pathlib import Path
from datetime import date
from typing import Any

# Add paths
sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/scripts')
sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/mcp/reports')
sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/mcp/analysis')
sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/mcp')

from mcp_unified_reports import (
    generate_daily_report_tool,
    generate_weekly_report_tool,
    generate_biweekly_report_tool,
    generate_monthly_report_tool,
    generate_all_reports_tool
)


class UnifiedReportsServer:
    """MCP Server for unified master reports"""

    def __init__(self):
        self.server = Server("unified-reports")
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup MCP event handlers"""

        @self.server.list_tools()
        async def list_tools():
            """List all available report generation tools"""
            return [
                Tool(
                    name="generate_daily_report",
                    description="Generate comprehensive DAILY report with conviction analysis, market regime, and position heat distribution",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "report_date": {
                                "type": "string",
                                "description": "ISO date string (YYYY-MM-DD). Defaults to today. E.g., '2026-05-11'"
                            }
                        }
                    }
                ),
                Tool(
                    name="generate_weekly_report",
                    description="Generate comprehensive WEEKLY report with 10 sections: market regime forecast, action priorities, IV rank gates, Greeks, decision tree, framework status",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "report_date": {
                                "type": "string",
                                "description": "ISO date string (YYYY-MM-DD). Defaults to today."
                            }
                        }
                    }
                ),
                Tool(
                    name="generate_biweekly_report",
                    description="Generate BI-WEEKLY trend analysis report with 3-month rolling conviction trends, tier evolution, win rates, Greeks drift, sector rotation",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "report_date": {
                                "type": "string",
                                "description": "ISO date string (YYYY-MM-DD). Defaults to today."
                            }
                        }
                    }
                ),
                Tool(
                    name="generate_monthly_report",
                    description="Generate MONTHLY strategic review with variance analysis, account performance, moat recalibration, Citadel comparison with delta calculation",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "report_date": {
                                "type": "string",
                                "description": "ISO date string (YYYY-MM-DD). Defaults to today."
                            }
                        }
                    }
                ),
                Tool(
                    name="generate_all_reports",
                    description="Generate ALL 4 reports at once: DAILY, WEEKLY, BIWEEKLY, MONTHLY. Comprehensive analysis of portfolio across all timeframes.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "report_date": {
                                "type": "string",
                                "description": "ISO date string (YYYY-MM-DD). Defaults to today."
                            }
                        }
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            """Execute report generation tool"""
            report_date = arguments.get('report_date')

            if name == "generate_daily_report":
                result = await generate_daily_report_tool(report_date)
            elif name == "generate_weekly_report":
                result = await generate_weekly_report_tool(report_date)
            elif name == "generate_biweekly_report":
                result = await generate_biweekly_report_tool(report_date)
            elif name == "generate_monthly_report":
                result = await generate_monthly_report_tool(report_date)
            elif name == "generate_all_reports":
                result = await generate_all_reports_tool(report_date)
            else:
                result = {
                    "success": False,
                    "error": f"Unknown tool: {name}"
                }

            return [
                ToolResult(
                    type="text",
                    text=json.dumps(result, indent=2)
                )
            ]

    async def run(self):
        """Run the MCP server"""
        async with stdio_server(self.server):
            await self.server.wait_for_shutdown()


async def main():
    """Main entry point"""
    server = UnifiedReportsServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
