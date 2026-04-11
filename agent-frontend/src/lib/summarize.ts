/**
 * Summarize text using Llama 4 Maverick via Bedrock proxy.
 */

const BEDROCK_URL = process.env.NEXT_PUBLIC_BEDROCK_PROXY_URL;
if (!BEDROCK_URL) {
  throw new Error('NEXT_PUBLIC_BEDROCK_PROXY_URL environment variable is required');
}
const MODEL_ID = process.env.NEXT_PUBLIC_BEDROCK_MODEL_ID;
if (!MODEL_ID) {
  throw new Error('NEXT_PUBLIC_BEDROCK_MODEL_ID environment variable is required');
}

export interface UserContext {
  name?: string;
  profession?: string;
  summary?: string;
}

export async function summarizeResponse(
  content: string,
  userContext?: UserContext | null
): Promise<string> {
  const personalization = userContext?.name
    ? `You are summarizing for ${userContext.name}, who is a ${userContext.profession || 'professional'}. Their background: ${userContext.summary || 'N/A'}. Address them by name and frame the summary from their professional perspective.`
    : '';

  const prompt = `${personalization ? personalization + '\n\n' : ''}Write exactly 2-3 sentences as an executive brief of this analysis. Be extremely concise — one sentence for the key finding, one for the risk/implication. No headers, no bullet points, no markdown, no citations, no URLs. Plain text only.\n\n---\n${content}`;

  const resp = await fetch(BEDROCK_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model_id: MODEL_ID,
      stream: true,
      prompt,
      max_gen_len: 1024,
    }),
  });

  if (!resp.ok) throw new Error(`Summarize failed: ${resp.status}`);

  const reader = resp.body?.getReader();
  if (!reader) throw new Error('No response body');

  const decoder = new TextDecoder();
  let result = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const text = decoder.decode(value, { stream: true });
    for (const line of text.split('\n')) {
      if (!line.startsWith('data: ') || line === 'data: [DONE]') continue;
      try {
        const chunk = JSON.parse(line.slice(6));
        result += chunk.generation || '';
      } catch {}
    }
  }

  return result.trim();
}
