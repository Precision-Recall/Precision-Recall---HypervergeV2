import { BedrockRuntimeClient, InvokeModelWithResponseStreamCommand, InvokeModelCommand } from "@aws-sdk/client-bedrock-runtime";

const client = new BedrockRuntimeClient({});

export const handler = awslambda.streamifyResponse(
  async (event, responseStream, _context) => {
    try {
      const body = JSON.parse(event.body || "{}");
      const { model_id, stream = true, content_type = "application/json", accept = "application/json", ...modelPayload } = body;

      if (!model_id) {
        responseStream.write(JSON.stringify({ error: "model_id is required" }));
        responseStream.end();
        return;
      }

      if (stream) {
        responseStream.setContentType("text/event-stream");

        const command = new InvokeModelWithResponseStreamCommand({
          modelId: model_id,
          contentType: content_type,
          accept,
          body: JSON.stringify(modelPayload),
        });

        const response = await client.send(command);

        for await (const event of response.body) {
          if (event.chunk?.bytes) {
            const chunk = JSON.parse(new TextDecoder().decode(event.chunk.bytes));
            responseStream.write(`data: ${JSON.stringify(chunk)}\n\n`);
          }
        }

        responseStream.write("data: [DONE]\n\n");
      } else {
        responseStream.setContentType("application/json");

        const command = new InvokeModelCommand({
          modelId: model_id,
          contentType: content_type,
          accept,
          body: JSON.stringify(modelPayload),
        });

        const response = await client.send(command);
        responseStream.write(new TextDecoder().decode(response.body));
      }

      responseStream.end();
    } catch (err) {
      try {
        responseStream.write(JSON.stringify({ error: err.message }));
        responseStream.end();
      } catch (_) {}
    }
  }
);
