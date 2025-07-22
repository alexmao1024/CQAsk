"""
Schemdraw 2D电路图代码生成器
专门用于生成schemdraw代码并执行
"""

import matplotlib
matplotlib.use('Agg')  # 使用非GUI后端，避免线程警告

import schemdraw
import schemdraw.elements as elm
import os
import openai
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Any
import traceback

load_dotenv()

# Schemdraw代码生成客户端
schemdraw_client = openai.OpenAI(
    api_key=os.environ["SILICONFLOW_API_KEY"],
    base_url="https://api.siliconflow.cn/v1",
)

def generate_schemdraw_code(user_msg: str, conversation_history: List[Dict[str, str]] = None, error_message: str = None):
    """
    生成schemdraw代码用于2D电路图绘制
    """
    
    # 专门用于schemdraw的系统提示词
    schemdraw_system_msg = """
You are an expert in electrical circuit design and schemdraw library. Your goal is to generate Python code using schemdraw to create professional electrical circuit diagrams based on user requests.

### Core Rules
1. **Output Format**: Generate ONLY Python code using schemdraw library
2. **Required Structure**: Your response must be valid Python code that can be executed directly
3. **Variable Name**: The drawing object MUST be assigned to a variable named `d`
4. **Library Usage**: Use `import schemdraw` and `import schemdraw.elements as elm`

### Schemdraw Syntax
- **Basic Structure**:
```python
import schemdraw
import schemdraw.elements as elm

d = schemdraw.Drawing(backend='matplotlib', show=False)
with d:
    # Add circuit elements here
    elm.Battery().up().label('9V')
    elm.Resistor().right().label('R1')
    # etc.
```

- **Common Elements**:
  - `elm.Resistor().direction().label('text')` - Resistor
  - `elm.Capacitor().direction().label('text')` - Capacitor
  - `elm.Battery().direction().label('text')` - Battery/DC source
  - `elm.SourceSin().direction().label('text')` - AC source
  - `elm.Inductor().direction().label('text')` - Inductor
  - `elm.Diode().direction().label('text')` - Diode
  - `elm.Line().direction()` - Connecting wire
  - `elm.Dot()` - Junction/connection point
  - `elm.Ground()` - Ground symbol
  - `elm.Switch().direction().label('text')` - Switch

- **Directions**: `.up()`, `.down()`, `.left()`, `.right()`
- **Labels**: `.label('component_name')` or `.label('value')`

- **Positioning**:
  - `d.push()` - Save current position
  - `d.pop()` - Return to saved position
  - Elements automatically connect to the end of the previous element

### Example Patterns

**Series Circuit**:
```python
import schemdraw
import schemdraw.elements as elm

d = schemdraw.Drawing(backend='matplotlib', show=False)
with d:
    elm.Battery().up().label('12V')
    elm.Resistor().right().label('R1')
    elm.Resistor().right().label('R2')
    elm.Line().down()
    elm.Line().left()
    elm.Line().left()
```

**Parallel Circuit**:
```python
import schemdraw
import schemdraw.elements as elm

d = schemdraw.Drawing(backend='matplotlib', show=False)
with d:
    elm.Battery().up().label('12V')
    elm.Dot()
    # Upper branch
    elm.Line().right()
    elm.Resistor().right().label('R1')
    elm.Line().right()
    elm.Dot()
    # Lower branch
    d.push()
    elm.Line().down()
    elm.Resistor().left().label('R2')
    elm.Line().up()
    d.pop()
    # Return path
    elm.Line().down()
    elm.Line().left()
    elm.Line().left()
    elm.Line().left()
```

### Important Notes
- Always use `with d:` context manager
- Elements connect automatically to the previous element's endpoint
- Use `elm.Dot()` for junctions in parallel circuits
- Use `d.push()` and `d.pop()` for branching
- Add meaningful labels to components
- Generate code that creates a complete, properly connected circuit
- DO NOT call d.show(), d.save(), or any display functions - the system will handle SVG generation

### Response Format
Respond ONLY with Python code. Do not include explanations, markdown formatting, or any other text.
"""

    # 构建消息列表
    messages = [{"role": "system", "content": schemdraw_system_msg}]
    
    # 添加对话历史
    if conversation_history:
        messages.extend(conversation_history)
    
    # 如果有错误信息，添加错误重试消息
    if error_message:
        error_prompt = f"上面的代码执行时出现了错误：\n{error_message}\n\n请修复代码中的问题并重新生成完整的schemdraw代码。"
        if conversation_history:
            messages.append({"role": "user", "content": error_prompt})
        else:
            messages.append({"role": "user", "content": f"{user_msg}\n\n{error_prompt}"})
    else:
        if not conversation_history:
            messages.append({"role": "user", "content": user_msg})
    
    # 调用大模型
    response = schemdraw_client.chat.completions.create(
        model="Qwen/Qwen2.5-72B-Instruct-128K",
        messages=messages,
    )

    id = datetime.now().isoformat().replace(":", "-")

    # 创建data/generated目录
    if not os.path.exists("data/generated"):
        os.makedirs("data/generated")

    file_name = f"data/generated/{id}.py"
    code_content = clean_schemdraw_code(response.choices[0].message.content)
    
    with open(file_name, "w", encoding='utf-8') as f:
        f.write(code_content)

    # 尝试执行代码
    try:
        with open(file_name, "r", encoding='utf-8') as f:
            code_to_execute = f.read()
        
        # 创建执行环境
        exec_globals = {
            'schemdraw': schemdraw,
            'elm': elm
        }
        exec(code_to_execute, exec_globals)
        
        if 'd' not in exec_globals:
            raise ValueError("Generated code does not define 'd' variable (schemdraw Drawing object)")
        
        # 生成SVG
        drawing = exec_globals['d']
        svg_content = drawing.get_imagedata('svg')
        
        # 保存SVG
        svg_path = f"data/generated/{id}.svg"
        with open(svg_path, 'wb') as f:
            f.write(svg_content)

        svg_string = svg_content.decode('utf-8')
        svg_cleaned_string = svg_string.replace('\n', ' ').replace('\r', ' ')

        return id, svg_cleaned_string, None
        
    except Exception as e:
        # 收集详细的错误信息
        error_info = {
            "type": type(e).__name__,
            "message": str(e),
            "traceback": traceback.format_exc()
        }
        return id, None, error_info

def clean_schemdraw_code(code_text: str) -> str:
    """清理schemdraw代码，移除 Markdown 格式标记"""
    lines = code_text.split('\n')
    clean_lines = []
    for line in lines:
        if line.strip() and not line.startswith('```') and not line.endswith('```'):
            clean_lines.append(line)
    return '\n'.join(clean_lines) 