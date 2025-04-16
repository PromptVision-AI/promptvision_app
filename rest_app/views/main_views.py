import os
import requests
from datetime import datetime
import time
from uuid import uuid4
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from rest_app.models import Conversation, Prompt, CloudinaryFile
from rest_app.forms import FileUploadForm
from rest_app.config.cloudinary_config import upload_file
from rest_app.services.file_service import SupabaseFileService


def conversation_list_view(request):
    user_id = request.session.get("user_id")
    conversations = Conversation.select_by_fields(fields={"user_id": user_id}, order_by="created_at", desc=True)
    return render(request, "main.html", {
        "conversations": conversations,
        "upload_form": FileUploadForm(),
    })


def conversation_detail_view(request, conversation_id):
    user_id = request.session.get("user_id")
    conversation = Conversation.select_by_id(conversation_id)
    prompts = Prompt.select_by_fields(fields={"conversation_id": conversation_id}, order_by="created_at")
    steps, input_outputs = {}, {}

    # Get all files in this conversation
    prompt_ids = [p["id"] for p in prompts]
    files = CloudinaryFile.select_by_field_in_list("prompt_id", prompt_ids)

    for file in files:
        pid = file.get("prompt_id")
        input_type = file.get("step_type", "input")

        # Input/Output images for Chat Panel
        if input_type in ["input", "output"]:
            if pid not in input_outputs:
                input_outputs[pid] = []
            input_outputs[pid].append(file)
        else:
            # Step visualisation
            if pid not in steps:
                steps[pid] = []
            steps[pid].append(file)

    return render(request, "main.html", {
        "selected_conversation": conversation,
        "prompts": prompts,
        "conversations": Conversation.select_by_fields(fields={"user_id": user_id}, order_by="created_at", desc=True),
        "steps": steps,
        "input_outputs": input_outputs,
        "upload_form": FileUploadForm(),
    })


def send_prompt_view(request):
    if request.method != "POST":
        return redirect(settings.LOGIN_REDIRECT_URL)

    user_id = request.session.get("user_id")
    prompt_text = request.POST.get("prompt_text")
    uploaded_file = request.FILES.get("file")
    conversation_id = request.POST.get("conversation_id")

    # Create new conversation if needed
    if not conversation_id:
        conv_data = {
            "user_id": user_id,
            "title": prompt_text[:50],
            "created_at": datetime.utcnow().isoformat(),
        }
        conversation = Conversation.insert(conv_data)
        conversation_id = conversation["id"]
    else:
        conversation = Conversation.select_by_id(conversation_id)

    # Insert prompt
    prompt_data = {
        "conversation_id": conversation_id,
        "text": prompt_text,
        "created_at": datetime.utcnow().isoformat(),
    }
    prompt = Prompt.insert(prompt_data)

    input_image_url = None

    # Handle image upload
    if uploaded_file:
        cloud_folder = f"{user_id}/inputs"
        public_id = f"{prompt['id']}_input"
        upload_result = upload_file(uploaded_file, folder=cloud_folder, public_id=public_id)
        if upload_result['success']:
            input_image_url = upload_result['url']
            SupabaseFileService.create_file(user_id, {
                'public_id': upload_result['public_id'],
                'filename': uploaded_file.name,
                'url': upload_result['url'],
                'resource_type': upload_result['resource_type'],
                'format': upload_result.get('format', ''),
                'folder': cloud_folder,
                'prompt_id': prompt['id'],
                'user_id': user_id,
                'step_type': 'input',
                'step_index': 0
            })

    # Call AI API
    try:
        # api_url = os.getenv("AI_INPAINT_API_URL")
        # payload = {
        #     "prompt_id": prompt["id"],
        #     "prompt": prompt_text,
        #     "conversation_id": conversation_id,
        #     "input_image_url": input_image_url  # ✅ pass uploaded image URL
        # }
        # response = requests.post(api_url, json=payload)
        # result_data = response.json()

        result_data = {
            "final_response": "This is a simulated AI response to your prompt.",
            "steps": [
                {
                    "step_type": "object_detection",
                    "public_id": f"{user_id}/steps/{prompt['id']}_detection",
                    "filename": f"{prompt['id']}_detection.jpg",
                    "url": "https://deeplobe.ai/wp-content/uploads/2023/06/Object-detection-Real-world-applications-and-benefits.png",
                    "resource_type": "image",
                    "format": "jpg"
                },
                {
                    "step_type": "segmentation",
                    "public_id": f"{user_id}/steps/{prompt['id']}_segmentation",
                    "filename": f"{prompt['id']}_segmentation.jpg",
                    "url": "https://d12aarmt01l54a.cloudfront.net/cms/images/UserMedia-20220826182039/808-440.png",
                    "resource_type": "image",
                    "format": "jpg"
                },
                {
                    "step_type": "output",
                    "public_id": f"{user_id}/outputs/{prompt['id']}_output",
                    "filename": f"{prompt['id']}_output.jpg",
                    "url": "https://www.shutterstock.com/image-photo/hand-writing-text-output-260nw-388626541.jpg",
                    "resource_type": "image",
                    "format": "jpg"
                }
            ]
        }

        # Update prompt with AI response
        Prompt.update_by_id(prompt["id"], {"response": result_data.get("final_response", "")})

        # Save visual steps and final output images to supabase
        for i, step in enumerate(result_data.get("steps", [])):
            step_type = step.get("step_type", f"step_{i+1}")
            folder_type = "outputs" if step_type == "output" else "steps"
            cloud_folder = f"{user_id}/{folder_type}"

            SupabaseFileService.create_file(user_id, {
                "public_id": step["public_id"],
                "filename": step["filename"],
                "url": step["url"],
                "resource_type": step["resource_type"],
                "format": step.get("format", ""),
                "folder": cloud_folder,
                "prompt_id": prompt["id"],
                "user_id": user_id,
                "step_type": step_type,
                "step_index": i + 1
            })

    except Exception as e:
        messages.error(request, f"AI API Error: {str(e)}")

    return redirect("conversation_detail", conversation_id=conversation_id)

# Final output structure from the external AI API
# {
#   "final_response": "The masked object was removed and background filled.",
#   "steps": [
#     {
#       "step_type": "object_detection",
#       "public_id": "user123/steps/step1_detection",
#       "filename": "step1_detection.jpg",
#       "url": "https://res.cloudinary.com/your-cloud/image/upload/v123456/user123/steps/step1_detection.jpg",
#       "resource_type": "image",
#       "format": "jpg"
#     },
#     {
#       "step_type": "segmentation",
#       "public_id": "user123/steps/step2_segmentation",
#       "filename": "step2_segmentation.jpg",
#       "url": "https://res.cloudinary.com/your-cloud/image/upload/v123456/user123/steps/step2_segmentation.jpg",
#       "resource_type": "image",
#       "format": "jpg"
#     },
#     {
#       "step_type": "output",
#       "public_id": "user123/outputs/final_output",
#       "filename": "final_output.png",
#       "url": "https://res.cloudinary.com/your-cloud/image/upload/v123456/user123/outputs/final_output.png",
#       "resource_type": "image",
#       "format": "png"
#     }
#   ]
# }