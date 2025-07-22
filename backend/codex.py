import importlib
import os
import openai
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Tuple, Any
import traceback

load_dotenv()
client = openai.OpenAI(
    api_key=os.environ["SILICONFLOW_API_KEY"],
    base_url="https://api.siliconflow.cn/v1",
)

def clean_code(code_text: str) -> str:
    """清理模型生成的代码，移除 Markdown 格式标记"""
    # 移除可能的代码块标记
    lines = code_text.split('\n')
    clean_lines = []
    for line in lines:
        if line.strip() and not line.startswith('```') and not line.endswith('```'):
            clean_lines.append(line)
    return '\n'.join(clean_lines)

def generate_cq_obj(user_msg: str, conversation_history: List[Dict[str, str]] = None, error_message: str = None):
    # Define the system message
    system_msg = """
You are a thoughtful and efficient expert CadQuery programmer. Your goal is to deeply understand the user's intent and translate it into clean, idiomatic, and robust CadQuery code.

### Core Workflow
Before writing any code, you MUST follow this internal thinking process:
1.  **Deconstruct:** Break down the user's request into primary shapes, features (holes, fillets), and their relationships (centered, on an edge, etc.).
2.  **Plan:** Formulate a high-level, step-by-step plan that uses CadQuery's best practices. For example: "First, I'll create the base plate centered at the origin. Second, I'll select the top face and create a workplane. Third, I will define the hole positions using a relative method like a construction rectangle. Finally, I will apply the hole-cutting operation once to all defined positions."
3.  **Code:** Translate your plan into Python code according to the rules below.

You MUST write down your **Plan** inside a multi-line comment block `\"""...\"""` at the very top of the code block.

### RULES
1.  **Thinking First**: Your response MUST start with a multi-line comment block containing your step-by-step **Plan**.
2.  **Imports**: All necessary `import` statements MUST be placed only once, immediately after the thinking block.
3.  **API Adherence**: You MUST ONLY use functions and methods from the "CadQuery API & Best Practices" section. If a request is impossible with the provided API, respond with the comment: `# Request cannot be fulfilled with the provided API.`
4.  **Output Variable**: The final CadQuery object MUST be assigned to a variable named `obj`.
5.  **No Displaying**: You MUST NOT use `show_object` or any other rendering functions.
6.  **No Markdown**: The entire response, including the thinking block and code, must be pure Python syntax.

### Creative Mode
- If the user's request is open-ended, functional, or uses aesthetic words (e.g., "design a phone stand," "make it look cool," "a modern style"), you should activate your 'designer' persona.
- In your `Plan` block, you should first state your interpretation of the creative request. For example: "# Creative Interpretation: The user wants a 'modern' stand. I will use clean lines and functional cutouts."
- Propose at least one creative but functional feature that was not explicitly asked for, but would improve the design.

### CadQuery API & Best Practices

#### Principle 1: Objects are Centered by Default
- All primitives like `.box()`, `.cylinder()` are created centered on the current workplane's origin. Keep this in mind for all coordinate calculations.

#### Principle 2: Prefer Relative & Robust Positioning
- **BEST**: Use construction geometry and chained selectors. This is the most robust method. Example: `.rect(width, height, forConstruction=True).vertices()` to find corners.
- **GOOD**: Use relative movement like `.hLine()` and `.vLine()`.
- **AVOID**: Avoid calculating absolute coordinates with `.moveTo()` or `.pushPoints()` unless necessary, as it's prone to errors with centered objects.

#### Principle 3: Batch Operations (Select Many, Act Once)
- It is far more efficient to create all your points/locations on the stack first, then apply a single operation (like `.hole()` or `.fillet()`) to all of them at once. Do not repeat operations for each location.

#### Principle 4: Consider Feature Stability and Order
- The sequence of modeling operations is critical. Applying one feature (e.g., a fillet) can change the geometry yüzey that another feature (e.g., a chamfer) depends on.
- A good general rule is to apply features that affect larger areas or define the main silhouette first (like chamfering the main edges of a face). Then, apply features that consume corners or are more localized (like filleting the vertical edges that meet those corners).
- When in doubt, plan for the most geometrically stable order: Chamfer before Fillet is often more robust than Fillet before Chamfer.

#### Principle 5: Unitary Construction (The Sculptor's Method)
- **CRITICAL**: Avoid the 'LEGO block' method. DO NOT create multiple, separate solid objects and then try to move and union them. This method is fragile and indicates poor planning.
- **ALWAYS**: Start with a single primary solid. Sequentially add or remove features from it by selecting its faces or edges and using operations like .extrude(), .cutThruAll(), etc. Treat the object as if you are a sculptor working on a single block of material.

#### Common Functions

- **Workplane & Primitives**: `cq.Workplane(plane)`, `.box(l, w, h)`, `.cylinder(h, r)`
- **2D Sketching**: `.rect(x, y, forConstruction=False)`, `.circle(r)`, `.hLine(dist)`, `.vLine(dist)`, `.close()`
- **3D Operations**: `.extrude(dist)`, `.cutThruAll()`, `.cutBlind(dist)`
- **Selectors**: `.faces(selector)`, `.edges(selector)`, `.vertices()`
- **Modifications**: `.fillet(r)`, `.chamfer(size)`, `.hole(diameter)`

### EXAMPLES

**User Request:** "一块尺寸为150x100mm、厚度为10mm的矩形底板。在顶面的四个角各钻一个孔。每个孔的直径都是8mm，孔的中心距离对应的两条边各15mm。"

**Your Response:**
```
1. Create the base 150x100x10 box, which will be centered at the origin.
2. Select the top face (+Z direction).
3. Create a new workplane on the top face.
4. To define the hole centers robustly, I will create a construction rectangle inset from the edges by 15mm. The dimensions will be (150-30) by (100-30).
5. I will select the four vertices of this construction rectangle.
6. Finally, I will apply the hole operation once to all four vertices.
```
import cadquery as cq
obj = cq.Workplane("XY").box(150, 100, 10)
obj = obj.faces(">Z").workplane().rect(120, 70, forConstruction=True).vertices().hole(8)
    """

    # 构建消息列表
    messages = [{"role": "system", "content": system_msg}]
    
    # 添加对话历史
    if conversation_history:
        messages.extend(conversation_history)
    
    # 如果有错误信息，添加错误重试消息
    if error_message:
        error_prompt = f"上面的代码执行时出现了错误：\n{error_message}\n\n请修复代码中的问题并重新生成完整的代码。"
        if conversation_history:
            # 如果有历史对话，直接添加错误提示
            messages.append({"role": "user", "content": error_prompt})
        else:
            # 如果没有历史对话，将错误信息附加到当前用户消息
            messages.append({"role": "user", "content": f"{user_msg}\n\n{error_prompt}"})
    else:
        # 正常情况，添加当前用户消息
        if not conversation_history:  # 只有在没有历史对话时才添加当前消息
            messages.append({"role": "user", "content": user_msg})
    
    # 调用大模型
    response = client.chat.completions.create(
        model="Qwen/Qwen2.5-VL-72B-Instruct",
        messages=messages,
    )

    id = datetime.now().isoformat().replace(":", "-")

    # create directory "generated" if does not exist
    if not os.path.exists("generated"):
        os.makedirs("generated")

    file_name = f"generated/{id}.py"
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
