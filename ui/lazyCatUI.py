import tkinter
from JobsAppliedFor.writeToExcel import write_jobs_to_excel
from JobsAppliedFor.showList import load_and_display_jobs
import json

def build_ui(cohere_API):
    chat_window = None 

    # Initialize main window
    window = tkinter.Tk()
    window.title("Lazy Cat")
    window.minsize(800, 600)
    tkinter.Label(window, text="Welcome to Lazy Cat!").pack(pady=20)

    # button to show list of applied jobs
    def open_jobs_window():
        jobs_window = tkinter.Toplevel(window)
        jobs_window.title("Jobs Applied For")
        jobs_window.geometry("800x600")

        frame = tkinter.Frame(jobs_window)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        load_and_display_jobs(frame)

    tkinter.Button(window, text="List of Applied", width=20, height=2, bg="white", command=open_jobs_window).pack(pady=10, padx=75, side="top", anchor="w")


    # Entry and Label to send job post to API
    tkinter.Label(window, text="Enter Job Post:").pack(pady=5)
    job_post_entry = tkinter.Text(window, width=80, height=20, wrap="word")
    job_post_entry.pack(pady=10, side="top")

    # Label to display success or error messages
    message_label = tkinter.Label(window, text="", font=('Arial', 10))
    message_label.pack(pady=5)

    #clean api response
    def _clean_response(response):
        if response.startswith("```json") and response.endswith("```"):
            lines = response.splitlines()
            # Remove the first and last lines (the fences)
            return "\n".join(lines[1:-1]).strip()
        # Remove back ticks only
        if response.startswith("```") and response.endswith("```"):
            return response[3:-3].strip()
        return response.strip()
    
    # Function to send job post to API
    def send_job_post():
        job_post = job_post_entry.get("1.0", "end-1c").strip()
        if not job_post:
            message_label.config(text="Please enter a job post.", fg="red")
            return
        
        # Prompt construction
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

DO NOT include any explanations, additional text, or formatting.

If you cannot parse the job posting into a JSON object, respond ONLY with a string starting exactly as:

"unable to parse job post: " followed by a brief reason why.

Job posting:
{job_post}
    """
        try:
            # Get response from API
            response = cohere_API.get_cohere_response(prompt)
            cleaned_response = _clean_response(response)
    
            try:
                job_data = json.loads(cleaned_response)
                write_jobs_to_excel([job_data])
                message_label.config(text="Lazy Cat: Job data written to Excel.", fg="green")
            except json.JSONDecodeError:
                if "unable to parse job post" in cleaned_response.lower():
                    message_label.config(text=f"Lazy Cat: {cleaned_response[:300]}", fg="red")
                else:
                    message_label.config(text=f"Lazy Cat: Response not JSON. Showing raw output:\n{cleaned_response[:300]}", fg="orange")

        except Exception as e:
            message_label.config(text=f"Error: {str(e)}", fg="red")
        job_post_entry.delete("1.0", "end")

    #Button to send job post
    send_job_post_button = tkinter.Button(window, text="Send Job Post", bg="white", command=send_job_post)
    send_job_post_button.pack(pady=10)
    

    # Function to open chat with AI window
    def open_chat_window():
        nonlocal chat_window # Use nonlocal to modify the outer variable
        if chat_window is not None and chat_window.winfo_exists():
            chat_window.lift()  # Bring the window to the front
            chat_window.focus_force()  # Focus on it
            return
        
        chat_window = tkinter.Toplevel()
        chat_window.title("Chat with Lazy Cat")
        chat_window.minsize(500, 400)

        tkinter.Label(chat_window, text="Type your message below:").pack(pady=10)
        chat_box = tkinter.Text(chat_window, width=50, height=15, state="disabled", wrap="word")
        chat_box.pack(pady=10, padx=10)
        input_box = tkinter.Text(chat_window, width=50, height=4)
        input_box.pack(pady=10, padx=10)

        def send_message():
            user_text = input_box.get("1.0", "end-1c").strip()
            if not user_text:
                return "break"
            response = cohere_API.get_cohere_response(user_text)
            chat_box.config(state="normal")
            chat_box.insert("end", f"You: {user_text}\n")
            chat_box.insert("end", f"Bot: {response}\n")
            chat_box.config(state="disabled")
            input_box.delete("1.0", "end")

        input_box.bind("<Return>", lambda event: send_message() or "break")
        send_button = tkinter.Button(chat_window, text="Send", command=send_message)
        send_button.pack(pady=5)

    # Add the "Open Chat" button to the main window
    chat_button = tkinter.Button(
    text="chat with AI",
    command=open_chat_window,
    width=10,
    height=1,
    bg="#4CAF50",
    fg="white",
    font=("Arial", 14, "bold"),)
    chat_button.place(relx=1.0, rely=1.0, x=-20, y=-20, anchor="se")

    window.mainloop()
