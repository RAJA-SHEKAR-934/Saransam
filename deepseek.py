import ollama

# Function to refine the BART summary with DeepSeek R1 model based on purpose
def refine_summary_with_ollama(summary_text, purpose="default"):
    prompts = {
        "note-taking": "Convert this summary into bullet points suitable for note-taking. Use clear, concise language and highlight important concepts, definitions, and cause-effect relationships:",
        "research-summary": "Rewrite the following summary into a structured research summary. Emphasize the objective, methodology, key findings, and conclusion. Use a formal academic tone:",
        "legal-summary": "Rewrite the summary into a clear and concise legal summary suitable for notary or legal documentation. Maintain neutrality and legal tone while simplifying the content for easier understanding:",
        "presentation-outline": "Transform this summary into a structured presentation outline with bullet points for slides. Start with an introduction, then cover the main points, and end with a conclusion or call to action:",
        "email-draft": "Rewrite this content as a professional email draft. Ensure a clear subject, concise body, and actionable tone. Include a polite greeting and closing:",
        "meeting-recap": "Summarize this as a meeting recap. Use bullet points to outline key discussions, decisions made, and action items. Keep it clear and concise:",
        "linkedin-post": "Convert this into a compelling LinkedIn post. Use a friendly and professional tone, a strong hook at the beginning, and a call to action at the end. Keep it engaging and readable:",
        "video-script": "Rewrite the summary into a conversational script suitable for a YouTube video. Include hooks, transitions, and clear explanations. Keep the tone friendly and informative:",
        "podcast-notes": "Reformat this summary into podcast show notes. Include an episode title, a short description, key points discussed, and timestamps if available:",
        "blog-draft": "Turn this summary into a well-structured blog post draft. Include a title, introduction, subheadings, and conclusion. Maintain a casual yet informative tone:",
        "default": "Improve and polish the following summary:"
    }

    prompt = prompts.get(purpose, prompts["default"])
    full_prompt = f"{prompt}\n\n{summary_text}"

    # Sending request to Ollama to use the deepseek-r1:1.5b model
    response = ollama.chat(model='deepseek-r1:1.5b', messages=[
        { "role": "user", "content": full_prompt }
    ])

    # Extracting the response content
    refined_summary = response['message']['content']
    return refined_summary
