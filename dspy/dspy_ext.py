from typing import List, Optional, Union, Any
from dsp.utils import dotdict
from dsp.modules.aws_providers import AWSProvider, Bedrock, Sagemaker
from dsp.modules.aws_models import AWSModel
from dspy.datasets.dataset import Dataset
import dspy
import chromadb
from datasets import load_dataset
import random
import json
import dsp
from dspy.signatures.signature import ensure_signature, signature_to_template
from dspy import Prediction

class SolarEnergyQA(Dataset):
    def __init__(self, *args, keep_details=True,**kwargs) -> None:
        super().__init__(*args, **kwargs)
 
        raw_datasets = load_dataset("squad")
        category = 'Solar_energy'
        
        full_train_set = raw_datasets['train'].filter(lambda x: x['title'] == category)
        full_test_set = raw_datasets['validation'].filter(lambda x: x['title'] == category)
        
        train_set = []
        test_set = []
        
        if len(full_test_set) == 0: #If there is no test data set available, split the train set for this
            split_set = full_train_set.train_test_split(test_size=0.1)
            full_train_set,full_test_set = split_set['train'],split_set['test']
        
        if keep_details:
            keys = ['id', 'title', 'context', 'question', 'answer','answer_start']
        else:
            keys = ['context', 'question', 'answer','answer_start']

        for set_item in full_train_set:
            set_item['answer'] = set_item['answers']['text'][0]
            set_item['answer_start'] = str(set_item['answers']['answer_start'][0])
            example = {k: set_item[k] for k in keys}
            train_set.append(example)
        
        for set_item in full_test_set:
            set_item['answer'] = set_item['answers']['text'][0]
            set_item['answer_start'] = str(set_item['answers']['answer_start'][0])
            example = {k: set_item[k] for k in keys}
            test_set.append(example)

        rng = random.Random(0)
        rng.shuffle(train_set)

        self._train = train_set
        self._test = test_set

class CUAD(Dataset):
    def __init__(self, *args,**kwargs) -> None:
        super().__init__(*args, **kwargs)
 
        raw_datasets = load_dataset("cuad")
       
        full_train_set = raw_datasets['train']
        full_test_set = raw_datasets['test']
        
        train_set = []
        test_set = []
        
        if len(full_test_set) == 0: #If there is no test data set available, split the train set for this
            split_set = full_train_set.train_test_split(test_size=0.1)
            full_train_set,full_test_set = split_set['train'],split_set['test']
        
        keys = ['id', 'title', 'context', 'question', 'answer','answer_start']

        for set_item in full_train_set:
            if len(set_item['answers']['text']) > 0:
                set_item['answer'] = set_item['answers']['text'][0]
                set_item['answer_start'] = str(set_item['answers']['answer_start'][0])
                example = {k: set_item[k] for k in keys}
                train_set.append(example)
        
        for set_item in full_test_set:
             if len(set_item['answers']['text']) > 0:
                set_item['answer'] = set_item['answers']['text'][0]
                set_item['answer_start'] = str(set_item['answers']['answer_start'][0])
                example = {k: set_item[k] for k in keys}
                test_set.append(example)

        rng = random.Random(0)
        rng.shuffle(train_set)

        self._train = train_set
        self._test = test_set


#This is based on https://github.com/stanfordnlp/dspy/blob/1c10a9d476737533a53d6bee62c234e375eb8fcb/dspy/predict/predict.py
class PredictMultiModal(dspy.Predict):
    def __init__(self, signature, activated=True, **config):
        super().__init__(signature, **config)
        self.activated = activated
        signature = self.signature
        *keys, last_key = signature.fields.keys()

    def __call__(self, *arg, **kwargs):
        if len(arg) > 0: 
            kwargs = {**arg[0], **kwargs}

        return self.forward(**kwargs)
    
    def forward(self, **kwargs):
        # Extract the three privileged keyword arguments.
        new_signature = ensure_signature(kwargs.pop("new_signature", None))
        signature = ensure_signature(kwargs.pop("signature", self.signature))
        demos = kwargs.pop("demos", self.demos)
        config = dict(**self.config, **kwargs.pop("config", {}))
        image_prompt = {}
        image_fields = []
        lm = kwargs.pop("lm", self.lm) or dsp.settings.lm
        assert lm is not None, "No LM is loaded."

        # This is from the base class 
        temperature = config.get("temperature")
        temperature = lm.kwargs["temperature"] if temperature is None else temperature

        num_generations = config.get("n")
        if num_generations is None:
            num_generations = lm.kwargs.get("n", lm.kwargs.get("num_generations", 1))

        if (temperature is None or temperature <= 0.15) and num_generations > 1:
            config["temperature"] = 0.7

        x = dsp.Example(demos=demos, **kwargs)

        if new_signature is not None:
            signature = new_signature

        if not all(k in kwargs for k in signature.input_fields):
            present = [k for k in signature.input_fields if k in kwargs]
            missing = [k for k in signature.input_fields if k not in kwargs]
            print(f"WARNING: Not all input fields were provided to module. Present: {present}. Missing: {missing}.")


        # Look up the appropriate fields in each demonstration.
        x = x.demos_at(lambda d: d[self.stage])

        #Remove the image prompt fields from signature
        for k,v in signature.input_fields.items():
            if "format" in v.json_schema_extra and (v.json_schema_extra["format"] == "jpg" or v.json_schema_extra["format"] == "png"):
                image_fields.append(k)
                #image_prompt[k] = {v.json_schema_extra["format"]:v}
                image_prompt[k] = {v.json_schema_extra["format"]:x.pop(k)}
                signature.model_fields.pop(k)

        template = signature_to_template(signature)

        # Generate and extract the fields.
        prompt = template(x)
        if self.lm is None:
            C: list[dict[str, Any]] = dsp.settings.lm(prompt,image_prompt, **kwargs)
        else:
            with dsp.settings.context(lm=self.lm, query_only=True):
                C: list[dict[str, Any]] = dsp.settings.lm(prompt,image_prompt, **kwargs)

        completions = []
        for c in C:
            completions.append({})
            for field in template.fields:
                if field.output_variable not in kwargs.keys():
                    completions[-1][field.output_variable] = c 

        pred = Prediction.from_completions(completions, signature=signature)

        if kwargs.pop("_trace", True) and dsp.settings.trace is not None:
            trace = dsp.settings.trace
            trace.append((self, {**kwargs}, pred))

        return pred
 
class AWSAnthropicMultiModal(AWSModel):

    def __init__(
        self,
        aws_provider: AWSProvider,
        model: str,
        max_context_size: int = 200000,
        max_new_tokens: int = 1500,
        **kwargs,
    ) -> None:

        super().__init__(
            model=model,
            max_context_size=max_context_size,
            max_new_tokens=max_new_tokens,
            **kwargs,
        )
        self.aws_provider = aws_provider
        self.provider = aws_provider.get_provider_name()

        if isinstance(self.aws_provider, Bedrock):
            self.kwargs["anthropic_version"] = "bedrock-2023-05-31"

        for k, v in kwargs.items():
            self.kwargs[k] = v


    def __call__(self,prompt: str,images:str,only_completed: bool = True,return_sorted: bool = False,**kwargs,) -> list[str]:
        n, body = self._create_body(prompt,images,**kwargs)
        generated = self._call_model(json.dumps(body))
        return [generated]

    def _create_body(self, prompt: str, images:str, **kwargs) -> tuple[int, dict[str, str | float]]:
        base_args: dict[str, Any] = self.kwargs

        image_prompts = []
        for k,v in images.items():
            img_ext, imgbase64_str = list(v.items())[0]
            image_prompts.append({"type": "image", "source": {"type": "base64","media_type": f"image/{img_ext}","data": imgbase64_str}})

        n, query_args = self.aws_provider.sanitize_kwargs(base_args)

        # Anthropic models do not support the following parameters
        query_args.pop("frequency_penalty", None)
        query_args.pop("num_generations", None)
        query_args.pop("presence_penalty", None)
        query_args.pop("model", None)
        text_prompts = [{"type": "text","text": prompt}]
        query_args["messages"] = [{"role": "user","content": text_prompts + image_prompts}]
        return (n, query_args)

    def _call_model(self, body: str) -> str:
        response = self.aws_provider.call_model(
            model_id=self._model_name,
            body=body
        )
        response_body = json.loads(response["body"].read())
        completion = response_body["content"][0]["text"]
        return completion


class ChromadbRMMultiModal(dspy.Retrieve):
    def __init__(
        self,
        collection: chromadb.Collection,
        embedding_function,
        k: int = 7,
    ):
        self._chromadb_collection = collection
        self.ef= embedding_function
        super().__init__(k=k)

    def _get_embeddings(self, query: str, imagebase64: Optional[str]= None) -> List[List[float]]:
        return self.ef.embed(inputText=query,inputImage=imagebase64)

    def forward(
        self, query: str, imagebase64: Optional[str]= None, k: Optional[int] = None, **kwargs,) -> dspy.Prediction:
        embeddings = self._get_embeddings(query,imagebase64)
        k = self.k if k is None else k
        results = self._chromadb_collection.query(query_embeddings=embeddings, n_results=k,**kwargs,)
        zipped_results = zip(
            results["ids"][0], 
            results["distances"][0], 
            results["documents"][0], 
            results["metadatas"][0])
        results = [dotdict({"id": id, "score": dist, "long_text": doc, "metadatas": meta }) for id, dist, doc, meta in zipped_results]
        return results