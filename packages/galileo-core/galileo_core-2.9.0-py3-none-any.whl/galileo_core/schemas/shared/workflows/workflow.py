from typing import List

from pydantic import BaseModel, Field

from galileo_core.schemas.shared.workflows.step import AWorkflowStep


class Workflow(BaseModel):
    workflows: List[AWorkflowStep] = Field(default_factory=list, description="List of workflows.")
