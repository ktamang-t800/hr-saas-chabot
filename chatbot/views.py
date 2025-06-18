from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import HRPolicyDocument
from dotenv import load_dotenv
load_dotenv()

@login_required
def home(request):
    user_files = HRPolicyDocument.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'chatbot/home.html', {'user_files': user_files})

@login_required
def upload_policy(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')
    if request.method == 'POST' and request.FILES.get('file'):
        HRPolicyDocument.objects.create(user=request.user, file=request.FILES['file'])
        return redirect('/upload/')
    files = HRPolicyDocument.objects.filter(user=request.user)
    return render(request, 'chatbot/upload.html', {'files': files})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'chatbot/register.html', {'form': form})
import os
import PyPDF2
from django.conf import settings
from .models import HRPolicyDocument

def chat_with_policy(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')
    files = HRPolicyDocument.objects.filter(user=request.user)
    answer = None

    if request.method == "POST":
        selected_id = request.POST.get("file_id")
        question = request.POST.get("question", "")
        selected_file = files.filter(id=selected_id).first()
        if selected_file and question:
            # Read PDF content
            file_path = os.path.join(settings.MEDIA_ROOT, selected_file.file.name)
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                all_text = ""
                for page in reader.pages:
                    all_text += page.extract_text() or ""
            # --- (Simple version) Use OpenAI API to answer ---
            from openai import OpenAI
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            prompt = (
                f"You are an HR assistant. Answer the user's question ONLY using the information below from the HR policy. "
                f"If the answer is not found, say 'I couldn't find this information in the provided HR policy.'\n\n"
                f"HR Policy Excerpt:\n{all_text[:4000]}\n\n"   # Limit to 4000 chars for safety
                f"Question: {question}\n"
                f"Answer:"
            )
            response = client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[
                    {"role": "system", "content": "You are an HR assistant who answers using the company policy document."},
                    {"role": "user", "content": prompt}
                ]
            )
            answer = response.choices[0].message.content

        return render(request, "chatbot/chat.html", {
            "files": files,
            "selected_id": selected_id,
            "question": question,
            "answer": answer,
        })

    return render(request, "chatbot/chat.html", {
        "files": files,
    })
from django.contrib import messages

@login_required
def delete_policy(request, file_id):
    file = HRPolicyDocument.objects.filter(id=file_id, user=request.user).first()
    if file:
        file.file.delete()  # remove from disk
        file.delete()       # remove from database
        messages.success(request, "File deleted successfully.")
    else:
        messages.error(request, "File not found or permission denied.")
    return redirect('home')
