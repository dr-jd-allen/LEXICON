"""Cloud Workflows orchestrator for LEXICON legal AI workflow"""

import os
import json
from typing import Dict, Any, List
from google.cloud import workflows_v1
from google.cloud import workflows_executions_v1
from google.cloud import tasks_v2
from google.cloud import pubsub_v1
import asyncio

class LEXICONWorkflowOrchestrator:
    """Orchestrates the LEXICON legal AI workflow using GCP services"""
    
    def __init__(self):
        self.project_id = os.environ.get('GCP_PROJECT_ID', 'spinwheel-464709')
        self.location = os.environ.get('GCP_REGION', 'us-central1')
        self.workflow_name = 'lexicon-legal-workflow'
        
        # Initialize clients
        self.workflows_client = workflows_v1.WorkflowsClient()
        self.executions_client = workflows_executions_v1.ExecutionsClient()
        self.tasks_client = tasks_v2.CloudTasksClient()
        self.publisher = pubsub_v1.PublisherClient()
        
        # Queue names
        self.research_queue = f"projects/{self.project_id}/locations/{self.location}/queues/research-tasks"
        self.contradiction_queue = f"projects/{self.project_id}/locations/{self.location}/queues/contradiction-tasks"
        self.precedent_queue = f"projects/{self.project_id}/locations/{self.location}/queues/precedent-tasks"
        self.draft_queue = f"projects/{self.project_id}/locations/{self.location}/queues/draft-tasks"
    
    def create_workflow_definition(self) -> str:
        """Create Cloud Workflows definition in YAML"""
        workflow_yaml = """
main:
  params: [args]
  steps:
    - init:
        assign:
          - project_id: ${args.project_id}
          - motion_type: ${args.motion_type}
          - jurisdiction: ${args.jurisdiction}
          - documents: ${args.documents}
          - workflow_id: ${sys.get_env("GOOGLE_CLOUD_WORKFLOW_EXECUTION_ID")}
    
    - research_agent:
        call: http.post
        args:
          url: https://lexicon-${project_id}.cloudfunctions.net/research-agent
          auth:
            type: OIDC
          body:
            motion_type: ${motion_type}
            jurisdiction: ${jurisdiction}
            documents: ${documents}
            task: "analyze_expert_testimony"
        result: research_result
    
    - find_contradictions:
        call: http.post
        args:
          url: https://lexicon-${project_id}.cloudfunctions.net/contradiction-finder
          auth:
            type: OIDC
          body:
            research_output: ${research_result.body}
            motion_type: ${motion_type}
        result: contradictions_result
    
    - find_precedents:
        parallel:
          branches:
            - client_precedents:
                call: http.post
                args:
                  url: https://lexicon-${project_id}.cloudfunctions.net/precedent-finder
                  auth:
                    type: OIDC
                  body:
                    research_output: ${research_result.body}
                    contradictions: ${contradictions_result.body}
                    source: "client_firm"
                result: client_precedents_result
            
            - lexis_precedents:
                call: http.post
                args:
                  url: https://lexicon-${project_id}.cloudfunctions.net/lexis-nexis-search
                  auth:
                    type: OIDC
                  body:
                    research_output: ${research_result.body}
                    jurisdiction: ${jurisdiction}
                result: lexis_precedents_result
    
    - draft_argument:
        call: http.post
        args:
          url: https://lexicon-${project_id}.cloudfunctions.net/argument-drafter
          auth:
            type: OIDC
          body:
            research: ${research_result.body}
            contradictions: ${contradictions_result.body}
            client_precedents: ${client_precedents_result.body}
            lexis_precedents: ${lexis_precedents_result.body}
            motion_type: ${motion_type}
            jurisdiction: ${jurisdiction}
        result: draft_result
    
    - save_results:
        call: http.post
        args:
          url: https://lexicon-${project_id}.cloudfunctions.net/save-results
          auth:
            type: OIDC
          body:
            workflow_id: ${workflow_id}
            draft: ${draft_result.body}
            metadata:
              motion_type: ${motion_type}
              jurisdiction: ${jurisdiction}
              timestamp: ${sys.now()}
        result: save_result
    
    - return_result:
        return: 
          success: true
          workflow_id: ${workflow_id}
          document_url: ${save_result.body.document_url}
          summary: ${draft_result.body.summary}
"""
        return workflow_yaml
    
    def deploy_workflow(self):
        """Deploy the workflow to Cloud Workflows"""
        parent = f"projects/{self.project_id}/locations/{self.location}"
        
        workflow = {
            "name": f"{parent}/workflows/{self.workflow_name}",
            "source_contents": self.create_workflow_definition(),
            "description": "LEXICON Legal AI Workflow for Daubert/Frye motions"
        }
        
        try:
            # Create or update workflow
            operation = self.workflows_client.create_workflow(
                parent=parent,
                workflow=workflow,
                workflow_id=self.workflow_name
            )
            
            print(f"Workflow deployment initiated: {operation.name}")
            return operation
        except Exception as e:
            if "already exists" in str(e):
                # Update existing workflow
                operation = self.workflows_client.update_workflow(
                    workflow=workflow
                )
                print(f"Workflow update initiated: {operation.name}")
                return operation
            else:
                raise
    
    def execute_workflow(self, motion_type: str, jurisdiction: str, documents: List[str]) -> str:
        """Execute the workflow with given parameters"""
        parent = f"projects/{self.project_id}/locations/{self.location}/workflows/{self.workflow_name}"
        
        execution = {
            "argument": json.dumps({
                "project_id": self.project_id,
                "motion_type": motion_type,
                "jurisdiction": jurisdiction,
                "documents": documents
            })
        }
        
        response = self.executions_client.create_execution(
            parent=parent,
            execution=execution
        )
        
        print(f"Workflow execution started: {response.name}")
        return response.name
    
    def get_execution_status(self, execution_name: str) -> Dict[str, Any]:
        """Get the status of a workflow execution"""
        execution = self.executions_client.get_execution(name=execution_name)
        
        return {
            "name": execution.name,
            "state": execution.state.name,
            "result": execution.result if execution.result else None,
            "error": execution.error if execution.error else None,
            "start_time": execution.start_time,
            "end_time": execution.end_time
        }
    
    async def create_task(self, queue_name: str, payload: Dict[str, Any], task_name: str = None):
        """Create a Cloud Task for async processing"""
        parent = queue_name
        
        task = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": f"https://lexicon-{self.project_id}.cloudfunctions.net/{task_name}",
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(payload).encode(),
                "oidc_token": {
                    "service_account_email": f"lexicon-sa@{self.project_id}.iam.gserviceaccount.com"
                }
            }
        }
        
        if task_name:
            task["name"] = f"{parent}/tasks/{task_name}-{os.urandom(8).hex()}"
        
        response = self.tasks_client.create_task(parent=parent, task=task)
        print(f"Created task: {response.name}")
        return response