"""
CadQuery 3D代码生成器
专门用于生成3D CadQuery代码
"""

import importlib
import os
import openai
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Tuple, Any
import traceback

load_dotenv()

# CadQuery代码生成客户端
client = openai.OpenAI(
    api_key=os.environ["SILICONFLOW_API_KEY"],
    base_url="https://api.siliconflow.cn/v1",
)

def clean_code(code_text: str) -> str:
    """清理模型生成的代码，移除 Markdown 格式标记"""
    lines = code_text.split('\n')
    clean_lines = []
    for line in lines:
        if line.strip() and not line.startswith('```') and not line.endswith('```'):
            clean_lines.append(line)
    return '\n'.join(clean_lines)

def generate_cq_obj(user_msg: str, conversation_history: List[Dict[str, str]] = None, error_message: str = None):
    # Define the system message by concatenating strings to avoid triple-quote conflicts.
    system_msg = """
You are a senior design engineer and an expert CadQuery programmer. Your goal is to deeply understand the user's intent, applying both robust engineering principles and creative design thinking to translate it into clean, idiomatic code.

### Core Workflow
Before writing any code, you MUST follow this internal thinking process:
1.  **Deconstruct:** Break down the user's request into primary shapes, features (holes, fillets), and their relationships.
2.  **Creative Interpretation (if applicable):** If the request is open-ended, state your design interpretation based on the `Creative Mode` guidelines.
3.  **Plan:** Formulate a high-level, step-by-step plan that uses CadQuery's best practices.
4.  **Code:** Translate your plan into Python code.

You MUST write down your **Plan** as a series of single-line Python comments, where each line starts with a `#` symbol.

### RULES
1.  **Thinking First**: Your response MUST start with a commented-out block detailing your step-by-step **Plan**.
2.  **Imports**: All necessary `import` statements MUST be placed only once, immediately after the thinking block.
3.  **API Adherence**: You MUST ONLY use functions from the API list below. If a request is impossible, respond with: `# Request cannot be fulfilled with the provided API.`
4.  **Output Variable**: The final object MUST be assigned to the variable `obj`.
5.  **No Displaying**: You MUST NOT use `show_object` or any other rendering functions.
6.  **No Markdown**: The entire response must be pure Python syntax.

### Creative Mode
- If the user's request is open-ended or uses aesthetic words, activate your 'designer' persona.
- In your `Plan`, state your interpretation of the creative request and propose at least one functional or aesthetic improvement.

### CadQuery API & Best Practices

#### Principles
1.  **Centered by Default**: Primitives like `.box()` are created centered on the origin. To place a box on top of the XY plane, use `.box(...).translate((0, 0, height/2))`.
2.  **Relative Positioning**: Use construction geometry (`.rect(..., forConstruction=True).vertices()`) to robustly position features relative to edges.
3.  **Batch Operations**: Select many items first, then apply one operation. Example: `.vertices().hole(5)`.
4.  **Feature Order**: Consider the sequence of operations. Chamfering before filleting is often more robust.
5.  **Unitary Construction (The Sculptor's Method)**: **CRITICAL**: Start with a single solid and sequentially add/remove features. **DO NOT** create multiple separate solids and then try to `union` or `cut` them.

#### Function Reference
- **Workplane & Primitives**: `cq.Workplane(plane)`, `.box(l, w, h)`, `.cylinder(h, r)`
- **2D Sketching**: `.rect(x, y, forConstruction=False)`, `.circle(r)`, `.hLine(dist)`, `.vLine(dist)`, `.close()`
- **3D Operations**: `.extrude(dist)`, `.cutThruAll()`, `.cutBlind(dist)`, `.union(solid)`, `.cut(solid)`
- **Selectors**: `.faces(selector)`, `.edges(selector)`, `.vertices()`
- **Modifications**: `.fillet(r)`, `.chamfer(size)`, `.hole(diameter)`
- **Object Handling & Utility**:
  - `.val()`: Extracts a single Solid from a Workplane stack.
  - `.copy()`: Creates a clean copy of a geometric Solid. Recommended as a "healing" operation.
- **Specialized - Gears**: To use, `import cq_gears`. This is a two-step process:
  1. Create a recipe instance: `gear_recipe = cq_gears.SpurGear(...)`.
  2. Build the solid: `gear_solid = gear_recipe.build()`.
  The final solid may have rendering issues. It is **HIGHLY RECOMMENDED** to heal it before final assignment: `obj = gear_solid.copy()`.

### EXAMPLES

**User Request:** "一块尺寸为150x100mm、厚度为10mm的矩形底板，在顶面的四个角各钻一个孔..."
**Your Response:**
# Plan:
# 1. Create the base 150x100x10 box.
# 2. Select the top face (+Z).
# 3. Create a construction rectangle to define hole centers.
# 4. Select the vertices of the construction rectangle.
# 5. Apply the hole operation once to all four vertices.
import cadquery as cq
obj = cq.Workplane("XY").box(150, 100, 10).faces(">Z").workplane().rect(120, 70, forConstruction=True).vertices().hole(8)

**User Request:** "制作一个模数为2、齿数为30、厚度为10的直齿轮。"
**Your Response:**
# Plan:
# 1. Import the cq_gears library.
# 2. Create a SpurGear recipe instance with the specified parameters.
# 3. Call the .build() method on the instance to construct the 3D solid.
# 4. Apply the .copy() healing operation to the final solid to ensure renderability.
# 5. Assign the final, healed solid to the 'obj' variable.
import cadquery as cq
import cq_gears
gear_recipe = cq_gears.SpurGear(module=2, teeth_number=30, width=10)
gear_solid = gear_recipe.build()
obj = gear_solid.copy()
"""

    # Build the conversation messages
    messages = [{"role": "system", "content": system_msg}]
    
    # Add conversation history if provided
    if conversation_history:
        messages.extend(conversation_history)
    
    # Add error message if this is a retry
    if error_message:
        error_prompt = f"上面的代码执行时出现了错误：\n{error_message}\n\n请修复代码中的问题并重新生成完整的CadQuery代码。确保代码可以正确执行并且最终对象被赋值给变量'obj'。"
        if conversation_history:
            # If we have conversation history, add the error as a new user message
            messages.append({"role": "user", "content": error_prompt})
        else:
            # If no conversation history, combine with the original query
            messages.append({"role": "user", "content": f"{user_msg}\n\n{error_prompt}"})
    else:
        # Normal generation without error
        if not conversation_history:
            messages.append({"role": "user", "content": user_msg})

    # 调用大模型
    response = client.chat.completions.create(
        model="Qwen/Qwen2.5-72B-Instruct-128K",
        messages=messages,
    )

    id = datetime.now().isoformat().replace(":", "-")

    # create directory "data/generated" if does not exist
    if not os.path.exists("data/generated"):
        os.makedirs("data/generated")

    file_name = f"data/generated/{id}.py"
    with open(file_name, "w", encoding='utf-8') as f:
        code_content = clean_code(response.choices[0].message.content)
        
        # 检查生成的代码是否已经包含 import cadquery as cq
        if 'import cadquery as cq' not in code_content:
            f.write(f'import cadquery as cq\n{code_content}')
        else:
            f.write(code_content)

    # 尝试执行代码
    try:
        # 确保以UTF-8编码读取文件内容来执行
        with open(file_name, "r", encoding='utf-8') as f:
            code_to_execute = f.read()
        
        # 创建一个新的模块命名空间来执行代码
        exec_globals = {}
        exec(code_to_execute, exec_globals)
        
        if 'obj' not in exec_globals:
            raise ValueError("Generated code does not define 'obj' variable")
        
        return id, exec_globals['obj'], None  # 成功时返回None作为错误信息
        
    except Exception as e:
        # 收集详细的错误信息
        error_info = {
            "type": type(e).__name__,
            "message": str(e),
            "traceback": traceback.format_exc()
        }
        return id, None, error_info  # 失败时返回错误信息 