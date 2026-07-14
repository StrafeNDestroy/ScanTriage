import logging

from ollama import chat 
from scantriage.domain.schema import Finding, TriageResult 

logger = logging.getLogger(__name__)
logging.basicConfig(filename=f'{__name__}.log', encoding='utf-8', level=logging.DEBUG)

class OllamaTriageModelAdapter:
    def triage(self, findings: list[Finding]) -> list[tuple[Finding,TriageResult]]:
        MODEL = 'qwen3:8b'
        SYSTEM_PROMPT =  """
        You are a security analyst triaging findings from an authorized
        penetration test. Assess severity objectively and asign the finding
        with a CVSS rating and support your assement with evidence.
        Further more include remediation to solve the issue. Ensure
        that all reponse text written is format to have 95 characters 
        max per line before wrapping. 
        """

        results = []    
        for finding in findings:
            USER_PROMPT = f'Assess this finding:\n{finding.model_dump_json()}' 

            message = [
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': USER_PROMPT},
            ]

            response = chat(
              model=MODEL,
              messages=message,
              format=TriageResult.model_json_schema(),
              options={'temperature':0}
            )

            content = response.message.content
            if not content:
                logger.warning("Model reponse empty for finding: %s",finding.service_name) 
                continue
            try:
                triage_result = TriageResult.model_validate_json(content)
            except ValueError as error:
                logger.warning("Invalid JSON: %s, %s",finding.service_name,error)
                continue 

            results.append((finding,triage_result))
        return results



