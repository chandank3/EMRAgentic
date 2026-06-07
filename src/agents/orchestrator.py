"""AutoGen agent orchestration for Healthcare Care Coordinator"""
from typing import Dict, List, Any, Optional
from src.config import get_settings
import json
import logging

# Try to import autogen, but make it optional
try:
    import autogen
    from autogen.agentchat.contrib.multimodal_conversable_agent import MultimodalConversableAgent
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False
    autogen = None
    MultimodalConversableAgent = None

logger = logging.getLogger(__name__)
settings = get_settings()


class StubAgent:
    """Stub agent for when AutoGen is not available"""
    def __init__(self, name: str):
        self.name = name
        self.system_message = f"Stub {name} agent - AutoGen not installed"
        self.llm_config = {}
    
    def initiate_chat(self, *args, **kwargs) -> Dict[str, Any]:
        """Stub chat method"""
        return {"status": "success", "message": f"Stub response from {self.name}"}


class HealthcareAgentTeam:
    """Multi-agent team orchestration for healthcare coordination"""

    def __init__(self):
        self.settings = settings
        self.llm_config = self._setup_llm_config()
        self.agents = {}
        self._initialize_agents()

    def _setup_llm_config(self) -> Dict[str, Any]:
        """Setup LLM configuration for local Ollama"""
        return {
            "config_list": [
                {
                    "model": settings.ollama_model,
                    "base_url": settings.ollama_base_url,
                    "api_type": "ollama",
                }
            ],
            "temperature": 0.3,
            "max_tokens": 2000,
            "timeout": 60,
        }

    def _initialize_stub_agents(self):
        """Initialize stub agents when AutoGen is not available"""
        stub_agents = [
            "coordinator", "clinical", "document", "policy", "escalation"
        ]
        for agent_name in stub_agents:
            self.agents[agent_name] = StubAgent(agent_name)

    def _initialize_agents(self):
        """Initialize the agent team"""
        if not AUTOGEN_AVAILABLE:
            logger.warning("AutoGen not available - initializing stub agents for API compatibility")
            self._initialize_stub_agents()
            return

        # Care Coordinator Agent - Main orchestrator
        self.agents["coordinator"] = autogen.ConversableAgent(
            name="CareCoordinator",
            system_message="""You are a Healthcare Care Coordinator AI Agent. Your responsibilities:
1. Schedule and manage patient appointments
2. Recommend personalized care plans based on patient history
3. Send medication reminders and track adherence
4. Retrieve and analyze patient documents
5. Generate visit summaries and escalate when needed
6. Ensure all actions comply with HIPAA and organizational policies
7. Request human approval for significant care plan changes

Always prioritize patient safety, data privacy, and clinical accuracy.""",
            llm_config=self.llm_config,
            human_input_mode="ALWAYS",  # Always ask for approval on critical actions
        )

        # Clinical Decision Support Agent
        self.agents["clinical"] = autogen.ConversableAgent(
            name="ClinicalDecisionSupport",
            system_message="""You are a Clinical Decision Support AI Agent. Your expertise:
1. Analyze patient clinical data and medical history
2. Recommend evidence-based care interventions
3. Flag potential drug interactions and allergies
4. Suggest appropriate follow-up care based on clinical guidelines
5. Highlight high-risk patients requiring escalation
6. Validate clinical protocols and best practices

Ensure all recommendations include clinical evidence and are compliant with medical regulations.""",
            llm_config=self.llm_config,
            human_input_mode="NEVER",  # CDS provides recommendations, doesn't make decisions
        )

        # Document Analysis Agent
        self.agents["document"] = autogen.ConversableAgent(
            name="DocumentAnalyzer",
            system_message="""You are a Medical Document Analysis AI Agent. Your responsibilities:
1. Extract key information from medical documents (labs, scans, notes)
2. Summarize document content for quick review
3. Identify abnormal findings that need attention
4. Index documents for efficient retrieval
5. Track document versions and maintain audit trail
6. Flag documents that may contain sensitive PII requiring masking

Always maintain document integrity and ensure proper PHI handling.""",
            llm_config=self.llm_config,
            human_input_mode="NEVER",
        )

        # Policy & Compliance Agent
        self.agents["policy"] = autogen.ConversableAgent(
            name="PolicyCompliance",
            system_message="""You are a Healthcare Policy & Compliance AI Agent. Your role:
1. Validate all actions against organizational policies
2. Ensure HIPAA and data privacy compliance
3. Check user permissions and RBAC rules
4. Monitor for suspicious activity patterns
5. Flag policy violations for audit
6. Ensure proper data access and retention policies
7. Validate PII masking strategies

Maintain strict compliance without compromising care delivery.""",
            llm_config=self.llm_config,
            human_input_mode="NEVER",
        )

        # Escalation & Approval Agent
        self.agents["escalation"] = autogen.ConversableAgent(
            name="EscalationManager",
            system_message="""You are an Escalation & Approval Management AI Agent. Your duties:
1. Identify situations requiring human review or approval
2. Route escalations to appropriate personnel
3. Manage approval workflows with timeouts
4. Document escalation reasons and decisions
5. Track approval status and follow-ups
6. Ensure urgent cases are handled with priority
7. Maintain escalation history and patterns

Always ensure critical decisions have proper human oversight.""",
            llm_config=self.llm_config,
            human_input_mode="ALWAYS",  # Manages human approvals
        )

    def coordinate_appointment_booking(self, patient_id: str, appointment_data: Dict) -> Dict:
        """Orchestrate appointment booking workflow"""
        logger.info(f"Starting appointment booking for patient {patient_id}")
        
        # Coordinator proposes appointment
        messages = [
            {
                "role": "user",
                "content": f"""Book an appointment with the following details:
Patient ID: {patient_id}
Appointment Data: {json.dumps(appointment_data, indent=2)}

Please:
1. Check patient availability and scheduling constraints
2. Verify provider availability
3. Check for policy violations
4. Request human approval"""
            }
        ]

        response = self._run_agent_chain(
            primary_agent=self.agents["coordinator"],
            supporting_agents=[self.agents["policy"], self.agents["escalation"]],
            messages=messages
        )
        
        return {"status": "success", "response": response}

    def recommend_care_plan(self, patient_id: str, context: Dict) -> Dict:
        """Orchestrate care plan recommendation workflow"""
        logger.info(f"Starting care plan recommendation for patient {patient_id}")
        
        messages = [
            {
                "role": "user",
                "content": f"""Generate a personalized care plan for patient {patient_id}.
Patient Context: {json.dumps(context, indent=2)}

Workflow:
1. Clinical Decision Support: Analyze patient data and recommend interventions
2. Care Coordinator: Compile comprehensive care plan
3. Policy Compliance: Validate against organizational standards
4. Escalation Manager: Route for human approval due to significance of care plan

Ensure all recommendations are evidence-based and patient-specific."""
            }
        ]

        response = self._run_agent_chain(
            primary_agent=self.agents["clinical"],
            supporting_agents=[
                self.agents["coordinator"],
                self.agents["policy"],
                self.agents["escalation"]
            ],
            messages=messages
        )
        
        return {"status": "success", "response": response}

    def generate_visit_summary(self, appointment_id: str, visit_notes: str) -> Dict:
        """Generate structured visit summary"""
        logger.info(f"Generating visit summary for appointment {appointment_id}")
        
        messages = [
            {
                "role": "user",
                "content": f"""Generate a comprehensive visit summary from the following notes:

Appointment ID: {appointment_id}
Visit Notes:
{visit_notes}

Please provide:
1. Patient vitals and measurements
2. Chief complaint and assessment
3. Interventions provided
4. Follow-up recommendations
5. Any alerts or escalations needed
6. Key points for care coordination"""
            }
        ]

        response = self._run_agent_chain(
            primary_agent=self.agents["document"],
            supporting_agents=[self.agents["clinical"], self.agents["coordinator"]],
            messages=messages
        )
        
        return {"status": "success", "response": response}

    def analyze_document(self, document_id: str, document_content: str, document_type: str) -> Dict:
        """Analyze medical document and extract insights"""
        logger.info(f"Analyzing document {document_id} of type {document_type}")
        
        messages = [
            {
                "role": "user",
                "content": f"""Analyze this {document_type} document:

Document ID: {document_id}
Content:
{document_content}

Please:
1. Extract key findings and values
2. Identify abnormal results that need attention
3. Summarize clinical significance
4. Recommend follow-up actions
5. Flag any PII that needs masking
6. Provide document indexing metadata"""
            }
        ]

        response = self._run_agent_chain(
            primary_agent=self.agents["document"],
            supporting_agents=[self.agents["clinical"], self.agents["policy"]],
            messages=messages
        )
        
        return {"status": "success", "response": response}

    def _run_agent_chain(
        self,
        primary_agent: Any,
        supporting_agents: List[Any],
        messages: List[Dict]
    ) -> str:
        """Execute agent chain with specified workflow"""
        try:
            # Simplified orchestration - in production, use more sophisticated routing
            chat_result = primary_agent.initiate_chat(
                recipient=supporting_agents[0],
                message=messages[0]["content"],
                max_consecutive_auto_reply=3,
                summary_method="last_msg",
            )
            return chat_result.summary if hasattr(chat_result, 'summary') else chat_result.chat_history[-1]['content']
        except Exception as e:
            logger.error(f"Agent chain execution error: {str(e)}")
            raise


class AgentOrchestrator:
    """High-level orchestrator for agent workflows"""

    def __init__(self):
        self.team = HealthcareAgentTeam()

    def execute_workflow(self, workflow_type: str, parameters: Dict) -> Dict:
        """Execute specified workflow"""
        workflows = {
            "appointment_booking": self.team.coordinate_appointment_booking,
            "care_plan": self.team.recommend_care_plan,
            "visit_summary": self.team.generate_visit_summary,
            "document_analysis": self.team.analyze_document,
        }

        if workflow_type not in workflows:
            raise ValueError(f"Unknown workflow type: {workflow_type}")

        return workflows[workflow_type](**parameters)
