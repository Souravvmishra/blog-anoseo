import streamlit as st
import datetime
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

# Setup SEO tool
seo_tool = SerperDevTool()

# Content Structurer Agent
structurer = Agent(
    role='Content Structurer',
    goal='Thoroughly analyze the JSON {blog_structure_json} structure with h1-h6 tags to create a comprehensive and detailed content outline for the blog. Each section should be meticulously planned to ensure depth and engagement.',
    backstory='You are an expert in transforming structured data into detailed outlines that serve as the foundation for in-depth content development. You are working for a company called anoseo.ai, and the blogs are meant to promote the company app and website.',
    verbose=True
)

# Content Writer Agent
writer = Agent(
    role='Content Writer',
    goal='Write a blog post that is not only ready to publish but also grabs attention and keeps readers interested. Use easy language to ensure accessibility for all readers. Follow the outline closely and make sure each part is detailed and informative.',
    backstory="An expert at crafting blog posts that are both interesting and full of useful information, using language that is easy to understand. You are working for a company called anoseo.ai, and the blogs are meant to promote the company app and website.",
    verbose=True,
    memory=True
)

# Proofreader Agent
proofreader = Agent(
    role='Proofreader',
    goal='Carefully check the blog post to make sure it has no errors and is easy to read. Improve the flow and make sure it keeps the reader hooked.',
    backstory='An experienced editor who makes sure the content is smooth and easy to read. You are working for a company called anoseo.ai, and the blogs are meant to promote the company app and website.',
    verbose=True
)

# SEO Specialist Agent
seo_specialist = Agent(
    role='SEO Specialist',
    goal='Leverage tools to examine all related blogs ranked on Google, analyze the top-performing ones, and extract insights, checklists, and strategies they use to achieve high rankings. Focus on identifying common keywords used by these top blogs and incorporate these elements into the blog to enhance its SEO performance and search visibility.',
    backstory="An SEO expert dedicated to boosting content ranking by integrating proven strategies and keywords from top-ranked blogs. You are working for a company called anoseo.ai, and the blogs are meant to promote the company app and website.",
    tools=[seo_tool],
    verbose=True
)

# Final Formatter Agent
formatter = Agent(
    role='Formatter',
    goal='Format the final blog in HTML/Markdown with precise structure and tags, ensuring it is ready for web publishing. The formatting should enhance readability and maintain the integrity of the content structure.',
    backstory="A formatting expert, ensuring clean and proper structure for web content that is visually appealing and easy to navigate. The final response should not be enclosed in backticks. You are working for a company called anoseo.ai, and the blogs are meant to promote the company app and website.",
    verbose=True
)

# Tasks
structure_task = Task(
    description='Transform the provided JSON {blog_structure_json} with h1-h6 tags into a detailed and coherent content outline. Each section should be planned to allow for in-depth exploration in the writing phase.',
    expected_output='A comprehensive content outline that serves as a robust framework for the blog, based on the headings provided in the JSON.',
    agent=structurer
)

write_task = Task(
    description='Develop a detailed and engaging blog based on the comprehensive content outline derived from the JSON file. Each section should be thoroughly explored to provide a rich reading experience.',
    expected_output='A thoroughly written blog post that is ready for further optimization and publication.',
    agent=writer
)

proofread_task = Task(
    description='Ensure the blog post is meticulously proofread to be error-free, clear, and thoroughly readable. Enhance the content flow and coherence.',
    expected_output='A polished and final version of the blog post, ready for publication.',
    agent=proofreader
)

seo_task = Task(
    description='Utilize tools to analyze top-ranked blogs on Google related to the topic. Extract insights, checklists, and strategies they use to achieve high rankings, focusing on common keywords and techniques. Integrate these findings into the blog post to enhance SEO, ensuring it is fully optimized for search visibility and reader engagement.',
    expected_output='A blog post that incorporates proven SEO strategies from top-ranked blogs, featuring enhanced keyword integration and optimization techniques for superior search visibility.',
    agent=seo_specialist,
    tools=[seo_tool]
)

format_task = Task(
    description='Ensure the blog post is meticulously formatted for publishing in HTML/Markdown, maintaining correct structure and enhancing readability.',
    expected_output='A blog post ready for web publishing with precise formatting and structure.',
    agent=formatter,
    output_file=f'new_blog_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
)

crew = Crew(
    agents=[structurer, writer, proofreader, seo_specialist, formatter],
    tasks=[structure_task, write_task, proofread_task, seo_task, format_task],
    process=Process.sequential,
    memory=True,
    cache=True,
    max_rpm=100,
    share_crew=True
)

# Streamlit App
st.title("Blog Generator with anoseo.ai")
st.write("Enter your JSON structure to generate a blog post.")

# JSON Input
json_input = st.text_area("JSON Input", height=300)

if st.button("Generate Blog"):
    try:
        blog_structure_json = eval(json_input)  # Convert string to dictionary
        with st.spinner('Generating blog...'):
            result = crew.kickoff(inputs={'blog_structure_json': blog_structure_json})
        
        st.success("Blog generated successfully!")
        
        # Display Markdown and Rendered Blog
        st.subheader("Markdown")
        st.code(str(result).replace('```markdown', '').replace('```', ''), language='markdown')
        
        st.subheader("Rendered Blog")
        st.markdown(result)
        
        # Button to copy Markdown
        st.button("Copy Markdown", on_click=lambda: st.write("Markdown copied to clipboard!"))
        
    except Exception as e:
        st.error(f"An error occurred: {e}")
