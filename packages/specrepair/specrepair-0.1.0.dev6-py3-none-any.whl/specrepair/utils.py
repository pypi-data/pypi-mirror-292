import re
import inspect
import difflib
from typing import Dict, Annotated, get_origin, get_args

TYPE_MAPPING = {
    "str": "string",
    "int": "integer",
    "float": "number",
    "bool": "boolean",
    "list": "array",
    "dict": "object",
    # 添加其他类型的映射，如果需要的话
}


def gen_func_description(func) -> Dict:
    # 生成函数描述
    func_name = func.__name__
    func_desc = func.__doc__.strip() if func.__doc__ else ""

    # 获取函数参数的注解信息和默认值
    sig = inspect.signature(func)
    annotations = func.__annotations__

    parameters = {}
    required_params = []

    for name, param in sig.parameters.items():
        hint = annotations.get(name, None)
        origin = get_origin(hint)
        args = get_args(hint)

        if origin is Annotated:
            # 处理 Annotated 类型
            param_type = args[0].__name__.lower()
            param_desc = args[1]
        else:
            # 处理非 Annotated 类型
            param_type = (
                hint.__name__.lower() if hasattr(hint, "__name__") else str(hint)
            )
            param_desc = ""

        # 使用类型映射进行转换
        param_type = TYPE_MAPPING.get(param_type, "string")

        parameters[name] = {"description": param_desc, "type": param_type}

        # 检查参数默认值
        if param.default is param.empty:
            required_params.append(name)

    # 将生成的参数信息结构化
    param_schema = {
        "type": "object",
        "properties": parameters,
        "required": required_params,
    }

    # 返回最终的结构化函数描述
    return {
        "type": "function",
        "function": {
            "name": func_name,
            "description": func_desc,
            "parameters": param_schema,
        },
    }


def repair_spec(
    suggestion: Annotated[str, "spec脚本修改建议"],
    fault_segment: Annotated[
        str, "spec脚本中导致错误的代码片段，附带行号，按行号从小到大顺序"
    ] = "",
    repaired_segment: Annotated[str, "对应修复后的spec脚本代码片段，附带行号"] = "",
) -> str:
    """根据报错信息修复spec脚本"""

    return "spec 脚本修复"


def repair_spec_pro(
    fault_segment: Annotated[
        str, "spec脚本中导致错误的代码片段，附带行号，按行号从小到大顺序"
    ] = "",
    repaired_segment: Annotated[str, "对应修复后的spec脚本代码片段，附带行号"] = "",
) -> str:
    """根据报错信息修复spec脚本"""

    return "spec 脚本修复"


def repair_spec_impl(
    original_spec_file: str,
    fault_segment: str,
    repaired_segment: str,
    repaired_spec_file: str,
) -> bool:
    with open(original_spec_file, "r", encoding="utf-8", errors="ignore") as f:
        spec_lines = f.readlines()
    fault_lines = fault_segment.split("\n")
    fault_lines = [line + "\n" for line in fault_lines]
    repaired_lines = repaired_segment.split("\n")
    repaired_lines = [line + "\n" for line in repaired_lines]

    # 匹配模式：
    # 25: %build
    # 26: export LANG=C.UTF-8
    pattern = r"^\d+: .+$"

    # 错误片段提取
    delete_list = []
    start_index = -1
    current_index = -1
    for i in range(len(fault_lines)):
        line = fault_lines[i]
        if re.match(pattern, line):
            index = int(line.split(": ")[0])
            if start_index == -1:
                start_index = index
                current_index = index
            elif index - current_index == 1:
                current_index = index
            else:
                delete_list.append((start_index, current_index + 1))
                start_index = index
                current_index = index
        else:
            if start_index != -1:
                delete_list.append((start_index, current_index + 1))
                start_index = -1
                current_index = -1
    if start_index != -1:
        delete_list.append((start_index, current_index + 1))

    if len(delete_list) == 0:
        return False

    # 修复片段提取
    insert_list = []
    start_index = -1
    current_index = -1
    insert_line_list = []
    line_list = []
    for i in range(len(repaired_lines)):
        line = repaired_lines[i]
        if re.match(pattern, line):
            index, line = line.split(": ", 1)
            index = int(index)
            if start_index == -1:
                start_index = index
                current_index = index
                line_list = [line]
            elif index - current_index == 1:
                current_index = index
                line_list.append(line)
            else:
                insert_list.append((start_index, current_index + 1))
                start_index = index
                current_index = index
                insert_line_list.append(line_list)
                line_list = [line]
        else:
            if start_index != -1:
                insert_list.append((start_index, current_index + 1))
                start_index = -1
                current_index = -1
                insert_line_list.append(line_list)
                line_list = []

    if start_index != -1:
        insert_list.append((start_index, current_index + 1))
        insert_line_list.append(line_list)

    # 按行号有大到小排序
    delete_list_with_index = [(index, tup) for index, tup in enumerate(delete_list)]
    sorted_delete_list_with_index = sorted(
        delete_list_with_index, key=lambda x: x[1][0], reverse=True
    )

    if len(delete_list) != len(insert_list):
        return False

    # 按顺序替换
    for index, tup in sorted_delete_list_with_index:
        start_index, end_index = tup
        del spec_lines[start_index:end_index]
        start_index, end_index = insert_list[index]
        spec_lines[start_index:start_index] = insert_line_list[index]
    with open(repaired_spec_file, "w") as f:
        f.write("".join(spec_lines))
    return True


def get_patch(source, target):
    with open(source, "r") as fs:
        source_lines = fs.readlines()

    with open(target, "r") as ft:
        target_lines = ft.readlines()

    # 生成patch
    diff = difflib.unified_diff(
        source_lines, target_lines, fromfile=source, tofile=target
    )
    patch = "".join(diff)
    return patch


def save_log(log_file, is_repaired, error_info, suggestion, fault_segment, patch):
    repair_status = "Repaired" if is_repaired else "Not Repaired"
    with open(log_file, "w") as f:
        f.write("====================[Execution Log]====================\n\n")
        f.write(f"Repair Status: [{repair_status}]\n\n")

        f.write("--------------------[Error Message]--------------------\n\n")
        f.write(f"{error_info}\n\n")

        f.write("--------------------[AI Suggestion]--------------------\n\n")
        f.write(f"{suggestion}\n\n")

        f.write("--------------------[Fault Code]--------------------\n\n")
        f.write(f"{fault_segment}\n\n")

        f.write("--------------------[Patch Code]-----------------------\n\n")
        f.write(f"{patch}\n\n")

        f.write("========================================================\n\n")
