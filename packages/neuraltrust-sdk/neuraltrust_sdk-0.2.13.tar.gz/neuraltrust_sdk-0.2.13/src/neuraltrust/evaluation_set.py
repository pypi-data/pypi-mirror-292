from typing import Dict
from .evaluator import Evaluator
import pandas as pd
from .utils import _generate_id
from .interfaces.data import DataPoint
from .target import complete
from croniter import croniter
import datetime
import json
from .llm.client import ChatMessage
from .testset import Testset
from .services.api_service import NeuralTrustApiService

class EvaluationSet:
    def __init__(self, id: str = None, name: str = None, description: str = None, scheduler: str = None):
        if id is None:
            if name is None or description is None:
                raise ValueError("Name and description are required when creating a new EvaluationSet")
            self.id = _generate_id(name)
            self.name = name
            self.description = description
            
            if not self._is_valid_cron(scheduler):
                raise ValueError("Invalid cron expression for scheduler")
            self.scheduler = scheduler
            
            self._create()
        else:
            self.id = id
            self._load_existing_evaluation_set()
            
            if self.testset_id is None:
                raise Warning("Testset is required when create_testset is False")
        
        self._update({'status': 'running'})
    
    def _create(self):
        """
        Creates a new evaluation set with the specified properties.
        Raises:
        - Exception: If the testset could not be created due to an error like invalid parameters, database errors, etc.
        """
        evalset_data = {
            "id": self.id,
            "name": self.name,
            "testsetId": self.testset_id,
            "status": "ready",
            "description": self.description,
            "scheduler": self.scheduler,
            "numQuestions": self.num_questions or 0,
        }

        try:
            NeuralTrustApiService.create_evaluation_set(evalset_data)
        except Exception as e:
            raise
    
    def _update(self, eval_set: Dict):
        """
        Updates an existing evaluation set with the specified properties.
        Raises:
        - Exception: If the testset could not be updated due to an error like invalid parameters, database errors, etc.
        """
        try:
            NeuralTrustApiService.update_evaluation_set(self.id, eval_set)
        except Exception as e:
            raise

    def _load_existing_evaluation_set(self):
        evalset_data = NeuralTrustApiService.load_evaluation_set(self.id)
        self.name = evalset_data.get("name")
        self.status = evalset_data.get("status")
        self.description = evalset_data.get("description")
        self.scheduler = evalset_data.get("scheduler")
        self.num_questions = evalset_data.get("numQuestions")
        self.testset_id = evalset_data.get("testsetId", None)

    def _is_valid_cron(self, cron_expression: str) -> bool:
        try:
            croniter(cron_expression, datetime.datetime.now())
            return True
        except ValueError:
            return False
    
    def _get_next_run_at(self):
        cron = croniter(self.scheduler, datetime.datetime.utcnow())
        return cron.get_next(datetime.datetime).isoformat()

    def run(self, max_parallel_evals: int = 5) -> Dict:
        try:        
            remote_data = self._load_testset_from_neuraltrust(self.testset_id)
            if not remote_data:
                raise ValueError(f"No data found for testset_id: {self.testset_id}")
            dataset = [DataPoint(**row) for row in remote_data]
            
            evaluator = Evaluator(evaluation_set_id=self.id, testset_id=self.testset_id, next_run_at=self._get_next_run_at(), neuraltrust_failure_threshold=0.7)
            data = [self._run_target(data) for data in dataset]

            results = evaluator.run_batch( 
                        data=data, 
                        max_parallel_evals=max_parallel_evals)
            
            return results
        except Exception as e:
            self._update({'status': 'failed'})
            raise
    
    def _run_target(self, data: DataPoint) -> DataPoint:
        context = (data['context'] or "") + "\n" + data['query']
        conversation_history = []
        if data['conversation_history'] is not None and data['conversation_history'] != "[]":
            conversation_history = [ChatMessage(**json.loads(msg)) if isinstance(msg, str) else ChatMessage(role=msg.get('role', ''), content=msg.get('content', '')) for msg in json.loads(data['conversation_history'])]
        response = complete({"system_prompt": ""}, context, conversation_history)

        if response.content is None:
            raise ValueError("No content in response")
        data['response'] = response.content
        return data

    def _load_testset_from_neuraltrust(self, testset_id: str):
        try:
            return Testset.fetch_testset_rows(
                testset_id=testset_id
            )
        except Exception as e:
            raise ValueError(f"Failed to load testset to NeuralTrust: {e}")