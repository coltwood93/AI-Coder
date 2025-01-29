# AI Tool Documentation Journal

## Overall Project Summary

*   This project is a deep dive into using **AI tools to build our A-Life Challenge simulation**, with a big emphasis on **documenting how well AI helps us**.
*   Our **A-Life Challenge** is a simulation where we aim to create an artificial world with evolving life, driven by simple rules and energy. It'll be visual and interactive, with saving, loading, and tweaking features.
*   We're using AI tools like **ChatGPT and GitHub Copilot for absolutely everything**: planning, coding, debugging, and more.
*   We want to learn about **both the benefits and the drawbacks of using AI** for software development, and will record our experiences, good or bad.
*   The final report will include tips on how to use these tools better, and why the simulation may or may not be fully finished.
*   This journal is meant to track our prompts, AI outputs, and personal reflections on the tool's usefulness.
*   The main goal is to **document our journey and learn the best ways to use AI tools**, the project itself is secondary.

## Sprint 1: Initial Setup and Core Mechanics

### Caleb Ingram

#### AI Tools Used
*   List AI tools used
#### Tasks and Features
*   List of specific tasks completed in this sprint.
#### Prompts and Outputs
*   Document specific prompts used with AI tools and their corresponding outputs.
    *   Example Prompt: "Generate a Python function to..."
    *   Example Output: ```python
            #insert code output here
#### Reflections on AI Quality
*   Analyze the quality of the AI output, discussing its usefulness and areas for improvement.
#### AI Tool Integration
*   Discuss how the AI tools were integrated into your workflow for specific tasks in this sprint.
#### Lessons Learned
*  Describe any insights or lessons learned about working with AI tools during the sprint.

### Colton Woodruff

#### AI Tools Used
*   Google NotebookLM, Google Gemini, and Github Copilot
#### Tasks and Features
*   Implemented DEAP library for mutation and evolution tools
*   Reviewed initial build and adjusted parameter values to achieve stable population size
#### Prompts and Outputs
* **Project Planning Prompts (Google Gemini):**  To kick things off, I fed Gemini the raw project requirements from our canvas assignment, the descriptions of our projects,  and prompted it to generate a response to each section of the project plan template. This proved surprisingly effective for initial brainstorming and high-level planning. However, as I started to get further into the details of the project, I found that Gemini struggled to maintain context and keep track of all the different aspects of the plan. Gemini started ignoring requirements that I mentioned earlier in the chat. This led me to explore other tools that could handle more input.
* **Code Planning Prompts (NotebookLM):**  Once we had a start to the project plan, I turned to NotebookLM for more detailed planning.  By uploading multiple documents from Canvas, the project descriptions, and documentation for several python libraries as "sources," I was able to ask NotebookLM to strategize further, describe features, and even generate specific prompts to guide Copilot's code generation. This ability to maintain context across multiple documents was a game-changer. However, while NotebookLM excelled at understanding and integrating information, its code generation capabilities were somewhat limited. It doesn't seem to be able to put output in a codeblock, so requested code ends up with unfavorable formatting. This is where Copilot came in.
* **Code Generation Prompts (Github Copilot):**  With a clear understanding of the desired features, I used Copilot to generate actual code snippets. Leveraging its knowledge of our existing codebase, I'd provide prompts based on the feature descriptions from NotebookLM, and Copilot would often suggest surprisingly relevant code blocks. While Copilot was excellent at generating code, it sometimes lacked the broader context of the project and the design decisions made during the planning phase. This reinforced the value of using a combination of tools, each playing to its strengths.

#### Reflections on AI Quality
Each AI tool brought its own strengths and weaknesses to the table, which influenced how I integrated them into my workflow:

* **Google Gemini:**  Gemini's conversational style was fantastic for initial brainstorming and iterating on the project plan. However, it struggled to maintain context as we moved into more detailed aspects of the project, which is why I transitioned to NotebookLM for code planning.
* **NotebookLM:**  NotebookLM truly shone in its ability to understand and integrate information from multiple sources. Its context awareness was invaluable for generating text that aligned with our project goals.  However, its code generation capabilities were not as robust as Copilot's, leading me to use it primarily for planning and prompt engineering.
* **Github Copilot:**  Copilot proved to be the most efficient tool for generating code, especially with its tight integration with VS Code and understanding of our codebase.  However, it sometimes lacked the broader project context that NotebookLM provided, which is why I found it valuable to use NotebookLM to generate prompts for Copilot.

#### AI Tool Integration
My workflow evolved organically as I discovered the strengths and weaknesses of each AI tool:

* **Workflow:**  I started with Gemini for initial project planning, then transitioned to NotebookLM for detailed feature design and prompt generation, and finally relied on Copilot for the actual code generation within our IDE. This multi-stage approach allowed me to leverage the best of each tool.
* **Task Allocation:**  This workflow highlighted the importance of selecting the right tool for the right task. Gemini excelled at high-level planning, NotebookLM at context-aware text generation, and Copilot at code generation.

#### Lessons Learned
This first sprint provided valuable insights into several of the popular AI tools I commonly hear about:

* **Context is King:**  Maintaining context throughout the AI interaction is paramount. The more context the AI has, the more relevant and accurate its outputs become. This was particularly evident when I switched from Gemini to NotebookLM for code planning.
* **Combine Multiple LLMs:**  Different AI tools have different strengths. Combining them strategically can unlock a new level of productivity and creativity. Using NotebookLM to generate prompts for Copilot was a prime example of this synergy.
* **Prompt Engineering Matters:**  Crafting effective prompts is imperative.  Learning how to communicate effectively with each AI tool is crucial for getting the desired results. Being direct, specific, and ignoring pleasantries results in more effective responses.
* **Human Oversight is Essential:**  While AI tools are powerful, they are not infallible.  Human oversight and critical evaluation remain essential to ensure quality and alignment with project goals. The tools I used hallucinated a few times and sometimes reprompting or asking "are you sure" is all it takes to get back on track.

This sprint gave me a good initial understanding of some strategies I can employ. I'm interested in trying another tool or two for the second sprint so I can really get a feel for the field. They each have their strengths and weaknesses, and using them is the quickest way to discover them.

### Tycin Wood

#### AI Tools Used
*   List AI tools used
#### Tasks and Features
*   List of specific tasks completed in this sprint.
#### Prompts and Outputs
*   Document specific prompts used with AI tools and their corresponding outputs.
    *   Example Prompt: "Analyze data output using Pandas..."
    *   Example Output: ```python
            #insert code output here
#### Reflections on AI Quality
*   Analyze the quality of the AI output, discussing its usefulness and areas for improvement.
#### AI Tool Integration
*   Discuss how the AI tools were integrated into your workflow for specific tasks in this sprint.
#### Lessons Learned
*  Describe any insights or lessons learned about working with AI tools during the sprint.

## Sprint 2: Simulation and Visual Elements
*(Example Sprint Title - this should be updated for each sprint)*

### Caleb Ingram
... *(repeat section from Sprint 1)*

### Colton Woodruff
... *(repeat section from Sprint 1)*

### Tycin Wood
... *(repeat section from Sprint 1)*


## Sprint 3: Optimization and Challenges
*(Example Sprint Title - this should be updated for each sprint)*

### Caleb Ingram
... *(repeat section from Sprint 1)*

### Colton Woodruff
... *(repeat section from Sprint 1)*

### Tycin Wood
... *(repeat section from Sprint 1)*

## Project Archive - Final

### Caleb Ingram
... *(repeat section from Sprint 1)*

### Colton Woodruff
... *(repeat section from Sprint 1)*

### Tycin Wood
... *(repeat section from Sprint 1)*

## Final Reflection

*   **Best Practices:**
    *   List key best practices for using AI tools.
*   **Limitations and Pitfalls:**
    *   Document limitations of the AI tools and strategies for overcoming them.
*   **Future Directions:**
    *   Ideas for how to use the project and AI tools in the future.
