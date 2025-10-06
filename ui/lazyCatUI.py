import tkinter as tk
from tkinter import ttk
from JobsAppliedFor.writeToExcel import write_jobs_to_excel
from JobsAppliedFor.showList import load_and_display_jobs
import json

def build_ui(cohere_API):
    chat_window = None 

    # Initialize main window
    window = tk.Tk()
    window.title("Lazy Cat")
    window.minsize(800, 600)

    # Apply Vista theme
    style = ttk.Style(window)
    style.theme_use('vista')

    ttk.Label(window, text="Welcome to Lazy Cat!").pack(pady=20)

    # Button to show list of applied jobs
    def open_jobs_window():
        jobs_window = tk.Toplevel(window)
        jobs_window.title("Jobs Applied For")
        jobs_window.geometry("800x600")

        frame = ttk.Frame(jobs_window)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        load_and_display_jobs(frame)

    ttk.Button(window, text="List of Applied", width=20, command=open_jobs_window).pack(
        pady=10, padx=75, side="top", anchor="w"
    )

    # Entry and Label to send job post to API
    ttk.Label(window, text="Enter Job Post:").pack(pady=5)
    job_post_entry = tk.Text(window, width=80, height=20, wrap="word")
    job_post_entry.pack(pady=10, side="top")

    # Label to display success or error messages
    message_label = ttk.Label(window, text="", font=('Arial', 10))
    message_label.pack(pady=5)

    # Clean API response
    def _clean_response(response):
        if response.startswith("```json") and response.endswith("```"):
            lines = response.splitlines()
            return "\n".join(lines[1:-1]).strip()
        if response.startswith("```") and response.endswith("```"):
            return response[3:-3].strip()
        return response.strip()
    
    # Function to send job post to API
    def send_job_post():
        job_post = job_post_entry.get("1.0", "end-1c").strip()
        if not job_post:
            message_label.config(text="Please enter a job post.", foreground="red")
            return
        
        prompt = f"""
You are a helpful assistant that extracts key information from software engineering job postings.

Given the job posting text below, return ONLY a JSON object with the following keys:

- Job_Title
- Company
- Website (Search and Provide the URL of The actual company name not job posting site)
- Location
- Qualifications
- Responsibilities
- Skills
- Date (Provide houston tx current date unrelated to job post listing with year as 2025)

DO NOT include any explanations, additional text, or formatting.

If you cannot parse the job posting into a JSON object, respond ONLY with a string starting exactly as:

"unable to parse job post: " followed by a brief reason why.

Job posting:
{job_post}
    """
        try:
            response = cohere_API.get_cohere_response(prompt)
            cleaned_response = _clean_response(response)
    
            try:
                job_data = json.loads(cleaned_response)
                write_jobs_to_excel([job_data])
                message_label.config(text="Lazy Cat: Job data written to Excel.", foreground="green")
            except json.JSONDecodeError:
                if "unable to parse job post" in cleaned_response.lower():
                    message_label.config(text=f"Lazy Cat: {cleaned_response[:300]}", foreground="red")
                else:
                    message_label.config(text=f"Lazy Cat: Response not JSON. Showing raw output:\n{cleaned_response[:300]}", foreground="orange")

        except Exception as e:
            message_label.config(text=f"Error: {str(e)}", foreground="red")
        job_post_entry.delete("1.0", "end")

    # Send job post button
    ttk.Button(window, text="Send Job Post", command=send_job_post).pack(pady=10)

    # Function to open chat with AI window
    def open_chat_window():
        nonlocal chat_window
        if chat_window is not None and chat_window.winfo_exists():
            chat_window.lift()
            chat_window.focus_force()
            return
        
        chat_window = tk.Toplevel()
        chat_window.title("Chat with Lazy Cat")
        chat_window.minsize(1000, 600)

        ttk.Label(chat_window, text="Type your message below:").pack(pady=10)

        # Frame to hold chat box and scrollbar
        chat_frame = ttk.Frame(chat_window)
        chat_frame.pack(pady=10, padx=10, fill="both", expand=True)

        scrollbar = ttk.Scrollbar(chat_frame)
        scrollbar.pack(side="right", fill="y")

        chat_box = tk.Text(chat_frame, width=50, height=15, state="disabled", wrap="word", yscrollcommand=scrollbar.set)
        chat_box.pack(side="left", fill="both", expand=True)

        chat_box.tag_configure("bot", background="#f0f0f0")
        chat_box.tag_configure("user", justify="right")

        scrollbar.config(command=chat_box.yview)

        input_box = tk.Text(chat_window, width=50, height=4)
        input_box.pack(pady=10, padx=10)

        def send_message():
            user_text = input_box.get("1.0", "end-1c").strip()
            if not user_text:
                return "break"
            response = cohere_API.get_cohere_response(user_text)
            chat_box.config(state="normal")
            chat_box.insert("end", f"\t\t\tYou: {user_text}\n\n", "user")
            chat_box.insert("end", f"Bot: {response}\n\n", "bot")
            chat_box.see("end")
            chat_box.config(state="disabled")

            input_box.delete("1.0", "end")

        input_box.bind("<Return>", lambda event: send_message() or "break")
        ttk.Button(chat_window, text="Send", command=send_message).pack(pady=5)

    # Chat button
    ttk.Button(
        window,
        text="Chat with AI",
        command=open_chat_window,
        width=15
    ).place(relx=1.0, rely=1.0, x=-20, y=-20, anchor="se")

    window.mainloop()
