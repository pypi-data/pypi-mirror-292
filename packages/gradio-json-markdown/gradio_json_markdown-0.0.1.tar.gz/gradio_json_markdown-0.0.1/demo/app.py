
import gradio as gr
from gradio_json_markdown import JsonMarkdown

import json

data = """
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
"""
nested_block = json.loads(data)

example = JsonMarkdown().example_value()

with gr.Blocks() as demo:
    with gr.Row():
        JsonMarkdown(label="Blank"),  # blank component
        JsonMarkdown(value=example, label="Populated"),  # populated component

    JsonMarkdown(value=nested_block, label="Nested JSON")

if __name__ == "__main__":
    demo.launch()
