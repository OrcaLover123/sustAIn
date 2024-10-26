# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Shows how to use the Converse API with Anthropic Claude 3 Sonnet (on demand).
"""

import logging
import boto3
import os

from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def generate_conversation(bedrock_client,
                          model_id,
                          system_prompts,
                          messages):
    """
    Sends messages to a model.
    Args:
        bedrock_client: The Boto3 Bedrock runtime client.
        model_id (str): The model ID to use.
        system_prompts (JSON) : The system prompts for the model to use.
        messages (JSON) : The messages to send to the model.

    Returns:
        response (JSON): The conversation that the model generated.

    """

    logger.info("Generating message with model %s", model_id)

    # Inference parameters to use.
    temperature = 0.5
    top_k = 200

    # Base inference parameters to use.
    inference_config = {"temperature": temperature}
    # Additional inference parameters to use.
    additional_model_fields = {"top_k": top_k}

    # Send the message.
    response = bedrock_client.converse(
        modelId=model_id,
        messages=messages,
        system=system_prompts,
        inferenceConfig=inference_config,
        additionalModelRequestFields=additional_model_fields
    )

    # Log token usage.
    token_usage = response['usage']
    logger.info("Input tokens: %s", token_usage['inputTokens'])
    logger.info("Output tokens: %s", token_usage['outputTokens'])
    logger.info("Total tokens: %s", token_usage['totalTokens'])
    logger.info("Stop reason: %s", response['stopReason'])

    return response

DEFAULT_SYSTEM_PROMPT = "You are a tool that judges carbon emissions of products based on their materials, weights, and countries of origin. You are given link(s), separated by commas. PROVIDE THE EXACT FORMAT AND NOTHING BESIDES THIS AND DO NOT INCLUDE NEW LINES: [{“product_name”: <a two to six word summary of the product name>, “index”: <a number from 0.10 to 0.90 that compares how carbon friendly the products are between each other with the lower end being less emission friendly and the higher being more emission friendly>}, { … }] The length of the list returned must match the number of links given."



# takes links separated by commas: abc.com, xyz.com, ...
def get_product_details_csv(links: str, SYSTEM_PROMPT=DEFAULT_SYSTEM_PROMPT):
    """
    Entrypoint for Anthropic Claude 3 Sonnet example.
    """

    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s: %(message)s")

    model_id = "anthropic.claude-3-sonnet-20240229-v1:0"


    # Setup the system prompts and messages to send to the model.
    system_prompts = [{"text": SYSTEM_PROMPT}]

    message = {
        "role": "user",
        "content": [{
            "text": links}]
    }

    try:

        bedrock_client = boto3.client("bedrock-runtime", region_name="us-west-2",
                                      aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                                      aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"]
                                      )

        response = generate_conversation(bedrock_client, model_id, system_prompts, [message])

        output_message = response['output']['message']


        return output_message


    except ClientError as err:
        message = err.response['Error']['Message']
        logger.error("A client error occurred: %s", message)
        print(f"A client error occured: {message}")

    else:
        print(
            f"Finished generating text with model {model_id}.")



if __name__ == "__main__":
    links = [
        "https://www.amazon.com/CYHTWSDJ-Shoulder-Handbag-Clutch-Closure/dp/B099DDH2RG/ref=sr_1_5?crid=1LHN4DJH9VFB6&dib=eyJ2IjoiMSJ9.BZc5eh3MPi6yoYyZGCuCwgPIY8tPJ3bmkt8A2lDOb_Mk3HVUmRzZBSX_gTwM16mTOFT2DgJU9WKW6UcY2qGHBYPJte23vSosNQL8QaHJWuvtGFe10DGdwWArEsMSjIz7baZU1WfXFtnBvEku19x4GxLif9RT9jdEZjey2PE0ZH-NvfWjJ7N2d_5WG04spa3ZRJ2IP_V3MAfF4hCtPrMO7igfFJNwHJSMikvx2MkIiLs7u_srjxsF6kYmFlxt228YFcjjgqekVyFPsCYDTxM6YFl2I8EoX1VJ_bPzNxcKhCU.J6l5CKNOHy3CbD1hkRWPzsr9rDv_LdBcr3ls8xEJkuU&dib_tag=se&keywords=hand+bags&qid=1728788975&sprefix=hand+ba%2Caps%2C165&sr=8-5",
        "https://www.amazon.com/Prada-Vitello-Leather-Satchel-1BC051/dp/B079XZT2GL/ref=sr_1_1?crid=LV7HKY59VKP7&dib=eyJ2IjoiMSJ9.d54CJ06hjd2mgQ88ixX34rwTCiqLtgIC3Z-jVajXT7ANc-0cfTO_qZaYGLPW8ql2v29rE3rergdqTcCNowmwlvo3QWnfx0bo5KAvHLIlZftQEQekuoWUS4W2QcP2RutzEh9zbeuJWVnfH4wSRI7OM8iCUOL6eJXF2X1_69oAN6520kOS9l_6c5f4HPSllN9DEvqzZMLSjvyvwsKluzlJn4LnRWC1yZJzUZYf-VnF11iOHzzf9MqFVI4diJ6BXPk7bZ_COoDx7m0garLZFzrsDLur_scGI9TDN8n0n1GgaS4.auIzG_0XC9va_U9f6T_u9H0GkyKd5lKJGC-4bQB2-zA&dib_tag=se&keywords=hand+bags&qid=1728789465&refinements=p_36%3A265000-&rnid=2661611011&sprefix=hand+bags+%2Caps%2C124&sr=8-1"]

    get_product_details_csv(links=links)
