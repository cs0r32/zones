#---------------------------------------------------------------------------
# Claude V2 PROMPT
#---------------------------------------------------------------------------
def claude_prompt(context):
    prompt = f"""

Human: You are a market intelligence specialist. We want to generate a short summary based on the provided image description. It's very important that summary is concise within 75 words or less.

Here is the image description inside <imageDescription></imageDescription> XML tags that you need to process.

<imageDescription>
{context}
</imageDescription>

Please put your summary of the image description in <response></response> XML tags.

Assistant:
"""
    return prompt

#---------------------------------------------------------------------------
# Claude V2 PROMPT Graphs
#---------------------------------------------------------------------------
def claude_prompt_graph(context):
    prompt = f"""

Human: You are a market intelligence specialist. We want to generate a short summary of a graph based on provided graph description. It's very important that summary is concise within 75 words or less.

Here is the graph description inside <graphDescription></graphDescription> XML tags that you need to process.

<graphDescription>
{context}
</graphDescription>

Please put your summary of the graph in <response></response> XML tags.

Assistant:
"""
    return prompt

#---------------------------------------------------------------------------
# Claude V2 PROMPT for Graphs
#---------------------------------------------------------------------------
def claude_prompt_graphs_summarize(context):
    prompt = f"""

Human: You are a market intelligence specialist. We want to generate a short summary of a graph that is represented by the JSON data provided. It's very important that summary is concise within 50 words or less.

Here is the JSON data inside <graphData></graphData> XML tags that you need to process.

<graphData>
{context}
</graphData>

Please put your summary of the graph in <response></response> XML tags.

Assistant:
"""
    return prompt

#---------------------------------------------------------------------------
# Claude V2 PROMPT for Graphs
#---------------------------------------------------------------------------
def claude_prompt_graphs_interpret(context):
    prompt = f"""

Human: You are a market intelligence specialist. Interpret the JSON data that represents a chart.

Here is the JSON data inside <graphData></graphData> XML tags that you need to process.

<graphData>
{context}
</graphData>

Please put your summary of the graph in <response></response> XML tags.

Assistant:
"""
    return prompt

#---------------------------------------------------------------------------
# J2 PROMPT
#---------------------------------------------------------------------------
def j2_prompt(context):
    prompt = f"""

You are a market intelligence specialist. We want to generate a short summary based on the provided image description. It's very important that summary is concise within 75 words or less.

Here is the image description inside "" that you need to process.

"
{context}
"

"""
    return prompt


