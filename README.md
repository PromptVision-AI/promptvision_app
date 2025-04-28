# 📸 PromptVision AI – Image Inpainting Web App

> ✨ Empowering Creators to Edit Images via Natural Language ✨

PromptVision is a **Django-based web platform** that allows users to **log in**, **upload images**, and **interact with an AI** to **edit or inpaint images** using **simple natural language prompts**.  
The AI processing is handled by a dedicated **Flask-based microservice** via API communication.

Built for **content creators**, **creative teams**, and **design enthusiasts** 🎨.

---

## 🚀 Key Features

- 🛡️ **Authentication System**: Register, Login, Logout (managed via Supabase)
- 💬 **Interactive Chat Interface**: Send prompts and view AI step-by-step image edits
- 🖼️ **Image Uploads and Management**: Upload pre-inpainting images
- 🔗 **Supabase Integration**: Cloud database for users, conversations, and images
- ☁️ **Cloudinary Storage**: Store all images (inputs, outputs, steps)
- 🧠 **AI Microservice Communication**: Flask endpoint that performs inpainting and returns results
- 📄 **Conversation History**: View past prompts and AI responses
- 🎨 **Aesthetic UI/UX**: Beautiful, responsive interface with Bootstrap + SASS

---

## 🏗️ Project Architecture Overview

- **Django** 🐍 – Web App Framework (Frontend & Backend integration)
- **Flask** 🔥 – AI Inpainting Microservice (API backend)
- **Supabase** 🛢️ – Cloud Database (Authentication + Storage)
- **Cloudinary** ☁️ – Image Hosting
- **Bootstrap + SASS** 🎨 – Responsive & Aesthetic Frontend

---

## 📦 Installation and Setup Guide

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/promptvision-ai.git
cd promptvision-ai
```

---

### 2. Set up Python Virtual Environment

```bash
conda create -n promptvision_env python=3.10
conda activate promptvision_env
```

OR with `pipenv`:

```bash
pipenv shell
```

---

### 3. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

Typical main libraries include:
- Django
- djangorestframework
- python-dotenv
- cloudinary
- supabase-py

---

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```
CLOUDINARY_CLOUD_NAME=your_cloudinary_name
CLOUDINARY_API_KEY=your_cloudinary_key
CLOUDINARY_API_SECRET=your_cloudinary_secret
CLOUDINARY_FOLDER_NAME=your_cloudinary_folder
SUPABASE_HOST_URL=your_supabase_url
SUPABASE_API_SECRET=your_supabase_service_key
AI_INPAINT_API_URL=your_flask_api_url
```

✅ This `.env` will automatically be loaded by Django on startup.

---

### 5. Run Supabase Table Migrations

Inside the Django project, run:

```bash
python rest_app/utils/migrate_to_supabase.py
```

✅ This will create necessary tables:
- `accounts`
- `conversations`
- `prompts`
- `files`

---

### 6. Run the Django Web App

```bash
python manage.py runserver
```

Access it via:

🔗 http://127.0.0.1:8000/

---

## 🛠️ Main Web App Pages

| Page                  | URL                         | Description                              |
|------------------------|------------------------------|------------------------------------------|
| 🏠 Home                | `/`                          | Landing Page / Welcome screen            |
| 🔐 Login               | `/login/`                    | Login form                               |
| 📝 Register            | `/register/`                 | User registration form                  |
| 💬 Main Chat Dashboard | `/main/`                     | Conversations + Upload + Prompt chat     |
| ➡️ Submit Prompt       | `/main/send-prompt/`          | Submit a prompt and upload an image      |

---

## ⚙️ How It Works

1. 🔐 Users authenticate (register/login).
2. 🖼️ Upload a pre-inpainting image (optional).
3. 💬 Send a **natural language prompt** describing the change.
4. 🔥 Flask AI backend processes the request:
   - Detects objects
   - Segments the area
   - Inpaints based on the prompt
   - Returns **steps** + **final result**
5. 📂 Images and conversations saved to Supabase + Cloudinary.

---

## 📸 Example Prompt Scenarios

| Scenario                    | Example Prompt                                  |
|------------------------------|-------------------------------------------------|
| Remove unwanted object       | "Remove the lamp post from the background."    |
| Replace an object            | "Replace the coffee cup with a red apple."     |
| Artistic Inpainting          | "Turn the cloudy sky into a sunset scene."     |

---

## 🎨 UI/UX Highlights

- Soft gradient backgrounds
- Animated Lottie loaders while processing
- Smooth scrolling chat view
- Blurred overlay during loading
- Floating responsive layout for conversation + steps

---

## ✨ Future Enhancements (Roadmap)

- Multi-step editing history 🛤️
- Favorite prompts/save custom templates 💾
- User settings + profile page 👤
- Role-based access control 🔐

---

## 🤝 Contributing

Pull requests are welcome! 🎉

Please fork the repo and open a pull request explaining your changes.

---

## 📄 License

This project is licensed under the **MIT License**.

---

# 🎉 Thank you for being part of the creative revolution with **PromptVision AI**!
