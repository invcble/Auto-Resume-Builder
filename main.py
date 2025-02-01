import openai, fitz, time
import os
import markdown
import subprocess
import tempfile
from dotenv import load_dotenv

load_dotenv()

def read_text(textname: str):
    with open(textname, 'r') as f:
        return f.read()

def read_pdf(pdfname: str):
    text = ""
    with fitz.open(pdfname) as f:
        for page in f:
            text += page.get_text()
        return text

# tokens per minute -> 6000
# time.sleep(59)

def resume_prompt_builder(master_resume_pdf, base_prompt_text, job_desc_text):
    master_resume = read_pdf(master_resume_pdf)
    base_prompt = read_text(base_prompt_text)
    job_desc = read_text(job_desc_text)

    final_prompt = f"""
    {base_prompt}

    <master_resume>
    {master_resume}
    </master_resume>

    <job_desc>
    {job_desc}
    </job_desc>
    """
    # final_prompt = base_prompt + '\n\n\n\n' + master_resume + '\n\n</master resume>\n\n' + '\n\n<job_desc>\n\n' + job_desc + '\n\n</job_desc>\n\n'
    return final_prompt

def generate_pdf(markdown_content, output_file, css_file=None):
    html_content = markdown.markdown(markdown_content, extensions=['extra', 'nl2br'])

    if css_file:
        with open(css_file, "r", encoding="utf-8") as f:
            css_content = f.read()
        styled_html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>{css_content}</style>
        </head>
        <body>{html_content}</body>
        </html>
        """
    else:
        styled_html = html_content
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as temp_html:
        temp_html.write(styled_html)
        temp_html_path = temp_html.name
    
    try:
        subprocess.run(["weasyprint.exe", temp_html_path, output_file], check=True)
    finally:
        os.remove(temp_html_path)

def call_LLM(final_prompt: str):
    # client = openai.Client(
    #     base_url="https://api.groq.com/openai/v1",
    #     api_key=os.getenv("GROQ_API_KEY")
    # )

    client = openai.OpenAI(
        base_url="https://api.together.xyz/v1",
        api_key=os.getenv("TOGETHER_API_KEY")
        
    )

    response = client.chat.completions.create(
        # model="deepseek-r1-distill-llama-70b",
        # model="deepseek-ai/DeepSeek-V3",
        model="deepseek-ai/DeepSeek-R1",
        messages=
            [
                {
                    "role": "user",
                    "content": final_prompt
                }
            ],
        temperature=0.7
    )

    content = response.choices[0].message.content
    # print(response.choices[0].message)
    print(f"Content: {content}")


if __name__ == "__main__":
    prompt = resume_prompt_builder('Imon_s_Resume_v10.pdf', 'prompt.txt', 'job_desc.txt')
    # call_LLM(prompt)

    with open('test.md', 'r', encoding='utf-8') as f:
        data = f.read()
    generate_pdf(data, "output.pdf", css_file="styles.css")