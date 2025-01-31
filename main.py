import openai, fitz, time

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

    final_prompt = base_prompt + '\n\n<master resume>\n\n' + master_resume + '\n\n</master resume>\n\n' + '\n\n<job_desc>\n\n' + job_desc + '\n\n</job_desc>\n\n'
    return final_prompt


def call_LLM(final_prompt: str):
    client = openai.Client(
        base_url="https://api.groq.com/openai/v1",
        api_key=""
    )


    {
        "role": "user",
        "content": final_prompt
    }

    response = client.chat.completions.create(
        model="deepseek-r1-distill-llama-70b",
        messages=[{"role": "user", "content": "hi, who are you. reply to me in markdown"}],
        temperature=0.7
    )

    content = response.choices[0].message.content
    # print(response.choices[0].message)
    print(f"Content: {content}")



    

print(read_pdf('Imon_s_Resume_v10.pdf'))

