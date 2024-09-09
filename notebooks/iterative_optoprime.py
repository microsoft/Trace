import json
import tqdm
import coding_env
import time
import opto
import opto.optimizers
import opto.trace as trace
import autogen


split = "test"
env = coding_env.CodeRepairEnv(split=split, with_mistral=True)
env = coding_env.ObservationWrapper(env)

results = []
for task_idx in tqdm.tqdm(coding_env.TEST_INDICES): # range(len(env.data)):
    prompt, _ = env.reset(options=dict(task_idx=task_idx))
    prompt = coding_env.SYSTEM_PROMPT + '\n' + prompt

    text_with_cot = trace.node(env.d['mistral_output'], trainable=True)
    optimizer = opto.optimizers.OptoPrime(
        [text_with_cot], config_list=autogen.config_list_from_json("OAI_CONFIG_LIST_4")
    )
    optimizer.objective = prompt

    for i in range(5):
        code = trace.bundle()(coding_env.extract_code)(text_with_cot)
        print(f"Iter {i}")
        print(f"Code: {code.data}")
        next_obs, reward, term, trunc, info = env.step(code.data)
        feedback = coding_env.construct_feedback(reward, info)

        optimizer_suggestion = None
        try:
            optimizer.zero_feedback()
            optimizer.backward(code, feedback)
            optimizer.step(verbose='output')
            optimizer_suggestion = optimizer.suggestion
        except:
            pass
            # optimizer_suggestion is None is a way to check if the optimizer failed

        results.append({
            'timestamp': time.time(),
            'task_idx': task_idx,
            'iter_idx': i,
            'text_with_cot': text_with_cot.data,
            'code': code.data,
            'reward': reward,
            'trace_output': info['trace_output'],
            'feedback': feedback,
            'optimizer_suggestion': optimizer_suggestion,
        })

        if term:
            break

with open(f'output/test1_trace_opt_results/test.jsonl', 'w') as f:
    for result in results:
        f.write(json.dumps(result) + '\n')