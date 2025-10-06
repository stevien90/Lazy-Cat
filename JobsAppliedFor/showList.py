import pandas as pd
import tkinter as tk
from api import cohere_API
import webbrowser

def load_and_display_jobs(parent_frame):
    # Clear existing widgets
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # --- Scrollable canvas setup ---
    canvas = tk.Canvas(parent_frame)
    scrollbar = tk.Scrollbar(parent_frame, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas)

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # --- Load job data ---
    try:
        df = pd.read_excel('JobsAppliedFor/jobs_applied.xlsx')
    except FileNotFoundError:
        tk.Label(scroll_frame, text="No job data found. Please apply for jobs first.", font=('Arial', 12), fg="red").pack(pady=10)
        return
    
    if df.empty:
        tk.Label(scroll_frame, text="Job List is empty", font=('Arial', 12), fg="red").pack(pady=10)
        return 


    # --- Show job list buttons ---
    def change_status(row_index, status, job_button):
        df.at[row_index, 'Status'] = status
        df.to_excel('JobsAppliedFor/jobs_applied.xlsx', index=False)

        # Change button background based on status
        if status == "Interviewed":
            job_button.config(bg="green")
        elif status == "No Call Back":
            job_button.config(bg="red")

     # --- Show job list buttons ---
    for idx, row in df.iterrows():
        title = row.get("Job_Title", f"Job {idx + 1}")
        company = row.get("Company", "Unknown Company")
        btn_text = f"{title} at {company}"

        status = row.get("Status", "")
        bg_color = "SystemButtonFace"  # default

        if status == "Interviewed":
            bg_color = "green"
        elif status == "No Call Back":
            bg_color = "red"

        # Create main job button with color
        row_frame = tk.Frame(scroll_frame)
        row_frame.pack(fill="x", pady=4, padx=10)

        job_button = tk.Button(
            row_frame,
            text=btn_text,
            wraplength=500,
            anchor="w",
            justify="left",
            bg=bg_color,
            command=lambda r=row: show_job_detail(r)
        )
        job_button.pack(side="left", fill="x", expand=True)

        green_button = tk.Button(
            row_frame,
            bg="green",
            width=2,
            height=1,
            relief="raised",
            command=lambda idx=idx, jb=job_button: change_status(idx, "Interviewed", jb)
        )
        green_button.pack(side="left", padx=2)

        red_button = tk.Button(
            row_frame,
            bg="red",
            width=2,
            height=1,
            relief="raised",
            command=lambda idx=idx, jb=job_button: change_status(idx, "No Call Back", jb)
        )
        red_button.pack(side="left", padx=2)


    # --- Function to show job details ---
    def show_job_detail(row):
        for widget in scroll_frame.winfo_children():
            widget.destroy()

        def call_api_and_show_details(value):
            #Construct a prompt for the API
            prompt = f"Tell me more about: {value} in 200 words or less"
            try:
                response = cohere_API.get_cohere_response(prompt)
            except Exception as e:
                response = f"Error fetching details: {str(e)}"
            ai_response_window_popup = tk.Toplevel()
            ai_response_window_popup.title(f"{value}")
            ai_response_window_popup.geometry("600x400")

            tk.Label(ai_response_window_popup, text=f"{value}:", font=("Arial", 12, "bold")).pack(pady=10)
            text_box=tk.Text(ai_response_window_popup, wrap="word", font=("Arial", 10))
            text_box.insert("1.0", response)
            text_box.configure(state="disabled")
            text_box.pack(expand=True, fill="both", padx=10, pady=10)

        for field, value in row.items():
            if isinstance(value, list):
                value = ", ".join(value)
            elif isinstance(value, float) and pd.isna(value):
                value = "(not provided)"

            # Field title
            tk.Label(scroll_frame, text=f"{field}:", font=("Arial", 10, "bold"), anchor="w").pack(anchor="w", padx=10, pady=(10, 0))

            # Special Case: Job Title and Company as clickable ai search
            if field == "Job_Title" or field == "Company":
                clickable_label = tk.Label(
                    scroll_frame,
                    text=value,
                    font=("Arial", 10, "underline"),
                    fg="blue",
                    wraplength=550,
                    justify="left",
                    anchor="w",
                    cursor="hand2"
                )
                clickable_label.pack(anchor="w", padx=20)
                clickable_label.bind("<Button-1>", lambda e, v=value: call_api_and_show_details(v))
            # Special Case: Website as clickable link
            elif field.lower() =="website" and value.startswith("http"):
                website_label = tk.Label(
                    scroll_frame,
                    text=value,
                    font=("Arial", 10, "underline"),
                    fg="blue",
                    wraplength=550,
                    justify="left",
                    anchor="w",
                    cursor="hand2"
                )
                website_label.pack(anchor="w", padx=20)
                website_label.bind("<Button-1>", lambda e, url=value: webbrowser.open_new(url))
            # Special Case: Search skills with AI on click
            elif field == "Skills":
                skills = [skill.strip() for skill in value.split(";") if skill.strip()]
                for skill in skills:
                    skill_label = tk.Label(
                        scroll_frame,
                        text=skill,
                        font=("Arial", 10, "underline"),
                        fg="blue",
                        wraplength=550,
                        justify="left",
                        anchor="w",
                        cursor="hand2"
                    )
                    skill_label.pack(anchor="w", padx=20)
                    skill_label.bind("<Button-1>", lambda e, v=skill: call_api_and_show_details(v))
            else:
                tk.Label(
                    scroll_frame,
                    text=value,
                    wraplength=550,
                    justify="left",
                    anchor="w"
                ).pack(anchor="w", padx=20)
            
            

        # Back button
        tk.Button(scroll_frame, text="⬅ Back to Job List", command=lambda: load_and_display_jobs(parent_frame)).pack(pady=20)