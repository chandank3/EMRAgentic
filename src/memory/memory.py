"""Agent memory management - conversation history and context"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """Single memory entry"""
    timestamp: str
    interaction_id: str
    agent_name: str
    action_type: str  # appointment, care_plan, medication, document, etc.
    patient_id: str
    content: str
    metadata: Dict[str, Any]
    outcome: Optional[str] = None


class AgentMemory:
    """In-memory conversation and decision history for agents"""

    def __init__(self, max_entries: int = 10000):
        self.max_entries = max_entries
        self.memory: List[MemoryEntry] = []
        self.patient_context: Dict[str, Dict] = {}  # Patient-specific context

    def store_interaction(
        self,
        interaction_id: str,
        agent_name: str,
        action_type: str,
        patient_id: str,
        content: str,
        metadata: Optional[Dict] = None,
        outcome: Optional[str] = None
    ) -> None:
        """Store an agent interaction in memory"""
        entry = MemoryEntry(
            timestamp=datetime.utcnow().isoformat(),
            interaction_id=interaction_id,
            agent_name=agent_name,
            action_type=action_type,
            patient_id=patient_id,
            content=content,
            metadata=metadata or {},
            outcome=outcome
        )
        
        self.memory.append(entry)
        
        # Maintain size limit
        if len(self.memory) > self.max_entries:
            self.memory = self.memory[-self.max_entries:]
        
        logger.debug(f"Stored memory entry: {interaction_id} for patient {patient_id}")

    def get_patient_history(self, patient_id: str, limit: int = 20) -> List[Dict]:
        """Get recent interaction history for a patient"""
        patient_entries = [
            entry for entry in self.memory
            if entry.patient_id == patient_id
        ]
        
        # Sort by timestamp descending and return recent
        patient_entries.sort(key=lambda x: x.timestamp, reverse=True)
        return [asdict(entry) for entry in patient_entries[:limit]]

    def get_agent_context(self, patient_id: str, agent_name: str) -> Dict:
        """Get context specific to an agent's work with patient"""
        history = self.get_patient_history(patient_id, limit=10)
        
        # Filter for this agent's interactions
        agent_interactions = [
            h for h in history
            if h['agent_name'] == agent_name
        ]
        
        return {
            "patient_id": patient_id,
            "agent_name": agent_name,
            "recent_interactions": agent_interactions,
            "context": self.patient_context.get(patient_id, {})
        }

    def update_patient_context(self, patient_id: str, context: Dict) -> None:
        """Update patient-specific context"""
        if patient_id not in self.patient_context:
            self.patient_context[patient_id] = {}
        
        self.patient_context[patient_id].update(context)
        logger.debug(f"Updated context for patient {patient_id}")

    def get_decision_rationale(self, interaction_id: str) -> Optional[Dict]:
        """Retrieve decision rationale for an interaction"""
        for entry in self.memory:
            if entry.interaction_id == interaction_id:
                return {
                    "interaction_id": interaction_id,
                    "agent": entry.agent_name,
                    "action": entry.action_type,
                    "timestamp": entry.timestamp,
                    "content": entry.content,
                    "metadata": entry.metadata,
                    "outcome": entry.outcome
                }
        return None

    def search_memory(self, patient_id: str, keywords: List[str]) -> List[Dict]:
        """Search memory for entries containing keywords"""
        results = []
        
        for entry in self.memory:
            if entry.patient_id == patient_id:
                content_lower = entry.content.lower()
                if any(keyword.lower() in content_lower for keyword in keywords):
                    results.append(asdict(entry))
        
        return results


class ConversationHistory:
    """Track conversation history between agents and humans"""

    def __init__(self):
        self.conversations: Dict[str, List[Dict]] = {}

    def start_conversation(self, conversation_id: str) -> None:
        """Start a new conversation"""
        self.conversations[conversation_id] = []

    def add_message(
        self,
        conversation_id: str,
        speaker: str,  # "agent" or "human"
        agent_name: str,
        message: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """Add message to conversation"""
        if conversation_id not in self.conversations:
            self.start_conversation(conversation_id)
        
        self.conversations[conversation_id].append({
            "timestamp": datetime.utcnow().isoformat(),
            "speaker": speaker,
            "agent_name": agent_name,
            "message": message,
            "metadata": metadata or {}
        })

    def get_conversation(self, conversation_id: str) -> List[Dict]:
        """Retrieve full conversation"""
        return self.conversations.get(conversation_id, [])

    def get_last_message(self, conversation_id: str) -> Optional[Dict]:
        """Get the last message in conversation"""
        conv = self.conversations.get(conversation_id, [])
        return conv[-1] if conv else None

    def summarize_conversation(self, conversation_id: str) -> Dict:
        """Generate summary of conversation"""
        conv = self.conversations.get(conversation_id, [])
        
        if not conv:
            return {"summary": "No conversation found"}
        
        return {
            "conversation_id": conversation_id,
            "total_messages": len(conv),
            "first_message": conv[0]["timestamp"],
            "last_message": conv[-1]["timestamp"],
            "participants": set(m["agent_name"] for m in conv),
            "messages": conv
        }
