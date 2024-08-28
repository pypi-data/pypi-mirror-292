
import gradio as gr
from app import demo as app
import os

_docs = {'JsonMarkdown': {'description': 'Used to display arbitrary JsonMarkdown output prettily. As this component does not accept user input, it is rarely used as an input component.\n', 'members': {'__init__': {'value': {'type': 'str | dict | list | Callable | None', 'default': 'None', 'description': 'Default value as a valid JsonMarkdown `str` -- or a `list` or `dict` that can be serialized to a JsonMarkdown string. If callable, the function will be called whenever the app loads to set the initial value of the component.'}, 'label': {'type': 'str | None', 'default': 'None', 'description': 'The label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.'}, 'every': {'type': 'Timer | float | None', 'default': 'None', 'description': 'Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.'}, 'inputs': {'type': 'Component | Sequence[Component] | set[Component] | None', 'default': 'None', 'description': 'Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.'}, 'show_label': {'type': 'bool | None', 'default': 'None', 'description': 'if True, will display label.'}, 'container': {'type': 'bool', 'default': 'True', 'description': 'If True, will place the component in a container - providing some extra padding around the border.'}, 'scale': {'type': 'int | None', 'default': 'None', 'description': 'relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.'}, 'min_width': {'type': 'int', 'default': '160', 'description': 'minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.'}, 'visible': {'type': 'bool', 'default': 'True', 'description': 'If False, component will be hidden.'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'elem_classes': {'type': 'list[str] | str | None', 'default': 'None', 'description': 'An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'render': {'type': 'bool', 'default': 'True', 'description': 'If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.'}, 'key': {'type': 'int | str | None', 'default': 'None', 'description': 'if assigned, will be used to assume identity across a re-render. Components that have the same key across a re-render will have their value preserved.'}, 'open': {'type': 'bool', 'default': 'False', 'description': 'If True, all JsonMarkdown nodes will be expanded when rendered. By default, node levels deeper than 3 are collapsed.'}, 'show_indices': {'type': 'bool', 'default': 'False', 'description': 'Whether to show numerical indices when displaying the elements of a list within the JsonMarkdown object.'}, 'height': {'type': 'int | str | None', 'default': 'None', 'description': 'Height of the JsonMarkdown component in pixels if a number is passed, or in CSS units if a string is passed. Overflow will be scrollable. If None, the height will be automatically adjusted to fit the content.'}}, 'postprocess': {'value': {'type': 'dict | list | str | None', 'description': 'Expects a valid JsonMarkdown `str` -- or a `list` or `dict` that can be serialized to a JsonMarkdown string. The `list` or `dict` value can contain numpy arrays.'}}, 'preprocess': {'return': {'type': 'dict | list | None', 'description': 'Passes the JsonMarkdown value as a `dict` or `list` depending on the value.'}, 'value': None}}, 'events': {'change': {'type': None, 'default': None, 'description': 'Triggered when the value of the JsonMarkdown changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input.'}}}, '__meta__': {'additional_interfaces': {}, 'user_fn_refs': {'JsonMarkdown': []}}}

abs_path = os.path.join(os.path.dirname(__file__), "css.css")

with gr.Blocks(
    css=abs_path,
    theme=gr.themes.Default(
        font_mono=[
            gr.themes.GoogleFont("Inconsolata"),
            "monospace",
        ],
    ),
) as demo:
    gr.Markdown(
"""
# `gradio_json_markdown`

<div style="display: flex; gap: 7px;">
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.1%20-%20orange">  
</div>

JSON module with markdown support
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_json_markdown
```

## Usage

```python

import gradio as gr
from gradio_json_markdown import JsonMarkdown

import json

data = \"\"\"
{
  "conversations": [
    {
      "value": "Modify the function to accept a list of integers and a positive integer `n` as input. The function should return the largest product that can be formed by selecting `n` integers from the list, where `n` is at least 2. For example, given the list `[-10,-20,5,6,7]` and `n=3`, the function should return `600` because the largest product is formed by selecting `-10`, `-20`, and `6` and multiplying them together. However, given `n=4`, the function should return `-1400` because the largest product is formed by selecting `-10`, `-20`, `5`, and `7`. Ensure the function handles cases where `n` is greater than the length of the input list by returning an appropriate message.",
      "from": "User",
      "canonical_form": ""
    },
    {
      "value": "```python\\ndef largest_product_n(nums, n):\\n    if n > len(nums):\\n        return \\\"n must be less than or equal to the length of the input list\\\"\\n    nums.sort()  # sort the list\\n    # return the product of the last 'n' elements (largest 'n' numbers) or\\n    # the product of the first 'n' elements (smallest 'n' numbers), whichever is greater\\n    return max(nums[-n] * nums[-1] *\\n               reduce(lambda x, y: x * y, nums[-n:-1], 1),\\n               nums[0] * nums[n-1] *\\n               reduce(lambda x, y: x * y, nums[1:n], 1))\\n\\n# I used functool's reduce function, so import reduce from functools module\\nfrom functools import reduce\\n\\n# test cases\\nprint(largest_product_n([-10,-20,5,6,7], 3))  # returns 600\\nprint(largest_product_n([-10,-20,5,6,7], 4))  # returns -1400\\nprint(largest_product_n([1,2,3,4,5], 2))  # returns 20\\nprint(largest_product_n([1,2,3,4,5], 6))  # returns \\\"n must be less than or equal to the length of the input list\\\"\\n\\n```\\nPlease note, this code assumes that you always have at least `n` integers in the input list. If this is not the case, you should add a check for this in the function.\\n\\nThe function sorts the integers in the list and checks if the product of the largest `n` integers or the product of the smallest  integers (with one exception, explained below) is larger.\\n\\nFor the smallest integers, the function multiplies the smallest integer (nums[0]) with the \\\"n-1\\\"th integer (since the smallest integer is already included), and with the product of all integers between the 1st and the \\\"n-1\\\"th index.\\n\\nFor the largest integers, the function multiplies the largest integer (nums[-1]) with the \\\"n\\\"th integer (with the sign taken into account, since if there are negative integers we want to include as many as possible), and with the product of all integers between the \\\"n\\\"th and the second last index. If all integers are positive, the product of the largest integers is always larger or equal than the product of the smallest integers. If there is one negative integer, the product of the largest integers is always larger, since -1*(-1)*any_positive_number > any_postive_number.\\n\\nThis case is different if there is more than one negative number. If there is more than one negative number, the product of the smallest integers could be larger than the product of the largest integers, since (-n1)*(-n2) > p1*p2, where n1, n2 are negative integers and p1, p2 are positive integers. Since we take the maximum product, this case is also covered.\\n\\nIn Python, indices start from 0 and go up to n-1, so nums[-n] denotes the n-th integer from the right (last 'n' integers), and nums[-1] denotes the last integer, corresponding to the largest integer. Likewise, nums[1:n] denotes the integers between index 1 and index n-1. The reduce function is used to multiply all integers in a range. For example, reduce(lambda x, y: x * y, [1,2,3,4,5]) is equivalent to 1*2*3*4*5, and returns `120`.\\n\\nThe input `n` is the number of integers we want to select to form our product. For this problem, we assume `n >= 2`. This condition should be checked before calling the function. We also assume that the input is a list of integers. The case where `n > len(nums)` is handled by returning an error message. If `n == 1`, the function would still work, but it would not make much sense, since it would always return the largest integer in the input list.",
      "from": "Assistant",
      "canonical_form": ""
    }
  ],
  "system": "",
  "mask": "User",
  "type": null,
  "task_id": 1450799
}
\"\"\"
nested_block = json.loads(data)

example = JsonMarkdown().example_value()

with gr.Blocks() as demo:
    with gr.Row():
        JsonMarkdown(label="Blank"),  # blank component
        JsonMarkdown(value=example, label="Populated"),  # populated component

    JsonMarkdown(value=nested_block, label="Nested JSON")

if __name__ == "__main__":
    demo.launch()

```
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `JsonMarkdown`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["JsonMarkdown"]["members"]["__init__"], linkify=[])


    gr.Markdown("### Events")
    gr.ParamViewer(value=_docs["JsonMarkdown"]["events"], linkify=['Event'])




    gr.Markdown("""

### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As input:** Is passed, passes the JsonMarkdown value as a `dict` or `list` depending on the value.
- **As output:** Should return, expects a valid JsonMarkdown `str` -- or a `list` or `dict` that can be serialized to a JsonMarkdown string. The `list` or `dict` value can contain numpy arrays.

 ```python
def predict(
    value: dict | list | None
) -> dict | list | str | None:
    return value
```
""", elem_classes=["md-custom", "JsonMarkdown-user-fn"], header_links=True)




    demo.load(None, js=r"""function() {
    const refs = {};
    const user_fn_refs = {
          JsonMarkdown: [], };
    requestAnimationFrame(() => {

        Object.entries(user_fn_refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}-user-fn`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })

        Object.entries(refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })
    })
}

""")

demo.launch()
