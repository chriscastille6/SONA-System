"""
Audit logging for IRB AI API calls.

Logs prompt/response hashes (not full content) for external providers to
support FERPA compliance forensics without storing education records in logs.
"""
import hashlib
import logging

logger = logging.getLogger(__name__)


def _hash_content(content: str) -> str:
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def log_ai_api_call(
    *,
    agent_name: str,
    provider: str,
    model: str,
    prompt: str,
    response: str,
    screening_metadata: dict | None = None,
    study_id: str | None = None,
    actor_id: str | None = None,
) -> None:
    """
    Record an AI API call to AuditLog and application logger.

    External providers: hash-only storage in metadata.
    Ollama (institutional): hash-only by default; full content never logged here.
    """
    prompt_hash = _hash_content(prompt)
    response_hash = _hash_content(response) if response else ''

    metadata = {
        'agent': agent_name,
        'provider': provider,
        'model': model,
        'prompt_hash': prompt_hash,
        'response_hash': response_hash,
        'prompt_length': len(prompt),
        'response_length': len(response) if response else 0,
        'external_provider': provider != 'ollama',
    }
    if screening_metadata:
        metadata['screening'] = screening_metadata
    if study_id:
        metadata['study_id'] = study_id

    try:
        from apps.credits.models import AuditLog

        AuditLog.objects.create(
            actor_id=actor_id,
            action='ai_api_call',
            entity='irb_ai',
            entity_id=None,
            metadata=metadata,
        )
    except Exception:
        logger.exception('Failed to write AI API call to AuditLog')

    logger.info(
        'ai_api_call agent=%s provider=%s model=%s prompt_hash=%s screening=%s',
        agent_name,
        provider,
        model,
        prompt_hash[:16],
        screening_metadata.get('risk_level') if screening_metadata else 'n/a',
    )
