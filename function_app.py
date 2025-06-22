import logging
import os
from azure.storage.blob import BlobServiceClient
import azure.functions as func
import azure.durable_functions as df
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import openai
from datetime import datetime

my_app = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)
blob_service_client = BlobServiceClient.from_connection_string(os.environ.get("BLOB_STORAGE_ENDPOINT"))

@my_app.blob_trigger(arg_name="myblob", path="input", connection="BLOB_STORAGE_ENDPOINT")
@my_app.durable_client_input(client_name="client")
async def blob_trigger(myblob: func.InputStream, client):
    logging.info(f"Python blob trigger function processed blob"
                f"Name: {myblob.name}"
                f"Blob Size: {myblob.length} bytes")

    blobName = myblob.name.split("/")[1]
    await client.start_new("process_document", client_input=blobName)

# ORCHESTRATOR FUNCTION
@my_app.orchestration_trigger(context_name="context")
def process_document(context):
    blobName: str = context.get_input()
    logging.info(f"📥 Orchestrator started for blob: {blobName}")

    retry_options = df.RetryOptions(5000, 3)

    result = yield context.call_activity_with_retry("analyze_pdf", retry_options, blobName)
    logging.info("✅ PDF analysis completed.")

    result2 = yield context.call_activity_with_retry("summarize_text", retry_options, result)
    logging.info("✅ Text summarization completed.")

    result3 = yield context.call_activity_with_retry("write_doc", retry_options, {
        "blobName": blobName,
        "summary": result2
    })
    logging.info(f"✅ Summary written to blob: {result3}")
    return f"Successfully uploaded summary as {result3}"

# ACTIVITY: Analyze PDF using Form Recognizer
@my_app.activity_trigger(input_name='blobName')
def analyze_pdf(blobName):
    logging.info(f"🔍 Analyzing PDF: {blobName}")
    container_client = blob_service_client.get_container_client("input")
    blob_client = container_client.get_blob_client(blobName)
    blob = blob_client.download_blob().read()

    key = os.environ["COGNITIVE_SERVICES_KEY"]
    endpoint = os.environ["COGNITIVE_SERVICES_ENDPOINT"]
    credential = AzureKeyCredential(key)
    document_analysis_client = DocumentAnalysisClient(endpoint, credential)

    poller = document_analysis_client.begin_analyze_document("prebuilt-layout", document=blob, locale="en-US")
    result = poller.result().pages

    doc = ""
    for page in result:
        for line in page.lines:
            doc += line.content + " "

    logging.info(f"📄 Extracted {len(doc)} characters from PDF.")
    return doc

# ACTIVITY: Summarize Text using Azure OpenAI
@my_app.activity_trigger(input_name='results')
def summarize_text(results):
    logging.info("⚠️ Mocking summarization due to Azure OpenAI quota limits.")
    mock_summary = "This is a mock summary of the uploaded PDF document. Replace this with actual output once your Azure OpenAI quota is approved."
    return {"content": mock_summary}

# ACTIVITY: Save Summary to Output Blob
@my_app.activity_trigger(input_name='results')
def write_doc(results):
    logging.info("💾 Saving summary to 'output' blob container.")
    container_client = blob_service_client.get_container_client("output")

    summary_name = results['blobName'] + "-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    fileName = summary_name + ".txt"

    container_client.upload_blob(name=fileName, data=results['summary']['content'], overwrite=True)
    logging.info(f"✅ Summary saved as: {fileName}")
    return fileName

@app.route(route="TestHttp", auth_level=func.AuthLevel.FUNCTION)
def TestHttp(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )