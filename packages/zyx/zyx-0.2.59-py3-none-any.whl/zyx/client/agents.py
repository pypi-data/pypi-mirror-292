from typing import List, Dict, Any, Optional, Union
from ..types import (
    TaskIntent,
    TaskDelegation,
    SupervisorResponse,
    WorkerResponse,
    AgentParams,
    ClientModeParams,
    ClientParams,
)


class Agents:
    def __init__(
        self,
        model: Optional[str] = "gpt-4o-mini",
        mode: Optional[ClientModeParams] = "md_json",
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        organization: Optional[str] = None,
        top_p: Optional[float] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        max_retries: Optional[int] = 3,
        params: Optional[ClientParams] = None,
        verbose: Optional[bool] = False,
    ):
        from .main import Client
        import networkx as nx

        self.verbose = verbose

        self.params = ClientParams(
            model=model,
            mode=mode,
            base_url=base_url,
            api_key=api_key,
            organization=organization,
            top_p=top_p,
            temperature=temperature,
            max_tokens=max_tokens,
            max_retries=max_retries,
        )

        self.client = Client()
        self.graph = nx.DiGraph()

        self.graph.add_node(
            "supervisor",
            agent=AgentParams(agent_id="supervisor", agent_type="supervisor"),
        )

    def add_worker(
        self,
        agent_id: str,
        instructions: Optional[str] = None,
        model: Optional[str] = "gpt-4o-mini",
        mode: Optional[ClientModeParams] = "md_json",
        tools: List[Any] = [],
        run_tools: Optional[bool] = True,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        organization: Optional[str] = None,
        top_p: Optional[float] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        max_retries: Optional[int] = 3,
    ):
        try:
            params = ClientParams(
                model=model,
                mode=mode,
                base_url=base_url,
                api_key=api_key,
                organization=organization,
                top_p=top_p,
                temperature=temperature,
                max_tokens=max_tokens,
                max_retries=max_retries,
            )
            worker = AgentParams(
                agent_id=agent_id,
                agent_type="worker",
                instructions=instructions,
                tools=tools,
                completion_params=params,
            )
            self.graph.add_node(agent_id, agent=worker)
            self.graph.add_edge("supervisor", agent_id)
        except Exception as e:
            print(f"Error adding agent {agent_id}: {str(e)}")

    def process_user_message(
        self,
        messages: Union[str, List[Dict[str, str]]],
    ):
        if isinstance(messages, list):
            message = messages[-1]["user"]
            prompt = f"""
            As a supervisor agent, analyze the following user message and break it down into specific intents or delegations:  
            
            User Message: {message}
            
            If delegation is needed, provide a list of TaskIntent objects, each containing:
            - intent: A short description of the task
            - description: A detailed explanation of what needs to be done
            - priority: An integer from 1 (lowest) to 5 (highest)
            
            If no delegation is needed, write a response message directly.
            """
            messages[-1]["user"] = prompt
        else:
            message = messages
            prompt = f"""
            As a supervisor agent, analyze the following user message and break it down into specific intents or delegations:  
            
            User Message: {message}
            
            If delegation is needed, provide a list of TaskIntent objects, each containing:
            - intent: A short description of the task
            - description: A detailed explanation of what needs to be done
            - priority: An integer from 1 (lowest) to 5 (highest)
            
            If no delegation is needed, write a response message directly.
            """
            messages = prompt

        try:
            response = self.client.completion(
                messages=messages,
                response_model=SupervisorResponse,
                model=self.params.model,
                mode=self.params.mode,
                base_url=self.params.base_url,
                api_key=self.params.api_key,
                organization=self.params.organization,
                top_p=self.params.top_p,
                temperature=self.params.temperature,
                max_tokens=self.params.max_tokens,
                max_retries=self.params.max_retries,
            )
            if self.verbose:
                print(response)
            return response
        except Exception as e:
            print(f"Error processing user message: {str(e)}")
            return None

    def delegate_tasks(
        self, supervisor_response: Optional[SupervisorResponse]
    ) -> Dict[str, TaskDelegation]:
        delegations = {}

        try:
            worker_agents = list(self.graph.neighbors("supervisor"))
            if not worker_agents:
                print("No worker agents found.")
                return delegations
            for i, delegation in enumerate(supervisor_response.delegations):
                assigned_worker = worker_agents[i % len(worker_agents)]
                delegation.assigned_worker = assigned_worker
                delegations[delegation.task_id] = delegation
        except Exception as e:
            print(f"Error delegating tasks: {str(e)}")
        return delegations

    def execute_worker_task(
        self,
        worker_id: str,
        task: TaskDelegation,
    ):
        try:
            worker = self.graph.nodes[worker_id]["agent"]

            if isinstance(task.intent, TaskIntent):
                task_intent = task.intent.intent
                task_description = task.intent.description
            else:
                task_intent = task.intent["intent"]
                task_description = task.intent["description"]

            worker_prompt = f"""
            You are a worker agent with the following tools and instructions:
            Tools: {worker.tools}
            Instructions: {worker.instructions}
            
            Execute the following task:
            Intent: {task_intent}
            Description: {task_description}
            
            Provide your response as a WorkerResponse object.
            """

            params = worker.completion_params

            response = self.client.completion(
                messages=worker_prompt,
                response_model=WorkerResponse,
                model=params.model,
                mode=params.mode,
                base_url=params.base_url,
                api_key=params.api_key,
                organization=params.organization,
                top_p=params.top_p,
                temperature=params.temperature,
                max_tokens=params.max_tokens,
                max_retries=params.max_retries,
            )
            if self.verbose:
                print(response)
            return response

        except Exception as e:
            print(f"Error executing worker task: {str(e)}")
            return None

    def run(
        self,
        messages: Union[str, List[Dict[str, str]]],
        instructions: Optional[str] = None,
        summarize: Optional[bool] = True,
    ):
        try:
            supervisor_response = self.process_user_message(messages)

            if not supervisor_response:
                return "Error: No response from Supervisor. Something went wrong."

            if not supervisor_response.delegations:
                if supervisor_response.message:
                    return supervisor_response.message
                else:
                    return "Error: No delegations or message provided by Agent."

            delegations = self.delegate_tasks(supervisor_response)

            if not delegations:
                return "Error: No delegations found."

            final_response = []
            for task_id, delegation in delegations.items():
                worker_response = self.execute_worker_task(
                    delegation.assigned_worker, delegation
                )
                if worker_response:
                    delegation.status = worker_response.status
                    delegation.result = worker_response.result
                    final_response.append(
                        f"Task: {delegation.intent.intent}\nResult: {worker_response.result}"
                    )
                else:
                    final_response.append(
                        f"Task: {delegation.intent.intent}\nResult: None"
                    )
        except Exception as e:
            print(f"Error running tasks: {str(e)}")
            return "Error: Failed to run tasks."

        if summarize:
            summary_prompt = "Summarize the results of the following tasks:\n\n"
            summary_prompt += "\n\n".join(final_response)
            if instructions:
                summary_prompt += f"\n\nInstructions : {instructions}"
            summary_prompt += "\n\nProvide a concise summary for the user."

            return self.client.completion(
                messages=summary_prompt,
                model=self.params.model,
                mode=self.params.mode,
                base_url=self.params.base_url,
                api_key=self.params.api_key,
                organization=self.params.organization,
                top_p=self.params.top_p,
                temperature=self.params.temperature,
                max_tokens=self.params.max_tokens,
                max_retries=self.params.max_retries,
            )
        else:
            return final_response
