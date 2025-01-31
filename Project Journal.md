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
*   ChatGPT o1, "DALL-E", "Whimsical Diagrams"
#### Tasks and Features
*   Created 1st functional version of evolutionary simulation using Python, involving several proof-of-concept parameters (e.g. a single-gene genome, one type of organism)
*   Drafted procedure for advancing evolutionary engine
*   Contributed to Project Plan
#### Prompts and Outputs
*   Document specific prompts used with AI tools and their corresponding outputs.
    *   Prompt (after asking it to complete a development plan): "Alright, I want you to pretend you are an expert in mathematical models (focus in population dynamics and evolutionary algorithms) and biology who is also an excellent coder (your main language is Python but you're familiar with other languages enough to accomplish what you need to). I need today to get all the way to the very simple simulation mentioned in step 4. Give me whatever completed files would be necessary to start the simulation (e.g. a .py file) and record the results (e.g. a .csv file)
ChatGPT"
    *   Output (summarized): "Below is a Python example that implements Step 4 and a simple CSV output with population data over time. [Insert Python file here]. Here's how it works [insert explanation]. Here's what's next: [insert suggestions]. In summary: [insert summary]."
    *   Next Prompt: The first line in the csv file is for time step = 0. However, this is after one time stamp. Can you modify this to make sure the population at time step = 0 is the INITIAL_POPULATION, the population at time step = 1 is after one real time step in the simulation, etc.?
    *   Output (summarized): "Below is a revised version of the minimal simulation that logs the population at t = 0 then logs again at t = 1 after the first update, and so on. This ensures that the CSV’s first data row corresponds to the initial population: [insert corrected python code]. Here's how it works: [insert explanation]. In summary: [insert summary]."
#### Reflections on AI Quality
*   The AI-generated diagrams were not helpful at all. I fed ChatGPT our nearly-completed project plan and asked it to generate the relevant visuals (System Architecture Diagram + Simulation Visual Markup). Trying to generate the diagram, it returned several diagrams that apparently did not incorporate the logic of the program. Trying to generate the visual markup, it eventually was able to generate a visual of an evolutionary simulation app, but it had many unnecessary buttons and dials along with nonsensical words. In summary, trying to get the visual generators to understand logic was painstaking and ultimately unsuccessful.
#### AI Tool Integration
*   I prompted ChatGPT to take on the role of a multidisciplinary expert -- a master of mathematical modeling, biology, and coding. With this context, I fed it the project requirements of the A-Life Challenge and asked for sequential steps on how to develop this project starting from square 1. With that layout, I progressively asked it to complete each step and fed it feedback each time. This workflow was very effective to a point. Once the simulation became advanced enough, it became hard to progress it further; the python code returned by ChatGPT would result in simulations being very sensitive to the initial parameters. Almost every single simulation would end with one or more populations dying off every time.
*   To give feedback to chatgpt, I would feed it the results of the simulation (directly from VSCode log) and any observations I had about the results. It would often validate my observations -- sometimes it would say something to the effect of "You're right! Here's what needs to change to make the simulation more realistic..." or "You're right! Here's why those results are to-be-expected...". This is problematic because I want the simulation to be functioning somewhat realistically (insofar as its current complexity allows) before trying to add features and complexity.


#### Lessons Learned
*  ChatGPT needs to get better at saying no. It is almost always encouraging, even when ideas are not good. At its most benign, this is annoying. At its worst, this is destructive and time-wasting.
*  Visuals that need to be specific are probably better-off generated by photoshop. Photoshop's AI is almost certainly better for this use case than DALL-E/Sora/Whimsical Diagrams, but I do not have access to this.
*  The volume of output that ChatGPT gives is excessive. It needs to be reigned in and re-focused on what is important. Even still, it will always provide an explanation and a summary unless prompted specifically not to.
*  Giving ChatGPT a role to play THEN giving it a task can add richness to its output. For example, "Here are instructions for the document I need to be completed..." can be augmented to something like: "Pretend you're an allstar leader of a computer science team creating a project plan. Here are your instructions...".
*  I found value in keeping everything in one chat; it was able to reference messages from the beginning of the conversation if I was specific enough. Going forward, I will continue to use ChatGPT; however, I will see what other tools can be used to enhance the simulation.
*  It will aim for EXACTLY what you suggest. For example, if you say "store results in a .csv file or something like that", it might go out of its way to use a .csv file.

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
*   ChatGPT o1/4o, DeepSeek R1 (cloud and quantized), copilot
#### Tasks and Features
*   Plan out data model with focus on modularity and ease of use in simulation loop
*   Built initial long term storage solution to retrieve/store step data using HDF5
#### Prompts and Outputs
*   Prompts showing it being agreeable to two different methods of doing something. 
    *   Prompt 1: "Would a good solution to avoid having to worry about variable length species names would be to store the species of each organism as an id number and have a reference file that species can be tied to if needed?"
    *   Output 1: "Solution: Using Species IDs Instead of Variable-Length Names
    Yes! Storing species as numerical IDs instead of strings is an excellent way to avoid variable-length issues and improve storage efficiency in HDF5. You can:
        *   Assign each species a unique ID.
        *   Store only the species ID per organism (instead of storing full names).
        *   Maintain a separate reference mapping (species_map.json or species_map.h5) to tie IDs back to species names when needed."
    *   Prompt 2: "Should I get rid of the species map and just store variable length strings to simplify?"
    *   Output 2: "Should You Get Rid of the Species Map and Store Variable-Length Strings Instead?
    Yes, storing variable-length species names directly in HDF5 instead of mapping them to IDs will simplify the code and avoid the need to manage species mappings separately. However, it comes with trade-offs in terms of storage efficiency and performance."
*   Internal monologue snippet from deepseek
    *   Prompt 1: "I have an artifical life simulation my team is working on. I have been tasked with the data storage and data visualization, this is my main task this sprint. Give me some advice

       Set up data analysis tools (Pandas, NumPy) and storage systems (HDF5)."
    *   Thought 1: "Okay, so the user is working on an artificial life simulation and is responsible for data storage and visualization this sprint. They mentioned setting up Pandas, NumPy, and HDF5. Let me break down how to approach this.
        
        First, data storage. HDF5 is a good choice because it's efficient for large datasets. I should explain why HDF5 is beneficial here—like handling large, complex data with compression. Maybe suggest using h5py or PyTables in Python. They might need to structure their data properly. Organizing datasets by timestep, agents, or environment layers makes sense. Also, chunking and compression settings are important for performance. Metadata is crucial for context, so they should include parameters like simulation configs, timestamps, etc.
    
        Version control for HDF5 files might be a consideration. They might need to track changes over time. Maybe mention backups and cloud storage for safety.

        Next, data analysis with Pandas and NumPy. They'll need to read data efficiently from HDF5. Using Pandas DataFrames could help, especially with time-series data. For example, loading agent data into DataFrames for analysis. NumPy is good for numerical computations. Maybe suggest preprocessing steps like normalization or handling missing data. They might also need to compute stats like survival rates or movement patterns. Time-series analysis would be important, like aggregating data over time intervals.

        For visualization, Matplotlib and Seaborn are standard. Plotly or Bokeh could add interactivity, which is useful for exploring complex data. They should visualize agent behaviors, population trends, environmental changes, and spatial data. Maybe using heatmaps for density. Dashboards with multiple plots can give a comprehensive view. Automating visualizations through scripts would save time, especially with scheduled reports.

        Integration and automation are key. They should create data pipelines to automate the process from storage to analysis to visualization. Unit tests for data integrity would prevent errors. Logging helps track the pipeline's status. Documentation is important for team collaboration—explaining the data schema and how to use the tools.

        Collaboration tips: Maybe use shared cloud storage for HDF5 files. Jupyter notebooks for exploratory analysis. CI/CD pipelines to automate testing and deployment. Performance optimization like parallel processing with Dask if data is too big. Caching intermediate results to speed things up.

        Wait, did I miss anything? Maybe security aspects of data storage? Or scalability issues if the simulation grows? Also, considering future-proofing the data format. Maybe suggest checking the HDF5 structure for flexibility as the simulation evolves. Also, error handling in data pipelines to catch issues early.

        Yes, that covers storage, analysis, visualization, automation, collaboration, and optimization. Make sure the advice is practical and step-by-step, aligning with their sprint goals. Keep it structured so they can follow each part without getting overwhelmed."

* Key prompt to ChatGPT to get it to stop trying to build out fields inside of the function instead of defining it on initialization of the object.
    *   Prompt 1: "Can I define all the fields on initialization so I can make it easier to expand instead of having to define every field saved as code?"
    *   Output 1: "Defining All Fields on Initialization for Flexibility

        Yes! You can dynamically define fields on initialization instead of hardcoding each dataset manually. This makes it easier to expand, so you don't need to modify the code when adding new organism attributes.
            🔹 Solution: Use a Dictionary to Define Fields Dynamically

        Instead of explicitly listing attributes (positions, energy, speed, etc.), use a dictionary to define all fields.
        
        1️⃣ Define a Flexible Schema

        Modify the HDF5Storage class to accept a schema dictionary when initializing.
        ``` Python
        import h5py
        import numpy as np
        import json
        import time

        class HDF5Storage:
            def __init__(self, filename=f"simulation_data.{int(time.time())}.h5"):
                self.filename = filename

                # Define all organism attributes dynamically
                self.fields = {
                    "positions": lambda org: [org.x, org.y],  # List [x, y]
                    "energy": lambda org: org.energy,         # Float
                    "speed": lambda org: org.speed,           # Int
                    "generation": lambda org: org.generation, # Int
                    # Add more fields here when needed!
                }

            def save_population(self, timestep, organisms, species_map):
                """Stores organisms' structured data dynamically based on defined fields."""
                with h5py.File(self.filename, "a") as f:
                    group = f.require_group(f"timestep_{timestep}")

                    # Dynamically extract and store data for all defined fields
                    for field_name, extractor in self.fields.items():
                        data = np.array([extractor(org) for org in organisms])
                        group.create_dataset(field_name, data=data, compression="gzip")

                    # Store species as integer IDs
                    species_ids = np.array([species_map[org.species] for org in organisms], dtype=np.int8)
                    group.create_dataset("species_ids", data=species_ids, compression="gzip")

                    # Store species mapping inside HDF5
                    species_json = json.dumps(species_map)
                    dt = h5py.string_dtype(encoding="utf-8")
                    group.create_dataset("species_dict", data=np.array(species_json, dtype=dt))
        ```"

#### Reflections on AI Quality
*   Quality was fine in my opinion, starting out my prompts are really vague and steer overtime but it gives you so much information up front using that methodology it is really easy to get lost in the detail. When I started to get it generating functions for me, I was able to take an iterative approach where I changed little things here or there. Some prompts ended up getting output that was outdated but required a correction to fix it. Little by little I got what I think is some good quality code but then I didn't even know if it would work. My plan was to create something modular and easy to integrate but I didn't want to take over the integration in the main sim loop so I had it create a test script that demonstrated it working perfectly for what I was looking for. Overall, with some "work" I put in I got quality I am okay with.
#### AI Tool Integration
*   This sprint being the beginning was a lot of planning and asking questions of what tools to use, how to organize our data. I appreciated how straightforward and streamlines the process of using it is. I liked using DeepSeek because of the output of the LLM's "internal monologue" to figure out how it is "thinking" out what you want from it. While I didn't use it much this sprint, I appreciate Copilot is tied directly into github so you can query it on matters related to your repo and it can give you a solid answer. I used it to ask about a diff on a pull request and it summarized the changes while also giving me assurances it couldn't see any failures.
#### Lessons Learned
*  **Plentiful Rabbit Holes** I've noticed it is really easy to give the AI a thought exercise and have it to try to turn it into a solution no matter how silly that idea might be. Not only will it try to solve the problem with that, but it will influence that entire session until you remember to tell it to forget it. I need to not get caught up in it being so agreeable.
*  **Maybe too greybeard sometimes** Trying to look up specific technologies with a long history will have old options or functions find their way creeping into modern solutions given by the LLM. You have to vet the output to make sure it is in line with current functionality or standards.
*  **Skills atrophy** Not a lesson learned necessarily but something I have been worried about in the past and had confirmed as I have been using LLMs more. There is a fine line between not falling behind peers from not using AI and having friction in your project to help keep your mind thinking and not offloading everything. Something I want to explore more. 
*  **Little bit of nuance** Most times without a little bit of nuance to the prompt, it felt like taking a sledgehammer to the task instead of gracefully working on it. The more detail I gave it the more it was able to provide me an answer that fit what I needed but still continued to need nudges to address nuances it didn't quite understand.

Final thoughts, I think this was a good warm-up sprint. I didn't get as much done as I wanted this week with work and family pulling me in a million directions but I got a good start and plan on putting in a lot more time in this next sprint.


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
