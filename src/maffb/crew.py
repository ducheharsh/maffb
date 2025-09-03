from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from .tools.rss_feed_extractor_tool import RssFeedExtractorTool
from .tools.emailer_tool import EmailerTool
from .tools.markdown_formatter_tool import MarkdownFormatterTool
from .tools.readme_updater_tool import ReadmeUpdaterTool

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class Maffb():
    """Maffb crew for collecting, analyzing, and summarizing blog content from RSS feeds"""

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def blogs_collector(self) -> Agent:
        return Agent(
            config=self.agents_config['blogs_collector'],
            tools=[RssFeedExtractorTool()],
            verbose=True
        )

    @agent
    def blogs_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['blogs_analyst'],
            verbose=True
        )

    @agent
    def blogs_summarizer(self) -> Agent:
        return Agent(
            config=self.agents_config['blogs_summarizer'],
            verbose=True,   
            tools=[MarkdownFormatterTool()]
        )

    @agent
    def readme_updater(self) -> Agent:
        return Agent(
            config=self.agents_config['readme_updater'],
            tools=[ReadmeUpdaterTool(), MarkdownFormatterTool()],
            verbose=True
        )

    @agent
    def blogs_summary_emailer(self) -> Agent:
        return Agent(
            config=self.agents_config['blogs_summary_emailer'],
            tools=[EmailerTool()],
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def blogs_collection_task(self) -> Task:
        return Task(
            config=self.tasks_config['blogs_collection_task'],
        )

    @task
    def blogs_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['blogs_analysis_task'],
        )

    @task
    def blogs_summarization_task(self) -> Task:
        return Task(
            config=self.tasks_config['blogs_summarization_task'],
            output_file='blog_summaries.md'
        )

    @task
    def blogs_summary_emailing_task(self) -> Task:
        return Task(
            config=self.tasks_config['blogs_summary_emailing_task'],
            output_file='blog_summaries.md'
        )

    @task
    def readme_update_task(self) -> Task:
        return Task(
            config=self.tasks_config['readme_update_task'],
            output_file='README.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Maffb crew for blog content processing"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
