# path: app/core/guardrails.py
import re
from typing import Any, Dict, List, Optional, Tuple

from app.core.state import TraceTracker


class NexusGuardrails:
    """
    Enterprise-Grade Governance, Input Guardrails, & Token-Masking Engine.
    Intercepts user inquiries, scrubs and masks PII/PHI tokens locally,
    and enforces strict technical workspace alignment boundaries.
    """

    def __init__(self) -> None:
        # Pre-compile adversarial regex patterns to guarantee sub-millisecond execution
        self.injection_patterns = [
            re.compile(r"ignore\s+(?:all\s+)?prior\s+instructions", re.IGNORECASE),
            re.compile(
                r"reveal\s+(?:your\s+)?system\s+(?:prompt|instructions)", re.IGNORECASE
            ),
            re.compile(r"you\s+are\s+now\s+an?\s+unrestricted", re.IGNORECASE),
            re.compile(r"output\s+the\s+above\s+text\s+instead", re.IGNORECASE),
            re.compile(r"system\s*prompt\s*disclosure", re.IGNORECASE),
        ]

        # Pre-compile broad structural patterns for system identity exploration
        self.meta_patterns = [
            re.compile(
                r"\b(?:who|what)\s+(?:are|is)\s+(?:you|your\s+name|nexa|nexusmind)\b",
                re.IGNORECASE,
            ),
            re.compile(
                r"\bwhat\s+(?:can\s+you\s+do|are\s+your\s+capabilities)\b",
                re.IGNORECASE,
            ),
            re.compile(r"\b(?:help|options|status)\b", re.IGNORECASE),
        ]

        # High-performance regular expression map for PII and PHI compliance scrubbing
        self.pii_phi_patterns: Dict[str, re.Pattern] = {
            "SOCIAL_SECURITY_NUMBER": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
            "MEDICAL_RECORD_NUMBER": re.compile(r"\bMRN-?\d{6,8}\b", re.IGNORECASE),
            "IPv4_ADDRESS": re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
            "CREDIT_CARD_NUMBER": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
        }

        # Broad technical boundary allowed-list tokens matching technical study preference
        self.valid_domains = [
            "code",
            "algorithm",
            "learn",
            "study",
            "explain",
            "how to",
            "why",
            "architecture",
            "framework",
            "database",
            "ai",
            "ml",
            "system",
            "graph",
            "langgraph",
            "chromadb",
            "ollama",
            "python",
            "docker",
            "math",
            "calculus",
            "linear algebra",
            "tensor",
            "matrix",
            "vector",
            "embedding",
            "rag",
            "search",
        ]

    def mask_sensitive_tokens(self, text: str) -> Tuple[str, List[str]]:
        """
        Scans raw buffer text and executes token-masking/redaction algorithms.
        Replaces raw compliance vulnerabilities with structured string tokens.
        """
        sanitized_text = text
        detected_violations = []

        for entity_label, compiled_regex in self.pii_phi_patterns.items():
            if compiled_regex.search(sanitized_text):
                detected_violations.append(entity_label)
                # Apply token substitution across the string sequence
                sanitized_text = compiled_regex.sub(
                    f"[{entity_label}_REDACTED]", sanitized_text
                )

        return sanitized_text, detected_violations

    def verify_input_safety(
        self, user_message: str, existing_trace: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, List[str], str, List[dict]]:
        """
        Runs comprehensive verification checks against raw user text strings.
        Applies data masking and enforces structural domain compliance.

        Returns:
            Tuple[bool, List[str], str, List[dict]]:
            (governance_passed, flags_list, masked_message_text, pipeline_trace_history)
        """
        # 🎯 CENTRALIZED DESIGN: Instantiate the global tracker structure smoothly
        tracker = TraceTracker(trace_state=existing_trace)

        if user_message is None:
            tracker.log_step(
                "User Request Entry", "Null Payload Intercepted", status_icon="🔴"
            )
            return False, ["EMPTY_INPUT_REJECTION"], "", tracker.timeline

        clean_text = str(user_message).strip()
        flags: List[str] = []

        # Use clean log_step API hooks everywhere
        tracker.log_step("User Request Entry", "Payload Ingested")
        tracker.log_step("Security Check Engine", "Nexus Guardrails V2 Active")

        # 2. Inspect for Empty Input explicitly
        if not clean_text:
            tracker.log_step(
                "Security Intercept",
                "Empty stream buffer string submitted",
                status_icon="🔴",
            )
            return False, ["EMPTY_INPUT_REJECTION"], "", tracker.timeline

        # 3. Inspect for Prompt Injection Vectors
        for pattern in self.injection_patterns:
            if pattern.search(clean_text):
                flags.append("PROMPT_INJECTION_ATTEMPT")
                break

        if "PROMPT_INJECTION_ATTEMPT" in flags:
            tracker.log_step(
                "Security Intercept",
                "Malicious override sequence blocked",
                status_icon="🔴",
            )
            return False, flags, clean_text, tracker.timeline

        # 4. Handle Identity Discovery Exceptions (Pass-through smoothly)
        is_meta_exploration = any(
            pattern.search(clean_text) for pattern in self.meta_patterns
        )
        if is_meta_exploration:
            tracker.log_step("Identity Query Pass", "System info exploration cleared")
            return True, [], clean_text, tracker.timeline

        # 5. EXECUTE TOKEN MASKING (PII/PHI Compliance Scrubbing)
        masked_text, triggered_leaks = self.mask_sensitive_tokens(clean_text)
        if triggered_leaks:
            flags.extend(triggered_leaks)
            tracker.log_step(
                "Token Masker Active",
                f"Scrubbed sensitive data vectors: {triggered_leaks}",
                status_icon="🟡",
            )

        # 6. Enforce Strict Domain Alignment Heuristics against the masked text
        lower_text = masked_text.lower()
        has_domain_match = any(domain in lower_text for domain in self.valid_domains)
        is_casual_greeting = any(
            greet in lower_text for greet in ["hi", "hello", "hey", "clear", "test"]
        )

        if not (has_domain_match or is_casual_greeting):
            flags.append("OUT_OF_DOMAIN_REJECTION")
            tracker.log_step(
                "Domain Alignment Failure",
                "Query bounds fell outside technical domain specifications",
                status_icon="🔴",
            )

        # Evaluate if any critical blocking security checks failed
        critical_failures = [
            "EMPTY_INPUT_REJECTION",
            "PROMPT_INJECTION_ATTEMPT",
            "OUT_OF_DOMAIN_REJECTION",
        ]
        governance_passed = not any(fail in flags for fail in critical_failures)

        return governance_passed, flags, masked_text, tracker.timeline

    def intercept_and_generate_rejection(self, flags: List[str]) -> str:
        """Formulates a structured system refusal card based on safety violations."""
        reasons = []

        if "EMPTY_INPUT_REJECTION" in flags:
            reasons.append("❌ Empty stream buffer string submitted.")
        if "PROMPT_INJECTION_ATTEMPT" in flags:
            reasons.append(
                "🚨 **Security Protocol Alert:** Malicious override sequence detected. System instructions shield active."
            )
        if "OUT_OF_DOMAIN_REJECTION" in flags:
            reasons.append(
                "⚠️ **Domain Alignment Flag:** NexusMind workspace limits are configured to focus on technical study, AI/ML engineering, and programming utilities."
            )

        if flags and not reasons:
            reasons.append(
                "🛡️ Security metric exception intercepted by compliance layers."
            )

        refusal_markdown = (
            "### 🛡️ NexusMind Governance Intercept\n"
            "Your query request vector failed internal input validation policies.\n\n"
            + "\n".join([f"- {r}" for r in reasons])
            + "\n\n*Adjust your engineering query or switch tracking contexts to reset the node.*"
        )
        return refusal_markdown
