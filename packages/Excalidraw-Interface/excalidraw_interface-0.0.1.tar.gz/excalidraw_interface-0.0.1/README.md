# Excalidraw_Interface

![Tests Badge](https://github.com/RobertJN64/Excalidraw_Interface/actions/workflows/tests.yml/badge.svg)
![Python Version Badge](https://img.shields.io/pypi/pyversions/Excalidraw_Interface)
![License Badge](https://img.shields.io/github/license/RobertJN64/Excalidraw_Interface)

A pythonic interface for creating diagrams in Excalidraw.

Based on https://github.com/BardOfCodes/procXD by Aditya Ganeshan (MIT License) and updated with modern python support
and API improvements.

## Example: Flowchart

[flowchart.py](Excalidraw_Interface/examples/flowchart.py)

![flowchart image](images/flowchart.png)

```python
from Excalidraw_Interface import SketchBuilder

flowchart_items = ['First Step', 'Second Step', 'Third Step']

sb = SketchBuilder() # Create a Sketch

prev_item = sb.TextBox("Start Here", x = 0, y = 0) # Create a Text Box
for index, item in enumerate(flowchart_items):
    new_item = sb.TextBox(item, x = 0, y = (index+1) * 150) # Create a Text Box
    sb.create_binding_arrows(prev_item, new_item) # Create arrows between boxes
    prev_item = new_item

hcb = sb.HeaderContentBox("Header", "Content", x = -200, y = 400) # Create a multiline text box
circle = sb.Ellipse(200, 400, width=50, height=50, backgroundColor = 'red',
                    roughness=1) # Create a red circle in hand drawn style

sb.create_binding_arrows(prev_item, hcb, sb.DoubleArrow) # Create a double headed arrow
sb.create_binding_arrows(prev_item, circle, strokeColor = 'blue') # Create an blue arrow

sb.export_to_file('out.excalidraw')
```