import json
import time

from transformers import AutoTokenizer, AutoModelForCausalLM

from dingo.model import Model
from dingo.model.modelres import ModelRes
from dingo.model.llm.base import BaseLLM
from dingo.config.config import DynamicLLMConfig
from dingo.utils import log

try:
    import torch
except ImportError as e:
    log.warning("=========== llama3 register fail. Please check whether install torch. ===========")


@Model.llm_register('llama3')
class LLaMa3(BaseLLM):
    model = None
    tokenizer = None

    custom_config = DynamicLLMConfig(
        prompt = """
Please rate the following sentences based on their fluency, completeness, and level of repetition. 
The scores from low to high indicate the quality of the sentences, with values ranging from 0 to 10 and reasons given. 
Please provide a JSON format reply containing the specified key and value.
requirement:
-The returned content must be in JSON format and there should be no extra content.
-The first key returned is score, which is an integer between 0 and 10.
-The second key returned is type, with a value of one of the following: unsmooth, incomplete, or repetitive. If the sentence is correct, this value is empty.
-The third key returned is reason, and the value is the reason for scoring.
-If the sentence is empty, please give it a score of 0.


%s

        """
    )

    @classmethod
    def generate_words(cls, input_data: str) -> json:
        if cls.model is None:
            cls.model = AutoModelForCausalLM.from_pretrained(
                cls.custom_config.path,
                torch_dtype=torch.bfloat16,
                device_map="auto",
            )
        if cls.tokenizer is None:
            cls.tokenizer = AutoTokenizer.from_pretrained(cls.custom_config.path)

        messages = [
            {"role": "system", "content": input_data},
        ]

        input_ids = cls.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(cls.model.device)

        terminators = [
            cls.tokenizer.eos_token_id,
            cls.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]

        outputs = cls.model.generate(
            input_ids,
            max_new_tokens=256,
            eos_token_id=terminators,
            do_sample=True,
            temperature=0.6,
            top_p=0.9,
        )
        response = outputs[0][input_ids.shape[-1]:]
        return json.loads(cls.tokenizer.decode(response, skip_special_tokens=True))


    @classmethod
    def call_api(cls, input_data: str) -> ModelRes:
        attempts = 0
        except_msg = ''
        while attempts < 3:
            try:
                response = cls.generate_words(cls.custom_config.prompt % input_data)

                return ModelRes(
                    error_status=False if response['score'] > 6 else True,
                    error_type='QUALITY_IRRELEVANCE',
                    error_name=response['type'],
                    error_reason=response['reason']
                )
            except Exception as e:
                attempts += 1
                time.sleep(1)
                except_msg = str(e)

        return ModelRes(
            error_status=True,
            error_type='QUALITY_IRRELEVANCE',
            error_name="API_LOSS",
            error_reason=except_msg
        )
