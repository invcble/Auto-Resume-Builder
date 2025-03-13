import os
import shutil
from datetime import datetime
import subprocess
from together import Together
from win11toast import toast
from dotenv import load_dotenv

load_dotenv()


def read_file(filename: str):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()


def resume_prompt_builder(main_tex, base_prompt_text, job_desc_text):
    master_resume = read_file(main_tex).split("%%%%%%  RESUME STARTS HERE  %%%%%%")[1]
    base_prompt = read_file(base_prompt_text)
    job_desc = read_file(job_desc_text)

    final_prompt = f"""
    <master_resume>
    {master_resume}
    </master_resume>

    <job_desc>
    {job_desc}
    </job_desc>

    
    {base_prompt}
    """
    return final_prompt


def generate_pdf(latex_content, tex_file):
    print('generating PDF...')

    with open(tex_file, "w", encoding="utf-8") as f:
        f.write(latex_content)

    with open(os.devnull, 'w') as devnull:
        subprocess.run(["pdflatex", tex_file], stdout=devnull, stderr=devnull, check=True)

    for ext in [".log", ".aux", ".out"]:
        aux_file = tex_file.replace(".tex", ext)
        if os.path.exists(aux_file):
            os.remove(aux_file)
    
    print('PDF generated.')
    toast('Resume Generated 🤖')


def call_LLM(final_prompt: str):
    print('calling LLM...')

    client = Together()

    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-R1",
        messages=
            [
                {
                    "role": "user",
                    "content": final_prompt
                }
            ],
        temperature=0.6,
        top_p=0.4,
        top_k=20,
        max_tokens=4096,
        repetition_penalty=1,
    )

    content = response.choices[0].message.content

    print(f"COT: {content.split('</think>')[0]}")
    return content.split("</think>")[1]


if __name__ == "__main__":
    prompt = resume_prompt_builder('main.tex', 'prompt.txt', 'job_desc.txt')
    latex_styling = read_file('main.tex').split("%%%%%%  RESUME STARTS HERE  %%%%%%")[0]
    # generated_resume = read_file('main.tex').split("%%%%%%  RESUME STARTS HERE  %%%%%%")[1]
    
    # typical token count 7778 in | 2793 out
    generated_resume = call_LLM(prompt)
    generate_pdf(latex_styling + generated_resume, "Resume_ImonBera.tex")

    applications_dir = "applications"
    os.makedirs(applications_dir, exist_ok=True)

    company_job_role = input("Enter the company and job role: ")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

    app_folder = os.path.join(applications_dir, f"{company_job_role} - {timestamp}")
    os.makedirs(app_folder, exist_ok=True)

    shutil.copy("job_desc.txt", os.path.join(app_folder, "job_desc.txt"))
    shutil.move("Resume_ImonBera.tex", os.path.join(app_folder, "Resume_ImonBera.tex"))
    print(f"Application saved in: {app_folder}")
