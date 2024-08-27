import os
import gc
import copy

import numpy as np

try:
    from llama_cpp import Llama
    use_gpu = True
except ModuleNotFoundError:
    use_gpu = False

from gpt4all import GPT4All

from Orange.data import Domain, StringVariable, Table


def generate_answers(table, model_path, progress_callback=None, argself=None):
    if table is None:
        return

    # Copy of input data
    data = copy.deepcopy(table)
    attr_dom = list(data.domain.attributes)
    metas_dom = list(data.domain.metas)
    class_dom = list(data.domain.class_vars)

    # Load model
    if os.path.exists(model_path):
        model = load_model(model_path, n_gpu_layers=0)
    else:
        print(f"Model could not be found: {model_path} does not exist")
        return

    # Generate answers on column named "prompt"
    try:
        rows = []
        for i, row in enumerate(data):
            features = list(data[i])
            metas = list(data.metas[i])
            answer = run_query(str(row["prompt"]), model=model, stream=True, argself=argself)
            metas += [answer]
            rows.append(features + metas)
            if progress_callback is not None:
                progress_value = float(100 * (i + 1) / len(data))
                progress_callback(progress_value)
    except ValueError as e:
        print("An error occurred when trying to generate an answer:", e)
        return
    # model.close()

    # Generate new Domain to add to data
    answer_dom = [StringVariable("Answer")]

    # Create and return table
    domain = Domain(attributes=attr_dom, metas=metas_dom + answer_dom, class_vars=class_dom)
    out_data = Table.from_list(domain=domain, rows=rows)
    return out_data


def load_model(path, n_gpu_layers=0):
    if use_gpu:
        model = Llama(path,
                      n_ctx=4096,
                      n_gpu_layers=n_gpu_layers)
    else:
        model = GPT4All(model_path=path,
                        model_name=path,
                        n_ctx=4096,
                        allow_download=False, verbose=True)
    return model


def query_cpu(prompt, model, max_tokens=4096, temperature=0, top_p=0.95, top_k=40, repeat_penalty=1.1, stream=False, argself=None):
    if not stream:
        output = model.generate(prompt,
                                max_tokens=max_tokens,
                                temp=temperature,
                                top_p=top_p,
                                top_k=top_k,
                                repeat_penalty=repeat_penalty)
    else:
        output = ""
        for token in model.generate(prompt,
                                    max_tokens=max_tokens,
                                    temp=temperature,
                                    top_p=top_p,
                                    top_k=top_k,
                                    repeat_penalty=repeat_penalty,
                                    streaming=True):
            output += token
            if argself is not None:
                if argself.stop:
                    break
                    # TODO Memory Leak
    return output


def query_gpu(prompt, model, max_tokens=4096, temperature=0, top_p=0.95, top_k=40, repeat_penalty=1.1, stream=False, argself=None):
    if not stream:
        output = model(prompt,
                       max_tokens=max_tokens,
                       temperature=temperature,
                       top_p=top_p,
                       top_k=top_k,
                       repeat_penalty=repeat_penalty)["choices"][0]["text"]
    else:
        output = ""
        for token in model(prompt,
                           max_tokens=max_tokens,
                           temperature=temperature,
                           top_p=top_p,
                           top_k=top_k,
                           repeat_penalty=repeat_penalty,
                           stream=True):
            output += token["choices"][0]["text"]
            if argself is not None:
                if argself.stop:
                    break
    return output


def run_query(prompt, model, max_tokens=4096, temperature=0, top_p=0.95, top_k=40, repeat_penalty=1.1, stream=False, argself=None):
    if use_gpu:
        return query_gpu(prompt, model, max_tokens, temperature, top_p, top_k, repeat_penalty, stream, argself=argself)
    else:
        return query_cpu(prompt, model, max_tokens, temperature, top_p, top_k, repeat_penalty, stream, argself=argself)
