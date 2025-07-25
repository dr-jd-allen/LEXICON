"""
Agent 1: Claude Opus 4 Orchestrator/Lead Attorney
Coordinates all agents and provides strategic guidance
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from flask import Flask, request, jsonify
import anthropic
import redis
import chromadb
from chromadb.config import Settings
import logging
import aiohttp
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class OrchestrationService:
    """
    Claude Opus 4 - Lead Attorney/Orchestrator
    Strategic analysis and agent coordination
    """
    
    def __init__(self):
        # Initialize Claude client
        self.claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Redis for caching and inter-agent communication
        self.redis_client = redis.Redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379"),
            decode_responses=True
        )
        
        # ChromaDB for vector search
        self.chroma_client = chromadb.HttpClient(
            host=os.getenv("CHROMA_HOST", "chromadb"),
            port=int(os.getenv("CHROMA_PORT", "8000"))
        )
        
        # Agent endpoints
        self.agent_endpoints = {
            "legal_research": "http://legal-research:8002",
            "scientific_research": "http://scientific-research:8003",
            "writer": "http://writer:8004",
            "editor": "http://editor:8005"
        }
        
        # Thread pool for parallel execution
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def orchestrate_brief_generation(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main orchestration logic using Claude Opus 4
        """
        brief_type = request_data.get("brief_type")
        case_files = request_data.get("case_files", [])
        jurisdiction = request_data.get("jurisdiction", "Federal")
        
        # Step 1: Strategic Analysis with Claude Opus 4
        strategy_prompt = f"""
        As Lead Attorney using Claude Opus 4, analyze this case for a {brief_type} brief:
        
        Jurisdiction: {jurisdiction}
        Case Files: {len(case_files)} documents uploaded
        
        Provide strategic guidance for:
        1. Key legal arguments to develop
        2. Precedents to research (for Agents 2 & 3)
        3. Scientific/medical evidence needed
        4. Potential weaknesses to address
        5. Overall strategy (support vs challenge expert)
        
        Your analysis will guide all other agents.
        """
        
        try:
            strategy_response = self.claude.messages.create(
                model="claude-opus-4-20250514",  # Latest Opus 4 model
                max_tokens=2000,
                messages=[{"role": "user", "content": strategy_prompt}],
                temperature=0.3
            )
            
            strategy = strategy_response.content[0].text
            logger.info("Claude Opus 4 strategic analysis complete")
            
            # Cache strategy for other agents
            self.redis_client.setex(
                f"strategy:{request_data.get('request_id')}",
                3600,
                json.dumps({
                    "strategy": strategy,
                    "timestamp": datetime.now().isoformat()
                })
            )
            
        except Exception as e:
            logger.error(f"Strategic analysis error: {str(e)}")
            strategy = "Default strategy: comprehensive research needed"
        
        # Step 2: Vector search for relevant precedents
        vector_results = await self.search_vector_database(case_files, brief_type)
        
        # Step 3: Coordinate parallel research (Agents 2 & 3)
        research_tasks = await self.coordinate_parallel_research(
            strategy, vector_results, request_data
        )
        
        # Step 4: Send to writer (Agent 4)
        draft_brief = await self.send_to_writer(
            strategy, research_tasks, request_data
        )
        
        # Step 5: Final editing (Agent 5)
        final_brief = await self.send_to_editor(draft_brief)
        
        return {
            "status": "success",
            "brief": final_brief,
            "strategy": strategy,
            "research_summary": research_tasks,
            "orchestrator": "Claude Opus 4",
            "timestamp": datetime.now().isoformat()
        }
    
    async def coordinate_parallel_research(
        self, strategy: str, vector_results: List[Dict], 
        request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Coordinate Agents 2 & 3 to work concurrently
        Enable real-time communication via Redis pub/sub
        """
        # Create research channels in Redis
        legal_channel = f"legal_research:{request_data.get('request_id')}"
        scientific_channel = f"scientific_research:{request_data.get('request_id')}"
        
        # Publish strategy to both channels
        self.redis_client.publish(legal_channel, json.dumps({
            "strategy": strategy,
            "vector_results": vector_results[:10]  # Top 10 relevant docs
        }))
        
        self.redis_client.publish(scientific_channel, json.dumps({
            "strategy": strategy,
            "focus_areas": self._extract_scientific_focus(strategy)
        }))
        
        # Launch parallel research
        async with aiohttp.ClientSession() as session:
            legal_task = self._call_legal_research(session, request_data, strategy)
            scientific_task = self._call_scientific_research(session, request_data, strategy)
            
            # Execute concurrently
            legal_results, scientific_results = await asyncio.gather(
                legal_task, scientific_task
            )
            
        return {
            "legal_research": legal_results,
            "scientific_research": scientific_results,
            "communication_enabled": True
        }
    
    async def _call_legal_research(
        self, session: aiohttp.ClientSession, 
        request_data: Dict, strategy: str
    ) -> Dict:
        """Call Agent 2: O3 Pro Deep Research"""
        try:
            async with session.post(
                f"{self.agent_endpoints['legal_research']}/api/v1/research",
                json={
                    "request_id": request_data.get("request_id"),
                    "strategy": strategy,
                    "brief_type": request_data.get("brief_type"),
                    "jurisdiction": request_data.get("jurisdiction")
                },
                timeout=aiohttp.ClientTimeout(total=300)
            ) as response:
                return await response.json()
        except Exception as e:
            logger.error(f"Legal research error: {str(e)}")
            return {"error": str(e)}
    
    async def _call_scientific_research(
        self, session: aiohttp.ClientSession,
        request_data: Dict, strategy: str
    ) -> Dict:
        """Call Agent 3: GPT-4.1 Scientific Research"""
        try:
            async with session.post(
                f"{self.agent_endpoints['scientific_research']}/api/v1/research",
                json={
                    "request_id": request_data.get("request_id"),
                    "strategy": strategy,
                    "focus_areas": self._extract_scientific_focus(strategy)
                },
                timeout=aiohttp.ClientTimeout(total=300)
            ) as response:
                return await response.json()
        except Exception as e:
            logger.error(f"Scientific research error: {str(e)}")
            return {"error": str(e)}
    
    def _extract_scientific_focus(self, strategy: str) -> List[str]:
        """Extract scientific/medical focus areas from strategy"""
        # Simple extraction - could be enhanced with NLP
        focus_keywords = [
            "neuropsychological", "DTI", "imaging", "cognitive",
            "TBI", "brain injury", "medical evidence", "diagnostic"
        ]
        
        found_areas = []
        strategy_lower = strategy.lower()
        
        for keyword in focus_keywords:
            if keyword in strategy_lower:
                found_areas.append(keyword)
        
        return found_areas or ["traumatic brain injury", "neuropsychological testing"]
    
    async def search_vector_database(
        self, case_files: List[Dict], brief_type: str
    ) -> List[Dict]:
        """Search ChromaDB for relevant precedents"""
        try:
            collection = self.chroma_client.get_collection("lexicon_tbi_corpus")
            
            # Build query based on brief type
            query_text = f"{brief_type} expert testimony precedent cases"
            
            results = collection.query(
                query_texts=[query_text],
                n_results=20,
                include=["metadatas", "documents", "distances"]
            )
            
            return [
                {
                    "document": doc,
                    "metadata": meta,
                    "relevance_score": 1 - dist  # Convert distance to similarity
                }
                for doc, meta, dist in zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                )
            ]
            
        except Exception as e:
            logger.error(f"Vector search error: {str(e)}")
            return []
    
    async def send_to_writer(
        self, strategy: str, research: Dict, request_data: Dict
    ) -> str:
        """Send to Agent 4 for initial draft"""
        # Implementation would call writer service
        return "Draft brief content..."
    
    async def send_to_editor(self, draft: str) -> str:
        """Send to Agent 5 for final editing"""
        # Implementation would call editor service
        return "Final edited brief..."

# Flask routes
orchestrator = OrchestrationService()

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "service": "orchestrator", "model": "claude-opus-4"})

@app.route("/api/v1/orchestrate", methods=["POST"])
async def orchestrate():
    """Main orchestration endpoint"""
    try:
        request_data = request.get_json()
        request_data["request_id"] = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        result = await orchestrator.orchestrate_brief_generation(request_data)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Orchestration error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=False)