"""
LEXICON MCP Integration Layer
Connects MCP servers to LEXICON agents for enhanced capabilities
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging
from datetime import datetime
import subprocess

# MCP Client imports (hypothetical - adjust based on actual MCP SDK)
# from mcp import MCPClient, MCPServer

logger = logging.getLogger(__name__)

class LEXICONMCPIntegration:
    """
    MCP Integration for LEXICON Pipeline
    Provides filesystem access, persistent context, and enhanced web scraping
    """
    
    def __init__(self):
        self.mcp_config_path = Path("mcp-config.json")
        self.mcp_servers = {}
        self.load_mcp_config()
        
    def load_mcp_config(self):
        """Load MCP server configurations"""
        try:
            with open(self.mcp_config_path, 'r') as f:
                config = json.load(f)
                self.mcp_config = config.get("mcpServers", {})
                logger.info(f"Loaded {len(self.mcp_config)} MCP server configurations")
        except Exception as e:
            logger.error(f"Failed to load MCP config: {e}")
            self.mcp_config = {}
    
    async def initialize_mcp_servers(self):
        """Start all configured MCP servers"""
        for server_name, config in self.mcp_config.items():
            try:
                # Start MCP server process
                env = os.environ.copy()
                env.update(config.get("env", {}))
                
                process = await asyncio.create_subprocess_exec(
                    config["command"],
                    *config["args"],
                    env=env,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                self.mcp_servers[server_name] = {
                    "process": process,
                    "config": config,
                    "status": "running"
                }
                
                logger.info(f"Started MCP server: {server_name}")
                
            except Exception as e:
                logger.error(f"Failed to start MCP server {server_name}: {e}")
    
    async def use_filesystem_mcp(self, operation: str, path: str, content: Optional[str] = None) -> Dict[str, Any]:
        """
        Use Filesystem MCP for corpus access
        
        Operations:
        - read: Read legal documents
        - write: Save generated briefs
        - search: Find relevant files
        - list: List available documents
        """
        # In production, this would communicate with the MCP server
        # For now, we'll simulate the functionality
        
        corpus_base = Path("C:\\Users\\jdall\\lexicon-mvp-alpha\\tbi-corpus")
        target_path = corpus_base / path
        
        try:
            if operation == "read":
                if target_path.exists():
                    with open(target_path, 'r', encoding='utf-8') as f:
                        return {
                            "status": "success",
                            "content": f.read(),
                            "metadata": {
                                "size": target_path.stat().st_size,
                                "modified": datetime.fromtimestamp(target_path.stat().st_mtime).isoformat()
                            }
                        }
                else:
                    return {"status": "error", "message": "File not found"}
                    
            elif operation == "write":
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return {"status": "success", "message": f"Wrote to {path}"}
                
            elif operation == "search":
                # Search for files matching pattern
                results = []
                pattern = path  # path acts as search pattern
                for file_path in corpus_base.rglob(f"*{pattern}*"):
                    if file_path.is_file():
                        results.append({
                            "path": str(file_path.relative_to(corpus_base)),
                            "size": file_path.stat().st_size,
                            "type": file_path.suffix
                        })
                return {"status": "success", "results": results[:20]}  # Limit to 20 results
                
            elif operation == "list":
                target_dir = corpus_base / path if path else corpus_base
                if target_dir.is_dir():
                    items = []
                    for item in target_dir.iterdir():
                        items.append({
                            "name": item.name,
                            "type": "directory" if item.is_dir() else "file",
                            "size": item.stat().st_size if item.is_file() else None
                        })
                    return {"status": "success", "items": items}
                else:
                    return {"status": "error", "message": "Directory not found"}
                    
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def use_context_mcp(self, operation: str, key: str, value: Optional[Any] = None) -> Dict[str, Any]:
        """
        Use Context MCP for persistent memory
        
        Operations:
        - store: Save case strategy, research findings, brief outcomes
        - retrieve: Get historical context
        - search: Find related past cases
        - analyze: Get insights from past briefs
        """
        context_store = Path("C:\\Users\\jdall\\lexicon-mvp-alpha\\context-store")
        context_store.mkdir(exist_ok=True)
        
        try:
            if operation == "store":
                # Store context with timestamp
                context_file = context_store / f"{key}.json"
                data = {
                    "key": key,
                    "value": value,
                    "timestamp": datetime.now().isoformat(),
                    "version": 1
                }
                
                # If file exists, increment version
                if context_file.exists():
                    with open(context_file, 'r') as f:
                        existing = json.load(f)
                        data["version"] = existing.get("version", 0) + 1
                        data["previous_versions"] = existing.get("previous_versions", [])
                        data["previous_versions"].append({
                            "value": existing["value"],
                            "timestamp": existing["timestamp"]
                        })
                
                with open(context_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                return {"status": "success", "version": data["version"]}
                
            elif operation == "retrieve":
                context_file = context_store / f"{key}.json"
                if context_file.exists():
                    with open(context_file, 'r') as f:
                        data = json.load(f)
                    return {"status": "success", "data": data}
                else:
                    return {"status": "not_found", "message": f"No context for key: {key}"}
                    
            elif operation == "search":
                # Search through all context files
                results = []
                search_term = key.lower()
                
                for context_file in context_store.glob("*.json"):
                    try:
                        with open(context_file, 'r') as f:
                            data = json.load(f)
                            
                        # Search in key and value
                        if (search_term in data.get("key", "").lower() or 
                            search_term in json.dumps(data.get("value", "")).lower()):
                            results.append({
                                "key": data["key"],
                                "timestamp": data["timestamp"],
                                "preview": str(data.get("value", ""))[:200]
                            })
                            
                    except Exception:
                        continue
                
                return {"status": "success", "results": results}
                
            elif operation == "analyze":
                # Analyze patterns across stored contexts
                all_contexts = []
                for context_file in context_store.glob("*.json"):
                    try:
                        with open(context_file, 'r') as f:
                            all_contexts.append(json.load(f))
                    except Exception:
                        continue
                
                # Simple analysis - count brief types, outcomes, etc.
                analysis = {
                    "total_cases": len(all_contexts),
                    "brief_types": {},
                    "outcomes": {},
                    "recent_strategies": []
                }
                
                for ctx in all_contexts:
                    value = ctx.get("value", {})
                    if isinstance(value, dict):
                        brief_type = value.get("brief_type")
                        if brief_type:
                            analysis["brief_types"][brief_type] = analysis["brief_types"].get(brief_type, 0) + 1
                        
                        outcome = value.get("outcome")
                        if outcome:
                            analysis["outcomes"][outcome] = analysis["outcomes"].get(outcome, 0) + 1
                
                # Get 5 most recent strategies
                sorted_contexts = sorted(all_contexts, key=lambda x: x.get("timestamp", ""), reverse=True)
                for ctx in sorted_contexts[:5]:
                    value = ctx.get("value", {})
                    if isinstance(value, dict) and "strategy" in value:
                        analysis["recent_strategies"].append({
                            "case": ctx["key"],
                            "strategy": value["strategy"][:200] + "...",
                            "date": ctx["timestamp"]
                        })
                
                return {"status": "success", "analysis": analysis}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def use_github_mcp(self, operation: str, repo: str, path: Optional[str] = None, content: Optional[str] = None) -> Dict[str, Any]:
        """
        Use GitHub MCP for version control and collaboration
        
        Operations:
        - create_repo: Initialize new repo for case
        - commit_brief: Save brief versions
        - get_template: Retrieve brief templates
        - track_changes: Get revision history
        - collaborate: Manage team edits
        """
        # This would normally use the GitHub MCP server
        # Simulating functionality for now
        
        github_base = Path("C:\\Users\\jdall\\lexicon-mvp-alpha\\.github-repos")
        github_base.mkdir(exist_ok=True)
        
        try:
            if operation == "create_repo":
                # Create a new repository for a case
                repo_path = github_base / repo
                repo_path.mkdir(exist_ok=True)
                
                # Initialize with README
                readme = repo_path / "README.md"
                readme.write_text(f"# {repo}\n\nLEXICON case repository\n\nCreated: {datetime.now().isoformat()}")
                
                # Create standard directories
                for dir_name in ["briefs", "research", "templates", "evidence"]:
                    (repo_path / dir_name).mkdir(exist_ok=True)
                
                return {
                    "status": "success",
                    "repo": repo,
                    "url": f"https://github.com/lexicon-firm/{repo}",
                    "structure": ["briefs/", "research/", "templates/", "evidence/"]
                }
                
            elif operation == "commit_brief":
                # Commit a brief version
                repo_path = github_base / repo
                if not repo_path.exists():
                    return {"status": "error", "message": "Repository not found"}
                
                brief_path = repo_path / "briefs" / path
                brief_path.parent.mkdir(exist_ok=True)
                
                # Save with version tracking
                version = 1
                version_file = brief_path.parent / ".versions.json"
                
                if version_file.exists():
                    with open(version_file, 'r') as f:
                        versions = json.load(f)
                    version = len(versions) + 1
                else:
                    versions = []
                
                # Save brief
                brief_path.write_text(content)
                
                # Update version history
                versions.append({
                    "version": version,
                    "file": path,
                    "timestamp": datetime.now().isoformat(),
                    "author": "LEXICON Agent",
                    "message": f"Auto-generated brief v{version}",
                    "hash": hash(content) % 1000000  # Simple hash for demo
                })
                
                with open(version_file, 'w') as f:
                    json.dump(versions, f, indent=2)
                
                return {
                    "status": "success",
                    "version": version,
                    "commit": f"v{version}-{versions[-1]['hash']}"
                }
                
            elif operation == "get_template":
                # Retrieve brief templates
                templates = {
                    "daubert_motion": """UNITED STATES DISTRICT COURT
[DISTRICT]

[CASE CAPTION]

MOTION TO EXCLUDE EXPERT TESTIMONY PURSUANT TO FED. R. EVID. 702 AND DAUBERT

[PARTY] respectfully moves this Court...""",
                    "frye_motion": """IN THE CIRCUIT COURT OF [COUNTY]
[STATE]

[CASE CAPTION]

MOTION TO EXCLUDE EXPERT TESTIMONY UNDER FRYE STANDARD

NOW COMES [PARTY], by and through undersigned counsel...""",
                    "response_to_daubert": """RESPONSE TO MOTION TO EXCLUDE EXPERT TESTIMONY

[PARTY] responds to [OPPOSING PARTY]'s Motion to Exclude..."""
                }
                
                template_name = path or "daubert_motion"
                return {
                    "status": "success",
                    "template": templates.get(template_name, templates["daubert_motion"]),
                    "available_templates": list(templates.keys())
                }
                
            elif operation == "track_changes":
                # Get revision history
                repo_path = github_base / repo / "briefs"
                version_file = repo_path / ".versions.json"
                
                if version_file.exists():
                    with open(version_file, 'r') as f:
                        versions = json.load(f)
                    
                    return {
                        "status": "success",
                        "history": versions,
                        "total_versions": len(versions),
                        "latest": versions[-1] if versions else None
                    }
                else:
                    return {"status": "success", "history": [], "total_versions": 0}
                    
            elif operation == "collaborate":
                # Manage collaborative editing
                collab_file = github_base / repo / ".collaborators.json"
                
                if collab_file.exists():
                    with open(collab_file, 'r') as f:
                        collaborators = json.load(f)
                else:
                    collaborators = {
                        "team": ["Lead Attorney (Claude Opus 4)", "Legal Analyst (O3 Pro)", 
                                "Scientific Expert (GPT-4.1)", "Writer (GPT-4.5)", 
                                "Editor (Gemini 2.5 Pro)"],
                        "permissions": {
                            "Lead Attorney (Claude Opus 4)": "admin",
                            "Legal Analyst (O3 Pro)": "write",
                            "Scientific Expert (GPT-4.1)": "write",
                            "Writer (GPT-4.5)": "write",
                            "Editor (Gemini 2.5 Pro)": "write"
                        },
                        "active_edits": []
                    }
                    
                    with open(collab_file, 'w') as f:
                        json.dump(collaborators, f, indent=2)
                
                return {
                    "status": "success",
                    "collaborators": collaborators,
                    "active_sessions": len(collaborators.get("active_edits", []))
                }
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def use_firecrawl_mcp(self, url: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Use Firecrawl MCP for enhanced web scraping
        
        Options:
        - extract_tables: Extract data tables from court opinions
        - follow_links: Crawl linked documents
        - pdf_support: Handle PDF court documents
        - clean_html: Remove navigation/ads
        """
        # This would normally communicate with the Firecrawl MCP server
        # For now, we'll enhance the existing Firecrawl integration
        
        default_options = {
            "onlyMainContent": True,
            "includeHtml": False,
            "extractTables": True,
            "followLinks": False,
            "waitForSelector": "body",
            "timeout": 30000
        }
        
        if options:
            default_options.update(options)
        
        try:
            # Simulate enhanced Firecrawl response
            if "courtlistener.com" in url:
                return {
                    "status": "success",
                    "content": "Enhanced court opinion content with tables extracted...",
                    "metadata": {
                        "title": "Case Title from CourtListener",
                        "date": "2024-01-15",
                        "court": "7th Circuit",
                        "tables": [
                            {"type": "precedents", "rows": 5},
                            {"type": "expert_qualifications", "rows": 3}
                        ]
                    }
                }
            elif "scholar.google.com" in url:
                return {
                    "status": "success",
                    "content": "Enhanced Google Scholar results with citation network...",
                    "metadata": {
                        "citations": 42,
                        "related_articles": 15,
                        "year": 2023
                    }
                }
            elif "pubmed.ncbi.nlm.nih.gov" in url:
                return {
                    "status": "success",
                    "content": "Medical research abstract and methodology details...",
                    "metadata": {
                        "pmid": "12345678",
                        "journal": "Journal of Neurotrauma",
                        "impact_factor": 4.2
                    }
                }
            else:
                return {
                    "status": "success",
                    "content": f"Scraped content from {url}",
                    "metadata": {"source": url}
                }
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def integrate_with_agents(self, agent_type: str, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Integrate MCP data with LEXICON agents
        
        Agent types:
        - orchestrator: Claude Opus 4
        - legal_research: O3 Pro Deep Research  
        - scientific_research: GPT-4.1
        - writer: GPT-4.5
        - editor: Gemini 2.5 Pro
        """
        integration_results = {
            "agent": agent_type,
            "mcp_sources": [],
            "enhanced_context": {}
        }
        
        # Add MCP-enhanced context based on agent needs
        if agent_type == "orchestrator":
            # Orchestrator gets full context from all MCP sources
            context_data = await self.use_context_mcp("retrieve", "recent_strategies")
            if context_data["status"] == "success":
                integration_results["enhanced_context"]["historical_strategies"] = context_data["data"]
            
            # Get corpus overview
            corpus_list = await self.use_filesystem_mcp("list", "processed/Client firm case law precedent")
            if corpus_list["status"] == "success":
                integration_results["enhanced_context"]["available_precedents"] = corpus_list["items"]
                
        elif agent_type == "legal_research":
            # Legal research agent gets precedent files and web scraping
            search_results = await self.use_filesystem_mcp("search", "Daubert")
            if search_results["status"] == "success":
                integration_results["enhanced_context"]["daubert_cases"] = search_results["results"]
            
            # Scrape recent court opinions
            court_url = "https://www.courtlistener.com/opinion/recent/?q=expert+testimony+TBI"
            scraped = await self.use_firecrawl_mcp(court_url, {"extractTables": True})
            if scraped["status"] == "success":
                integration_results["enhanced_context"]["recent_opinions"] = scraped
                
        elif agent_type == "scientific_research":
            # Scientific agent gets medical literature
            pubmed_url = "https://pubmed.ncbi.nlm.nih.gov/?term=traumatic+brain+injury+diagnosis"
            scraped = await self.use_firecrawl_mcp(pubmed_url, {"followLinks": True})
            if scraped["status"] == "success":
                integration_results["enhanced_context"]["medical_research"] = scraped
                
        return integration_results
    
    async def cleanup(self):
        """Shutdown MCP servers gracefully"""
        for server_name, server_info in self.mcp_servers.items():
            try:
                process = server_info["process"]
                process.terminate()
                await process.wait()
                logger.info(f"Stopped MCP server: {server_name}")
            except Exception as e:
                logger.error(f"Error stopping MCP server {server_name}: {e}")


# Example usage in LEXICON pipeline
async def enhanced_lexicon_pipeline_with_mcp():
    """
    Example of how to integrate MCP into existing LEXICON pipeline
    """
    mcp = LEXICONMCPIntegration()
    
    # Initialize MCP servers
    await mcp.initialize_mcp_servers()
    
    try:
        # Store case strategy in persistent context
        strategy = {
            "brief_type": "Daubert Motion",
            "approach": "Challenge opposing expert methodology",
            "key_arguments": ["Lack of peer review", "Unreliable testing methods"]
        }
        await mcp.use_context_mcp("store", "case_12345_strategy", strategy)
        
        # Use filesystem MCP to access specific precedents
        precedent = await mcp.use_filesystem_mcp(
            "read", 
            "processed/Client firm case law precedent/Illinois/Illinois Doctor Testify to Probability.pdf"
        )
        
        # Use Firecrawl for fresh case law
        recent_cases = await mcp.use_firecrawl_mcp(
            "https://www.courtlistener.com/api/rest/v3/search/?q=Daubert+neuropsychological",
            {"extractTables": True, "followLinks": True}
        )
        
        # Integrate with agents
        orchestrator_context = await mcp.integrate_with_agents("orchestrator", {
            "precedent": precedent,
            "recent_cases": recent_cases
        })
        
        return {
            "mcp_enhanced": True,
            "sources_accessed": ["filesystem", "context", "firecrawl"],
            "orchestrator_context": orchestrator_context
        }
        
    finally:
        await mcp.cleanup()


if __name__ == "__main__":
    # Test MCP integration
    asyncio.run(enhanced_lexicon_pipeline_with_mcp())