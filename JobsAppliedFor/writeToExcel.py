import os
import pandas as pd

def write_jobs_to_excel(data, filename=None):
    """
    Appends job dictionaries to an Excel file inside 'JobsAppliedFor' folder,
    avoiding duplicates based on Job_Title and Company.

    :param data: List of dictionaries with job info.
    :param filename: Optional filename (default: 'jobs_applied.xlsx' in 'JobsAppliedFor' folder)
    """
    folder = "JobsAppliedFor"
    os.makedirs(folder, exist_ok=True)

    # Set default filename
    if filename is None:
        filename = os.path.join(folder, "jobs_applied.xlsx")
    else:
        filename = os.path.join(folder, filename)

    # Flatten the incoming data
    flat_data = []
    for job in data:
        flat_job = job.copy()
        flat_job["Qualifications"] = "; ".join(job.get("Qualifications", []))
        flat_job["Responsibilities"] = "; ".join(job.get("Responsibilities", []))
        flat_job["Skills"] = "; ".join(job.get("Skills", []))
        flat_job["Status"] = "Applied"
        flat_data.append(flat_job)

    new_df = pd.DataFrame(flat_data)

    # Load existing data if file exists
    if os.path.exists(filename):
        existing_df = pd.read_excel(filename)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)

        # 🔍 Remove duplicates based on Job_Title + Company
        combined_df.drop_duplicates(subset=["Job_Title", "Company"], keep="first", inplace=True)
    else:
        combined_df = new_df

    # Save updated data
    combined_df.to_excel(filename, index=False)
