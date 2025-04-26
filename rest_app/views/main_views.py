from datetime import datetime
import requests
import os
import json
from uuid import uuid4
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from rest_app.models import Conversation, Prompt, CloudinaryFile
from rest_app.forms import FileUploadForm
from rest_app.config.cloudinary_config import upload_file
from rest_app.services.file_service import SupabaseFileService
from rest_app.utils.utils import remove_text_after


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
    prompts = [ {**obj, "response": json.loads(obj["response"]), "text": remove_text_after(obj["text"], " Here is the image URL:")} 
               if "text" and "response" in obj else obj 
               for obj in prompts 
            ]
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
        api_url = os.getenv("AI_INPAINT_API_URL")
        print(f"AI API URL: {api_url}")
        payload = {
            "user_id": user_id,
            "prompt_id": prompt["id"],
            "prompt": prompt_text if not input_image_url else f"{prompt_text} Here is the image URL: {input_image_url}",
            "conversation_id": conversation_id,
            "input_image_url": input_image_url  # ✅ pass uploaded image URL
        }
        
        response = requests.post(api_url, json=payload, timeout=9999)
        result_data = response.json()

        print("RESULT DATA:")
        print(result_data)

        # Update prompt with AI response
        Prompt.update_by_id(prompt["id"], {"response": json.dumps(result_data.get("final_response", "")), "text": f"{prompt_text} Here is the image URL: {input_image_url}"})

        # Save visual steps and final output images to supabase
        for i, step in enumerate(result_data.get("steps", [])):
            step_type = step.get("step_type", f"step_{i+1}")
            folder_type = "outputs" if step_type == "output" else "steps"
            cloud_folder = f"{user_id}/{folder_type}"

            SupabaseFileService.create_file(user_id, {
                "public_id": step["public_id"] if "public_id" in step else "",
                "filename": step["filename"] if "filename" in step else "",
                "url": step["url"] if "url" in step else "",
                "resource_type": step["resource_type"] if "resource_type" in step else "",
                "format": step.get("format", "") if "format" in step else "",
                "folder": cloud_folder,
                "prompt_id": prompt["id"],
                "user_id": user_id,
                "step_type": step_type,
                "step_index": i + 1
            })

    except Exception as e:
        messages.error(request, f"AI API Error: {str(e)}")

    return redirect("conversation_detail", conversation_id=conversation_id)