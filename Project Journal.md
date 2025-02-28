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

### Caleb Ingram
#### AI Tools Used
*   ChatGPT 1o
#### Tasks and Features
*   Introduced visual UI into the simulation
*   Made dynamics of producers and consumers more realistic
#### Prompts and Outputs
*   Prompt #1: How about this: If a consumer's energy is running low (i.e. reaches some threshold) and there is no food in sight (with a reasonably shallow field of vision) then they must move? And once they eat a plant, the plant will disappear but will realistically regenerate (i.e. not immediately, but a seed will likely land and germinate). Please give the full code for that version of the program
*   Response #1 (paraphrased): Here is a single python file that addresses your concern... Here's a list of your concerns... [insert python] Here's why this python file addresses the aforementioned concerns. [insert summary of changes]
*   Prompt #2: I've pasted the results I'm getting. The consumer population explodes but they're still camping in one spot. A handful of spots end up each housing a great number of consumers: [insert results from running provided code]
*   Response #2: Here is why you're getting these results... Here's how you can fix it... [insert python]. Here's why this python file addresses the aforementioned concerns... [insert summary of changes]
*   Prompt #3: This is definitely more realistic, but certain consumers are still camping on a single spot without ever moving. Are you sure plants are being culled after the consumer lands on it?
*   Response #3: Here are your concerns: [insert understanding of problem statement]... [insert Python file]. Here's why this python file addresses the aforementioned problem statement... [insert summary of changes]
  
#### Reflections on AI Quality
*   ChatGPT seems to be very good at understanding how to achieve a particular outcome. The trick is making sure it understands the desired outcome and how that differs from the current state of things.
*   ChatGPT does a really good job of explaining code

#### AI Tool Integration
*   I continued to use the same chat within ChatGPT that I was using previously. It seemed to understand generic context but occasionally needs a reminder of what the ultimate goal is.

#### Lessons Learned
*   Human oversight is necessary to make progress. ChatGPT will always THINK it is solving the problem you provide because it doesn't always know WHY certain outputs are being created. For example, there was an incident wherein consumers (who were technically mobile) would camp out on a single producer because they could receive infinite energy and expend none. Therefore, they would reproduce and all the offspring would end up on that single square. I pointed this out to ChatGPT and prompted repeatedly for a fix; however, none of the code provided solved the problem. It responded as if it recognized the code that was causing the problematic behavior, but its solutions were ultimately insufficient. The problem was not solved until I pointed out in a single prompt that consumers can camp because producers aren't being culled AND that a producer should be culled once a consumer eats it. Only then did it provide me with code that solved the problem.

### Colton Woodruff

#### AI Tools Used
*   Github Copilot (with Gemini 2.0 Flash and Github Agent - Claude 3.5 Sonnet)

#### Tasks and Features
*   Implemented a nutrient system between producers and consumers using Github Agent. This involved creating a 2D array to represent nutrient levels, modifying the Producer and Consumer classes to interact with the nutrient environment, and implementing nutrient diffusion and decay.
*   Reviewed and understood a pull request submitted by Caleb using Github Copilot (on Github.com). This helped understand the changes made to the core simulation loop and how they impacted performance.
*   Using Github Agent, further addressed balancing of the simulation by updating organism parameters and start state. Further work is needed, but the balance is drastically improved.

#### Prompts and Outputs
*   **Idea Generation Prompts (Github Copilot with Gemini 2.0 Flash):** Used Gemini 2.0 Flash to brainstorm different approaches to implementing the nutrient system, focusing on balancing realism with computational efficiency. Examples included prompts like "What are some simple ways to add a feedback loop between producers and consumers?" and "How can I make producers and consumers interact with a shared nutrient resource?".
*   **Code Implementation Prompts (Github Agent - Claude 3.5 Sonnet):** Primarily used Github Agent for code implementation, specifically using the Claude 3.5 Sonnet model. To create the prompt, I first talked through the feature with Gemini 2.0 Flash, then asked it to create a detailed prompt to pass to Claude 3.5 Sonnet on Github Agent. The resulting prompt was perfect and gave Claude a specific set of guidelines to work with. The main prompt was: "Implement a nutrient system where producers consume nutrients from the environment, consumers release nutrients upon death, and nutrients diffuse to neighboring cells and decay over time." Gemini then provided a much longer prompt to pass to Github Agent, which then iteratively assessed the codebase, made changes to the Producer and Consumer classes, and added the necessary calls to the simulation loop. The agent prompted for approval after each iteration, allowing for fine-grained control. GPT-4o was also tested, but Claude 3.5 Sonnet provided better results.
*   **Pull Request Explanation (Github Copilot on Github.com):** Used Github Copilot on the Github website to break down and explain Caleb's pull request. Specific questions included: "Explain the changes in this pull request" and "Describe how each new addition interacts". The tool provided a clear summary of the changes and highlighted potential areas for optimization.

#### Reflections on AI Quality
*   Github Agent (Claude 3.5 Sonnet) proved surprisingly effective for code implementation, especially for the larger task of implementing the nutrient system. The iterative process and built-in testing helped ensure code quality and reduced the need for manual debugging. The ability to approve changes line by line provided fine-grained control and allowed for experimentation with different approaches. However, it sometimes required careful prompt engineering to guide the agent towards the desired outcome.
*   Github Copilot (on Github.com) provided a valuable overview of Caleb's pull request, but it sometimes lacked the depth of understanding that a manual code review would provide. It was most useful for quickly identifying the key changes and understanding their purpose.

#### AI Tool Integration
*   This sprint focused on leveraging Github Copilot's new features. Gemini 2.0 Flash was used for initial brainstorming and high-level design, while Github Agent (Claude 3.5 Sonnet) handled the bulk of the code implementation. Github Copilot (on Github.com) was used for code review and understanding. This workflow allowed for leveraging the strengths of each tool: Gemini 2.0 Flash for creative problem-solving, Github Agent (Claude 3.5 Sonnet) for efficient code generation, and Github Copilot (on Github.com) for quick code review.

#### Lessons Learned
*   **Github Agent (with Claude 3.5 Sonnet) is a Powerful Code Generation Tool:** The iterative approach and automated testing of Github Agent significantly improved code quality and reduced the need for manual debugging. However, it requires careful prompt engineering and close monitoring to ensure that it produces the desired results.
*   **Model Selection Matters for Different Tasks:** Gemini 2.0 Flash was more effective for brainstorming and high-level design, while Github Agent (Claude 3.5 Sonnet) was better suited for code implementation. Choosing the right model for the task at hand is crucial for maximizing productivity.
*   **AI-Assisted Code Review is a Useful Starting Point:** Using Github Copilot to explain pull requests can significantly speed up the code review process and provide a useful overview of the changes. However, it should not replace a thorough manual code review.
*   **Iterative Prompting is Key to Success with Github Agent:** Starting with a broad prompt and then iteratively refining it based on the agent's output is an effective strategy for achieving complex goals. This allows for guiding the agent towards the desired outcome while still leveraging its ability to automate code generation.

### Tycin Wood

#### AI Tools Used
*   Github Copilot (On github and while using VS Code)
*   ChatGPT 4o, o1 and o3-mini-high

#### Tasks and Features
*   Implement in-memory volatile storage of data to act as middleware between the simulation and the long-term non-volatile storage using ChatGPT.
*   Enhance the long-term storage capabilities to leave room for growth and implement changes to ensure smooth operation with in-memory storage using ChatGPT.
*   Create unit tests for new storage capabilities using ChatGPT
*   Integrate in-memory storage functions to replace original storage functionality using Copilot and ChatGPT.
*   Understand and merge pull requests from teammates using Copilot.

#### Prompts and Outputs
*   **I have a large simulation project and here’s the main simulation loop; how do I expand HDF5 storage to include the gameboard?:** The assistant outlined modifications to the HDF5Storage class to add datasets for the gameboard alongside organism data, discussed snapshot versus delta storage, and suggested a hybrid approach for improved retrieval speed.
*   **Can you write tests for all functionalities of the memory storage and its interactions with HDF5 storage?:** The assistant provided a comprehensive test suite covering full-state updates, piecewise updates, individual organism modifications, persistence (flush/load), mode switching, and various edge cases.
*   **I need a memory-resident store that supports interactive time travel and on-demand state updates; how can I structure it?:** The assistant explained how to design a single authoritative in‑memory store with update methods (both full-state and piecewise) and flush/load functions, which can then be integrated with HDF5 storage for persistence and replay.
*   **I want to separate organisms into consumers and add producers as a new data type; how should I update memory_storage.py and hdf5_storage.py?:** The assistant recommended splitting the state dictionary into separate keys for the board, producers, consumers, and debug logs. It provided new method outlines (e.g. update_state, update_producers, update_consumers) for the memory store and updated HDF5 saving/loading functions to handle the new schema.
*   **I’m getting errors because functions like update_organism_position and add_consumer are missing; how do I add these?:** The assistant suggested adding new methods to the MemoryResidentSimulationStore class (such as add_consumer, remove_consumer, update_consumer_position) and updating the tests to call these new methods so that consumer-specific updates work as intended.

#### Reflections on AI Quality
*   I used Copilot more this time around, both for reviewing pull requests from my teammates and in my IDE while trying to debug the smaller items that ChatGPT got too cumbersome for at a couple points. It really had a hard time with what indentation level to drop functions into and seem to be a little clueless about code I didn't highlight or was a ways from the cursor. The functions it made though were sound and I could see it being used to generate quick functions when you know how you want to transform inputs into what outputs consistently.
*   Continued to use ChatGPT since I had a lot of information plugged into it. I found the model choice to be important for the tasks I was doing, with o1 being able to do high quality analysis and handle large contexts while o3-mini-high got lost a few times on all the different items I was caring about which I don't suspect it was a context window issue since it seemed to overly focus on criteria I mentioned 10 prompts back but forget criteria I gave it 2 prompts back. With the main script, it was a lot more successful in having a working script everytime it gave me entire output while unit tests were a whole other story. I had it make me unit tests multiple times and with varying results. Some of the unit tests ended up having the problem with the test itself while others found actual bugs in the code. It seemed to be about a 50/50 split. It also had hilarious and severe problems counting. Asked it to make 9 more tests at 21 and I ended up with 26 then asked for 4 more and ended up with 25 and then making it count each test as it made it yielded 30. Most of the time. 

#### AI Tool Integration
*   This sprint I still leveraged ChatGPT a lot because I already have a project setup with it and needed continuity between the different pieces I have been working on and my teammates. I used a variety of models to figure out the differences between them and at one point ran out of prompts on what is considered the current best model so had to look elsewhere. I used copilot some within the github and VSCode but found that those were for very specific use cases and did not have much power as using a generalized LLM.

#### Lessons Learned
*   **Choose models carefully:** I found jumping around ChatGPTs models that I was getting subpar output for some aspects of development while others were fine on that same topic. I need to better learn the strengths and weaknesses of the models I am choosing instead of hopping around blindly.
*   **Sessions can get really bloated:** I had a single chat session, though not my only one, that ended up reaching ~77k tokens and had a wild ride with it. Keeping the AI focused, especially with the smaller models, was hard to keep on all criteria given. At certain points, the models would choose
*   **Disconnection doesn't feel great:** This week I feel more disconnected from my code than ever before and it doesn't feel great at all. I've found myself a couple times trying to debug a problem or trying to add a small feature after some advice from the AI and failing to find all the relevant pieces to update. While I am still trying to figure out how to be attached and understanding the code better, I think I will try to ask more questions about what the functionality is and where it fits into the larger picture.
*   **Doing puzzles with AI is hard:** Sometimes when I was asking for an update to specific code or function, I would get code that had an ambiguous place in the overall scheme of the project. It would give me some lines to add or parts of the script with items stripped out and expected me to follow along. I tried implementing the changes but inevitably would make some sort of mistake and have to scrap the changes and try again. I then would revert to asking it to just redo the entire script but a 500 line script is pretty heavy on token use. I found a good middleground where I would just ask for entire functions and tell me whether it is an updated function or new function and if it is a subordinate function to another function or class. It's not perfect, but it ends up working much better to be in managable chunks.

Final thoughts, it was a good week, feel like I am hitting my stride but also have some areas what I want to shore up, like using AI to better understand the scripts I am building and updating instead of just being glad it works. 


## Sprint 3: Optimization and Challenges

### Caleb Ingram

#### AI Tools Used
*   ChatGPT 4o/o1/o3-mini
*   Gemini-Code-Assist (Github Extension)

#### Tasks and Features
* Made the spawning methods more realistic for all creatures
* Advanced the food web by adding omnivores and carnivores. This brings about complexity wherein consumers that can be eaten (producers, omnivores) are inclined to run from those that can eat consumers (other omnivores + carnivores)


#### Prompts and Outputs
* Me: [after attaching the maximum 10 files that are most relevant for the code functionality] Can you explain to me how the current code works and how alife.py will execute? Several changes have been made by other people in my group, so I have attached a directory with the current 'main' branch in our repo.

Here's the structure of the directory:

AI CODER
--organisms
----__init__.py
----carnivore.py
----herbivore.py
----omnivore.py
----producer.py
--tests
----test_memory_storage.py
--utils
----constants.py
----toolbox.py
--alife.py
--hdf5_storage.py
--memory_storage.py
--requirements.txt

* ChatGPT's response:
Below is a high-level summary of how the code in the main branch is structured and how alife.py will execute, based on your described directory layout and file roles:

Directory & File Overview [gives high-level overview of each file]

How alife.py Typically Executes

Imports: On startup, alife.py imports items from utils (for constants, toolbox functions), from organisms (for the classes Carnivore, Herbivore, Omnivore, Producer), and from any storage modules (memory_storage.py, hdf5_storage.py), plus common libraries (random, pygame, etc.).
    Initialization: It sets up the main simulation parameters (e.g., grid width, initial population sizes) by reading from constants.py or by using local defaults.
    Create Populations: It spawns the initial sets of producers, herbivores, omnivores, and carnivores—likely generating random positions on the grid and random or defaulted gene sets for speed, vision, metabolism, etc.
    Main Loop: Inside the loop:
        Each organism’s update() method is called (for example, carnivore.update(...)) so it can move, eat, reproduce, or die.
        The environment might be updated if you track resources or seasons.
        The storage modules (memory_storage or hdf5_storage) could record snapshots of the population each turn, so you can load or replay states.
        If you have a Pygame window, alife.py updates the display by drawing the grid, the organisms, and any UI elements.
        The loop continues until you reach a maximum number of steps, or until all organisms die, or some other stopping condition.
    Logging & End: Each time step might log statistics—like population counts or average speeds—to a CSV or your memory/hdf5 storage, so you can analyze them later. When the run ends, alife.py closes everything gracefully and writes final data if needed.

Recent Changes
[summarizes changes implemented by team members]

Summary
[summarizes flow of alife.py]


* Me: Can you walk me through exactly how alife.py executes? If it calls another file, please explain thoroughly the relevant pieces of that file then return to the walkthrough of alife.py

*ChatGPT: 
Below is a step-by-step explanation of how alife.py generally executes, including where it calls into other files (like the ones in organisms/ or your storage utilities) and what parts of those files matter, then returning to what happens next in alife.py. The exact function or class names may vary slightly, but here’s the typical flow and references:

1. Initialization & Imports (Inside alife.py)

    Imports:
        [detailed description of all imports and underlying logic]

    Global or Constant Setup:
        [detailed description of constants and how they are introduced into the program]

2. Main Entry Point

Inside alife.py, you typically have:

if __name__ == "__main__":
    run_simulation_interactive()  # or main(), or whichever function starts everything

That means when you run python alife.py, Python looks here and calls your primary function (e.g., run_simulation_interactive()).

3. Creating the Environment & Populations

[explains initial state of simulation and hdf5 memory in detail]


4. The Main Simulation Loop
[detailed description of main simulation and where/how files other than alife.py are used]


5. Pygame & Final Steps

    If the simulation is interactive, alife.py sets up a Pygame window:
        The loop might call a function like draw_grid(screen, environment, producers, herbivores, carnivores, omnivores) to visualize the environment and each organism.
        Key or mouse events might be handled to pause, step backward/forward if a memory-based time travel is implemented.
    Once the loop finishes (reaching MAX_TIMESTEPS or no organisms left), alife.py closes the store and files, possibly writes a final message, and quits.

Overall Flow Summary

    alife.py starts, imports from organisms/ and utils/.
    It creates the environment (a 2D array or nutrient grid) and initializes populations by calling each organism’s constructor from their respective file.
    It runs a main loop, each iteration calling producer.update(...), herbivore.update(...), carnivore.update(...), omnivore.update(...). These methods are all defined in producer.py, herbivore.py, carnivore.py, and omnivore.py. They handle movement, eating, reproduction, or dying.
    After updating all species, alife.py calls update_environment(...) if you have resource diffusion or decay.
    If configured, it stores the new state in memory or HDF5 by calling methods from memory_storage.py or hdf5_storage.py.
    If interactive, it draws everything on the Pygame window and checks user input.
    The loop ends after a condition (time limit or all species extinct), and alife.py cleans up, closing any open files or logs.

With these steps, alife.py orchestrates the entire simulation: it calls code in the other files for organism logic, for storage and for utils. Once it’s done, the final data (like CSV logs or HDF5 snapshots) remains for analysis or replay.



#### Reflections on AI Quality
* Having an ongoing chat with ChatGPT has been extremely positive overall. While its memory is not perfect in that it does not always remember the goal, it is still an utter convenience.
* The code provided by ChatGPT is not remarkably advanced. Though it is a long program with much happening, little to nothing therein is particularly "clever".
* ChatGPT is really good at breaking down how code works!
* Github's Gemini-Code-Assist extension is GREAT. Although our codebase is long, it clearly summarizes any changes and recommends relevant improvements. This is hugely helpful BECAUSE there can be so much code to review. While this may bias the reviewer to only see what the AI sees, the feedback it does give is high quality. 

#### AI Tool Integration
* I have continued to use the same chat or two that I have been using all term. It works great for the most part. One big flaw is that when somebody else adds to the codebase, it takes work to get ChatGPT to put that in its memory.
* Github's Gemini-Code-Assist extension has proved very useful for code reviews. 

#### Lessons Learned
* Mr. GPT is not very skilled at incorporating changes that it did not introduce itself. Even giving ChatGPT the entire codebase, it tends to think that the latest version is the most recent one that it created.
   * To mitigate this problem, I ask the bot to explain in detail how the current codebase works. After priming the bot in that way, prompting it to change something or add a feature seems to yield fewer dropped details.

  
### Colton Woodruff

#### AI Tools Used
*   Github Copilot (with Gemini 2.0 Flash and Github Agent - Claude 3.5 Sonnet)
*   Github Copilot Chat (within VS Code, using Gemini 2.0 Flash)
*   Gemini-Code-Assist (Github Extension)

#### Tasks and Features
*   Implemented CI/CD pipelines using Github Actions. This involved creating three separate workflow YAML files:
    *   **Linting and Formatting (Ruff):**  A workflow that runs Ruff on pull requests to ensure code style consistency and identify potential errors.
    *   **Automated Testing (Pytest):** A workflow that executes Pytest unit tests on pull requests to verify code functionality.
    *   **Docker Build:** A workflow that builds a Docker image for the project, facilitating deployment and environment consistency.
*   Developed comprehensive unit tests for all project files using Pytest, guided by Github Copilot Agent.
*    Integrated the Gemini-Code-Assist extension into the Github repository for automated PR summarization and review.

#### Prompts and Outputs
*   **Research and Decision-Making Prompts (Github Copilot Chat with Gemini 2.0 Flash):**  Used Gemini 2.0 Flash within VS Code (via Github Copilot Chat) to research best practices for CI/CD, determine appropriate tools (Ruff, Pytest, Github Actions), and plan the structure of the workflows.  Examples include prompts like: "What are the best practices for setting up CI/CD for a Python project?", "How can I integrate Ruff and Pytest with Github Actions?", and "What's the recommended structure for a Dockerfile for this type of project?".
*   **Workflow Creation Prompts (Github Agent - Claude 3.5 Sonnet):**  Leveraged Github Agent (Claude 3.5 Sonnet) to generate the YAML files for the Github Actions workflows.  After discussing the workflow structure with Gemini 2.0 Flash in Copilot Chat, I transferred the conversation to Github Agent to generate the code.  Example initial prompts:  "Create a Github Actions workflow that runs Ruff on pull requests.", "Generate a workflow to run Pytest on pull requests.", and "Create a workflow to build a Docker image for the project." These were refined iteratively.
*   **Unit Test Generation Prompts (Github Agent - Claude 3.5 Sonnet):** Used Github Agent to create Pytest unit tests.  Instead of generating tests for the entire project at once, prompts were focused on individual files or groups of related functions within larger files. Example prompts include: "Generate Pytest unit tests for the `producer.py` file." or "Create tests for the `consume` and `reproduce` functions in `consumer.py`."  This granular approach yielded significantly better results.
*   **Gemini-Code-Assist Interaction (Github):** No explicit prompting was needed; the extension automatically generated a summary comment and a review comment on each pull request.  Used conversational prompts within the PR comments to ask clarifying questions, such as, "Can you elaborate on this suggested change?" and "What other potential issues might exist in this section of code?".

#### Reflections on AI Quality
*   **Github Agent (Claude 3.5 Sonnet) for Workflow Creation:**  Highly effective for generating well-structured YAML files.  The iterative nature of Github Agent allowed for fine-tuning and ensured the workflows were correctly configured.
*   **Github Agent (Claude 3.5 Sonnet) for Unit Test Generation:**  Performance was highly dependent on the scope of the request.  Generating tests for the entire project at once resulted in numerous errors and poor test quality.  Focusing on smaller units (files or groups of functions) drastically improved results and made it easier to guide the agent and intervene when necessary.
*   **Gemini-Code-Assist:** Provided accurate and useful summaries and reviews of pull requests. The automatic generation of these comments streamlined the review process. The ability to chat with the model within the PR comments facilitated deeper understanding and discussion.
*   **Github Copilot Chat (Gemini 2.0 Flash):** Excellent for research, planning, and understanding the broader context of CI/CD and testing.  Served as a valuable "sounding board" for ideas before moving to code generation.

#### AI Tool Integration
*   This sprint showcased a multi-stage workflow utilizing different AI tools for specific purposes.  Github Copilot Chat (with Gemini 2.0 Flash) was used for initial research, planning, and decision-making.  Github Agent (with Claude 3.5 Sonnet) handled the code generation for both Github Actions workflows and Pytest unit tests. The Gemini-Code-Assist extension provided automated PR reviews and summarization. The seamless integration of Chat into Agent within VS Code (transferring the conversation) was particularly beneficial.

#### Lessons Learned
*   **Granularity is Key for Effective AI-Assisted Test Generation:**  Attempting to generate tests for an entire project at once with Github Agent is overwhelming and leads to poor results.  A file-by-file or function-by-function approach is significantly more effective and manageable.
*   **Leverage AI for Research and Planning:** Github Copilot Chat (with Gemini 2.0 Flash) proved invaluable for researching best practices and making informed decisions about the CI/CD setup.
*   **Automated PR Summarization and Review is a Time-Saver:** The Gemini-Code-Assist extension significantly streamlined the pull request review process, providing valuable insights and suggestions automatically.
*   **Iterative Prompting with Focused Scope is Crucial:** Combining iterative refinement of prompts with a narrow focus (e.g., single file or function group) is essential for maximizing the effectiveness of Github Agent, particularly for complex tasks like test generation. The ability to move a conversation from Chat to Agent within the Github Copilot extension is highly effective.

### Tycin Wood

#### AI Tools Used
*   Github Copilot (on github)
*   Github Copilot Chat w/ Claude 3.7 Sonnet, GPT-4o, Gemini 2.0 flash, o1 (in VSCode)
*   ChatGPT 4o, 1o (web)

#### Tasks and Features
*   Worked through merge of expanding types of organisms with existing storage methodology and improved storage to be more dynamic and resilient to change.
*   Created a menu system to better navigate the simulation and give some polish
*   Implemented initial options menu to modify simulation start conditions
*   Generated initial statistics page with some stats to better visualize changes over time to the simulation.

#### Prompts and Outputs
*   **Comment:**  Keeping in the nature of this project, I asked Copilot for a summary of prompts it felt moved the project forward the most. Below is what it said.

During our chat, several crucial prompts significantly advanced the AI-Coder project. Here's a summary of the most impactful contributions:

1. Adding the Stats View Screen

You requested:
"I want to add another state that can be opened off of the simulation pause menu that is tentatively called stats. I don't want to do anything with it yet, just want the state made."

This created a fundamental new feature by:
*   Adding the STATS_VIEW state to app_states.py
*   Implementing input handling for the new state
*   Creating UI navigation between pause menu and stats view

2. Historical Population Graph

You requested:
"I want to display a historical graph of the simulation from beginning to current step on the stats page, whether the step is a live or replay step."

This dramatically improved data visualization by implementing:
*   SimulationGraphRenderer class for statistical visualization
*   Population history tracking in SimulationManager
*   Line graph visualization of population changes over time
*   Stats summary table beneath the graph

3. Graph Refinement

You requested:
"Please remove producers from the graph but leave it on the current stats section."

This optimized the visualization by:
*   Focusing the graph on animal populations only
*   Adding a legend to explain graph elements
*   Keeping producers in the statistics table for reference
*   Making the graph more readable and focused

4. Configurable Simulation Settings

You requested:
"I want to add option to the main menu options menu to modify the grid size and the number of starting organisms for each type. I also want to add an option to change the speed of the simulation."

This created a complete configuration system including:
*   ConfigManager for saving/loading user preferences
*   Interactive options menu UI
*   Editable settings for grid size, organism counts, and simulation speed
*   Persistent configuration between runs

5. Code Structure and Documentation

While not explicitly requested, we added:
*   Comprehensive docstrings to all major classes and methods
*   Cleaner code organization across modules
*   Clear separation of responsibilities between components
*   Improved input handling with dedicated state management

#### Reflections on AI Quality
*   **ChatGPT:**  I found this week it becoming unwieldy very quickly with how I was trying to work on the project with either prompts taking many minutes to complete or it went off the mark and was borderline useless
*   **Copilot in VSCode:** This was absolutely a massive game changer and I am genuinely impressed. This is less the actual quality of the AI itself but commentary on the quality of the integration. Some models had issues of the prompt breaking if it was running too long, but that appeared to be api throttling issues. 
*   **Copilot in Gihub:** It has worked fine so far, good for quick summaries. No further comments on it. 

#### AI Tool Integration
*   I finally integrated Copilot in VSCode into my workflow and it was seriously a game changer. I was trying to use a chatgpt project to manage the entire project and not only would it take an extremely long amount of time for ChatGPT to work through, it also lost the plot multiple times and just became unwieldy. Colton brought up his experience with Copilot so I gave it a shot and immediately I was able to push through with changes where it had direct access to the code and propose changes directly. I was able to get through merging two massive branches and got a ton of work done on the UI in the time I had the past week to work on the project. I told it I wanted to add options to a specific state in the simulation program and one round of modification and one bug fix it was working perfectly. I think this is the first time this project I have been absolutely blown away. 

#### Lessons Learned
*   **Don't expect nuance:** Trying to get the AI to implement a merge was the worst idea and experience I have had in this project. Due to not thinking ahead, the data structures I had implemented were not dynamic enough to handle changes to the main codebase. I branched a feature branch to work on fixing it and in the process of merging the expanded organism branch and the one that had the data structures, I had the bright idea to have the AI just do the merge from within VSCode using copilot. It fundamentally was not able to figure out which feature was needed to be kept and which ones were redundant so I ended up with classes in the main script but then also had the classes in the files that I had moved the classes to so I could break up the app to make it more modular. That leads to my next point.
*   **Details can make or break a prompt** I got trapped in a few loops where I would tell copilot very plainly what was wrong. Multiple times it made a single line change and told me it was fixed. I was probably not in the right mood but I really had issues not getting frustrated and kept giving short but pointed comments on what was still wrong. I finally got frustrated enough that I typed a very large block of how things should work and then it went through and was able to fix a bunch of little items that made the program work again. I ran into that same situation a few times but was much quicker to recognize I was getting too basic with my prompts. 
*   **Chose the right tool for the job** This already got mentioned last week but it carried over into this week quite a bit. Using Copilot in VSCode was a huge boost to my productivity and I came to realize that I needed to be deliberate with which models I chose when trying to make changes to the program. I really found that for example that o1 was much better at handling large changes that required either a lot of lines of code or a lot of files modified to get to a good end results but it is rate limited so only a small usage everyday and it can take a long time with how large the project is getting. On the other hand, GPT-4o could handle very minor changes but was very quick. Claude 3.7 would be able to handle the middle ground very well, but it was always a risk because there were times where it would hit prompt limit mid modification which left me either asking it to continue and hoping it picked up where it was at or discard the changes. 


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
